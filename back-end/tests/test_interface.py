"""
Unit tests for utils.ebay_interface and utils.etsy_interface.

These tests are *direct* tests of the marketplace interface classes,
independent of Flask and the database. HTTP calls to eBay/Etsy are
mocked out so no real network traffic occurs.

To run:

    python -m unittest tests.test_interface

Project structure (relevant):

back-end/
  utils/
    ebay_interface.py
    etsy_interface.py
  tests/
    test_interface.py  <-- this file
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root (back-end/) is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # .../back-end/tests
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)                   # .../back-end
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Make sure 'utils' marketplace modules are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from ebay_interface import EbayInterface, EbayAPIError
#from etsy_interface import EtsyInterface, EtsyAPIError


class TestEbayInterface(unittest.TestCase):
    def setUp(self):
        # Fake env vars so EbayInterface __init__ doesn't blow up
        os.environ["EBAY_CLIENT_ID"] = "FAKE_EBAY_CLIENT_ID"
        os.environ["EBAY_CLIENT_SECRET"] = "FAKE_EBAY_CLIENT_SECRET"
        os.environ["EBAY_ENV"] = "sandbox"
        # Don't override EBAY_SCOPE so we test the default scope logic

        # Create instance with default constructor (new interface)
        self.ebay = EbayInterface()

        # Replace the real HTTP session with a mock so no network calls ever happen
        self.ebay.session = MagicMock()

        # Avoid real token refresh; stub the app-token helper
        self.ebay._get_app_access_token = MagicMock(return_value="APP_TOKEN")

    # ------------------------------------------------------------------
    # Scope & OAuth wiring
    # ------------------------------------------------------------------

    def test_default_scope_contains_all_required_scopes_for_sandbox(self):
        """
        The default scope (when EBAY_SCOPE is not provided) should include
        all relevant sandbox sell scopes so the app token can be used for
        inventory + account/fulfillment/marketing if needed.
        """
        scope = self.ebay.scope
        self.assertIn("api.sandbox.ebay.com/oauth/api_scope", scope)
        self.assertIn("sell.inventory", scope)
        self.assertIn("sell.account", scope)
        self.assertIn("sell.fulfillment", scope)
        self.assertIn("sell.marketing", scope)

    def test_auth_headers_uses_app_token_for_inventory_calls(self):
        """
        _auth_headers(use_user_token=False) should use the app token and
        not require any user token to be set.
        """
        headers = self.ebay._auth_headers(use_user_token=False)
        self.ebay._get_app_access_token.assert_called_once()
        self.assertEqual(headers["Authorization"], "Bearer APP_TOKEN")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Accept"], "application/json")

    def test_auth_headers_uses_user_token_when_requested(self):
        """
        _auth_headers(use_user_token=True) should use the user access token
        if set, and should NOT call _get_app_access_token.
        """
        self.ebay.set_user_access_token("USER_TOKEN", expiry=None)
        # Reset mock call count to ensure we detect unwanted calls
        self.ebay._get_app_access_token.reset_mock()

        headers = self.ebay._auth_headers(use_user_token=True)
        self.ebay._get_app_access_token.assert_not_called()
        self.assertEqual(headers["Authorization"], "Bearer USER_TOKEN")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Accept"], "application/json")

    def test_auth_headers_without_user_token_raises_error_for_user_mode(self):
        """
        If use_user_token=True but no user token is configured, an error should be raised.
        """
        # Ensure no user token is set
        self.ebay._user_access_token = None

        with self.assertRaises(EbayAPIError):
            self.ebay._auth_headers(use_user_token=True)

    def test_refresh_app_access_token_sends_scope_to_oauth_endpoint(self):
        """
        _refresh_app_access_token should send the scope string in the POST
        to the OAuth endpoint.
        """
        # Prepare a fake OAuth response
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"access_token": "NEW_APP_TOKEN", "expires_in": 3600}
        self.ebay.session.post.return_value = mock_resp

        # Call the private method directly
        self.ebay._refresh_app_access_token()

        self.ebay.session.post.assert_called_once()
        _, kwargs = self.ebay.session.post.call_args
        data = kwargs.get("data", {})
        self.assertIn("scope", data)
        # Ensure the same scope string is used
        self.assertEqual(data["scope"], self.ebay.scope)

    # ------------------------------------------------------------------
    # Inventory vs Offer/Listings – token usage
    # ------------------------------------------------------------------

    def test_inventory_methods_use_app_token(self):
        """
        upsert_inventory_item/get_inventory_item/delete_inventory_item should
        rely on the app token (client_credentials).
        """
        # Mock _request to avoid real HTTP calls
        self.ebay._request = MagicMock(return_value={"ok": True})

        sku = "INV-SKU-123"
        payload = {"product": {"title": "Test Item"}}

        self.ebay.upsert_inventory_item(sku, payload)
        self.ebay.get_inventory_item(sku)
        self.ebay.delete_inventory_item(sku)

        # For all these calls, _auth_headers should have been invoked
        # with use_user_token=False
        # -> easiest is to patch _auth_headers temporarily
        # but we already stubbed _get_app_access_token, so we just assert
        # that it was used at least once.
        self.assertGreaterEqual(self.ebay._get_app_access_token.call_count, 1)

    def test_offer_methods_require_user_token(self):
        """
        create_offer, publish_offer, and end_listing should use the USER token,
        not the app token, and should fail if no user token is set.
        """
        # Ensure no user token
        self.ebay._user_access_token = None

        # All of these should raise if use_user_token=True and no user token
        with self.assertRaises(EbayAPIError):
            self.ebay.create_offer(
                sku="OFFER-SKU-1",
                price="10.00",
                quantity=1,
                listing_description="test",
            )

        with self.assertRaises(EbayAPIError):
            self.ebay.publish_offer("OFFER-ID-1")

        with self.assertRaises(EbayAPIError):
            self.ebay.end_listing("OFFER-ID-1")

        # Now set a user token and verify that _request is called.
        self.ebay.set_user_access_token("USER_TOKEN", expiry=None)
        self.ebay._request = MagicMock(return_value={"status": "OK"})

        self.ebay.create_offer(
            sku="OFFER-SKU-1",
            price="10.00",
            quantity=1,
            listing_description="test",
        )
        self.ebay.publish_offer("OFFER-ID-1")
        self.ebay.end_listing("OFFER-ID-1")

        # Three calls: create_offer, publish_offer, end_listing (as PATCH)
        self.assertEqual(self.ebay._request.call_count, 3)

    # ------------------------------------------------------------------
    # sync_item_create_or_update
    # ------------------------------------------------------------------

    def test_sync_item_create_or_update_inventory_only_when_no_user_token(self):
        """
        When no user token is set, sync_item_create_or_update should:
          - call upsert_inventory_item (app-token)
          - NOT call create_offer / publish_offer
          - return inventory result with offer/publish set to None
        """
        # Patch underlying methods
        self.ebay.upsert_inventory_item = MagicMock(return_value={"inv": "ok"})
        self.ebay.create_offer = MagicMock()
        self.ebay.publish_offer = MagicMock()

        item = {
            "item_id": 1,
            "sku": "TEST-SKU-UNIT",
            "title": "Test Item",
            "description": "Unit testing eBay interface",
            "category": "Test",
            "quantity": 3,
            "price": "9.99",
        }

        result = self.ebay.sync_item_create_or_update(item)

        self.ebay.upsert_inventory_item.assert_called_once()
        self.ebay.create_offer.assert_not_called()
        self.ebay.publish_offer.assert_not_called()

        self.assertEqual(result["inventory"], {"inv": "ok"})
        self.assertIsNone(result["offer"])
        self.assertIsNone(result["publish"])

    def test_sync_item_create_or_update_with_user_token_calls_offer_and_publish(self):
        """
        When a user token is set, sync_item_create_or_update should:
          - call upsert_inventory_item
          - call create_offer
          - call publish_offer
          - return all three results
        """
        self.ebay.set_user_access_token("USER_TOKEN", expiry=None)

        self.ebay.upsert_inventory_item = MagicMock(return_value={"inv": "ok"})
        self.ebay.create_offer = MagicMock(return_value={"offerId": "OFFER-123"})
        self.ebay.publish_offer = MagicMock(return_value={"status": "PUBLISHED"})

        item = {
            "item_id": 1,
            "sku": "TEST-SKU-UNIT",
            "title": "Test Item",
            "description": "Unit testing eBay interface",
            "category": "Test",
            "quantity": 3,
            "price": "9.99",
        }

        result = self.ebay.sync_item_create_or_update(item)

        self.ebay.upsert_inventory_item.assert_called_once()
        self.ebay.create_offer.assert_called_once()
        self.ebay.publish_offer.assert_called_once()

        self.assertEqual(result["inventory"], {"inv": "ok"})
        self.assertEqual(result["offer"], {"offerId": "OFFER-123"})
        self.assertEqual(result["publish"], {"status": "PUBLISHED"})

    # ------------------------------------------------------------------
    # sync_item_delete
    # ------------------------------------------------------------------

    def test_sync_item_delete_calls_delete_inventory_only_when_no_user_token(self):
        """
        If no user token is set and ebay_offer_id is present, sync_item_delete
        should still attempt to delete the inventory item but cannot end the listing.
        """
        self.ebay.delete_inventory_item = MagicMock()
        self.ebay.end_listing = MagicMock()

        item = {
            "sku": "TEST-SKU-UNIT-DEL",
            "ebay_offer_id": "OFFER-999",
        }

        # No user token set -> end_listing should NOT be called
        self.ebay.sync_item_delete(item)

        self.ebay.delete_inventory_item.assert_called_once_with("TEST-SKU-UNIT-DEL")
        self.ebay.end_listing.assert_not_called()

    def test_sync_item_delete_calls_end_listing_and_delete_inventory_with_user_token(self):
        """
        If user token is set and ebay_offer_id is present, sync_item_delete
        should call end_listing and delete_inventory_item.
        """
        self.ebay.set_user_access_token("USER_TOKEN", expiry=None)

        self.ebay.delete_inventory_item = MagicMock()
        self.ebay.end_listing = MagicMock()

        item = {
            "sku": "TEST-SKU-UNIT-DEL",
            "ebay_offer_id": "OFFER-999",
        }

        self.ebay.sync_item_delete(item)

        self.ebay.end_listing.assert_called_once_with("OFFER-999")
        self.ebay.delete_inventory_item.assert_called_once_with("TEST-SKU-UNIT-DEL")


# class TestEtsyInterface(unittest.TestCase):
#     def setUp(self):
#         self.client_id = "FAKE_ETSY_CLIENT_ID"
#         self.client_secret = "FAKE_ETSY_CLIENT_SECRET"
#         self.env = "production"
#         self.shop_id = "123456789"
#         self.access_token = "FAKE_ETSY_ACCESS_TOKEN"
#
#         self.etsy = EtsyInterface(
#             client_id=self.client_id,
#             client_secret=self.client_secret,
#             env=self.env,
#             shop_id=self.shop_id,
#             access_token=self.access_token,
#         )
#
#         # Replace HTTP session with mock
#         self.etsy.session = MagicMock()
#
#     # ------------------------------------------------------------------
#     # _auth_headers behavior
#     # ------------------------------------------------------------------
#
#     def test_auth_headers_include_bearer_and_api_key(self):
#         """_auth_headers should include Authorization and x-api-key."""
#         headers = self.etsy._auth_headers()
#
#         self.assertEqual(headers["Authorization"], f"Bearer {self.access_token}")
#         self.assertEqual(headers["x-api-key"], self.client_id)
#         self.assertEqual(headers["Content-Type"], "application/json")
#
#     def test_auth_headers_without_token_raises_error(self):
#         """_auth_headers should raise EtsyAPIError if no access_token is set."""
#         self.etsy.access_token = None
#         with self.assertRaises(EtsyAPIError):
#             self.etsy._auth_headers()
#
#     # ------------------------------------------------------------------
#     # _request behavior (HTTP core)
#     # ------------------------------------------------------------------
#
#     def test_request_success_returns_json(self):
#         """_request should return parsed JSON when response is OK."""
#         mock_resp = MagicMock()
#         mock_resp.ok = True
#         mock_resp.text = '{"status":"ok","listing_id":999}'
#         mock_resp.json.return_value = {"status": "ok", "listing_id": 999}
#
#         self.etsy.session.request.return_value = mock_resp
#
#         result = self.etsy._request("GET", "/shops/123/listings")
#         self.assertEqual(result["status"], "ok")
#         self.assertEqual(result["listing_id"], 999)
#         self.etsy.session.request.assert_called_once()
#
#     def test_request_error_raises_etsy_error(self):
#         """_request should raise EtsyAPIError on non-OK response."""
#         mock_resp = MagicMock()
#         mock_resp.ok = False
#         mock_resp.status_code = 401
#         mock_resp.text = "Unauthorized"
#
#         self.etsy.session.request.return_value = mock_resp
#
#         with self.assertRaises(EtsyAPIError) as cm:
#             self.etsy._request("GET", "/shops/123/listings")
#
#         self.assertIn("401", str(cm.exception))
#         self.etsy.session.request.assert_called_once()
#
#     # ------------------------------------------------------------------
#     # sync_item_create_or_update
#     # ------------------------------------------------------------------
#
#     def test_sync_item_create_or_update_calls_request(self):
#         """
#         sync_item_create_or_update should route through create_or_update_listing
#         and ultimately call _request.
#         """
#         self.etsy._request = MagicMock(return_value={"status": "ok", "listing_id": 555})
#
#         item = {
#             "item_id": 1,
#             "sku": "ETSY-TEST-SKU",
#             "title": "Etsy Test Item",
#             "description": "Unit testing Etsy interface",
#             "category": "Test",
#             "quantity": 2,
#             "price": "12.34",
#         }
#
#         result = self.etsy.sync_item_create_or_update(item)
#         self.etsy._request.assert_called()
#         self.assertEqual(result.get("listing_id"), 555)
#
#     # ------------------------------------------------------------------
#     # sync_item_delete
#     # ------------------------------------------------------------------
#
#     def test_sync_item_delete_without_listing_id_logs_warning_but_not_crash(self):
#         """
#         If sync_item_delete is called without an etsy_listing_id, implementation
#         logs a warning but should NOT throw by default.
#         """
#         # We don't care about _request here because there is no listing_id.
#         self.etsy._request = MagicMock()
#
#         item = {"sku": "ETSY-TEST-SKU-NO-LISTING"}
#         # Should not raise
#         self.etsy.sync_item_delete(item)
#         self.etsy._request.assert_not_called()
#
#     def test_sync_item_delete_with_listing_id_calls_request(self):
#         """If etsy_listing_id is present, _request should be called."""
#         self.etsy._request = MagicMock(return_value={})
#
#         item = {"etsy_listing_id": "999999999"}
#         self.etsy.sync_item_delete(item)
#
#         self.etsy._request.assert_called()


if __name__ == "__main__":
    unittest.main()
