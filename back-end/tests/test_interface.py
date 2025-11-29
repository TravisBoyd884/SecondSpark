"""
Unit tests for utils.ebay_interface and utils.etsy_interface.

These tests are *direct* tests of the marketplace interface classes,
independent of Flask and the database. HTTP calls to eBay/Etsy are
mocked out so no real network traffic occurs.

To run:

For unit tests only:
python -m unittest tests.test_marketplaces_unit

For integration tests:
python tests/integration_tests.py

To run all tests:
python -m unittest discover -s tests

These are segmented in order to test the ACTUAL functions if flask won't work.

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

# Ensure project root (back-end/) is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # .../back-end/tests
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)                   # .../back-end
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from unittest.mock import MagicMock

# Make sure your PYTHONPATH is set so that 'utils' is importable from backend root,
# e.g. run from 'back-end/' with:  python -m unittest tests.test_marketplaces_unit

from utils.ebay_interface import EbayInterface, EbayAPIError
from utils.etsy_interface import EtsyInterface, EtsyAPIError


class TestEbayInterface(unittest.TestCase):
    def setUp(self):
        # Minimal, fake credentials
        self.client_id = "FAKE_EBAY_CLIENT_ID"
        self.client_secret = "FAKE_EBAY_CLIENT_SECRET"
        self.env = "sandbox"

        # Create instance
        self.ebay = EbayInterface(
            client_id=self.client_id,
            client_secret=self.client_secret,
            env=self.env,
        )

        # Replace the real HTTP session with a mock
        self.ebay.session = MagicMock()

    # ------------------------------------------------------------------
    # _request behavior (HTTP core)
    # ------------------------------------------------------------------

    def test_request_success_returns_json(self):
        """_request should return parsed JSON when response is OK."""
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.text = '{"status":"ok","data":{"foo":"bar"}}'
        mock_resp.json.return_value = {"status": "ok", "data": {"foo": "bar"}}

        self.ebay.session.request.return_value = mock_resp

        result = self.ebay._request("GET", "/inventory_item/TEST-SKU-123")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["foo"], "bar")
        self.ebay.session.request.assert_called_once()

    def test_request_error_raises_ebay_error(self):
        """_request should raise EbayAPIError on non-OK response."""
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 400
        mock_resp.text = "Bad Request"

        self.ebay.session.request.return_value = mock_resp

        with self.assertRaises(EbayAPIError) as cm:
            self.ebay._request("GET", "/inventory_item/TEST-SKU-123")

        self.assertIn("400", str(cm.exception))
        self.ebay.session.request.assert_called_once()

    # ------------------------------------------------------------------
    # sync_item_create_or_update
    # ------------------------------------------------------------------

    def test_sync_item_create_or_update_calls_request(self):
        """
        sync_item_create_or_update should call _request (or the relevant
        internal API methods) with expected arguments.
        """
        # Instead of going deep into eBay Sell Inventory specifics,
        # we just assert that _request is invoked and result is returned.
        self.ebay._request = MagicMock(return_value={"result": "ok"})

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

        self.ebay._request.assert_called()  # At least once
        self.assertEqual(result.get("result"), "ok")

    # ------------------------------------------------------------------
    # sync_item_delete
    # ------------------------------------------------------------------

    def test_sync_item_delete_calls_request(self):
        """
        sync_item_delete should call the underlying DELETE endpoint via _request.
        """
        self.ebay._request = MagicMock(return_value={})

        item = {"sku": "TEST-SKU-UNIT-DEL"}
        self.ebay.sync_item_delete(item)

        self.ebay._request.assert_called()
        # No exception means success at this layer


class TestEtsyInterface(unittest.TestCase):
    def setUp(self):
        self.client_id = "FAKE_ETSY_CLIENT_ID"
        self.client_secret = "FAKE_ETSY_CLIENT_SECRET"
        self.env = "production"
        self.shop_id = "123456789"
        self.access_token = "FAKE_ETSY_ACCESS_TOKEN"

        self.etsy = EtsyInterface(
            client_id=self.client_id,
            client_secret=self.client_secret,
            env=self.env,
            shop_id=self.shop_id,
            access_token=self.access_token,
        )

        # Replace HTTP session with mock
        self.etsy.session = MagicMock()

    # ------------------------------------------------------------------
    # _auth_headers behavior
    # ------------------------------------------------------------------

    def test_auth_headers_include_bearer_and_api_key(self):
        """_auth_headers should include Authorization and x-api-key."""
        headers = self.etsy._auth_headers()

        self.assertEqual(headers["Authorization"], f"Bearer {self.access_token}")
        self.assertEqual(headers["x-api-key"], self.client_id)
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_auth_headers_without_token_raises_error(self):
        """_auth_headers should raise EtsyAPIError if no access_token is set."""
        self.etsy.access_token = None
        with self.assertRaises(EtsyAPIError):
            self.etsy._auth_headers()

    # ------------------------------------------------------------------
    # _request behavior (HTTP core)
    # ------------------------------------------------------------------

    def test_request_success_returns_json(self):
        """_request should return parsed JSON when response is OK."""
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.text = '{"status":"ok","listing_id":999}'
        mock_resp.json.return_value = {"status": "ok", "listing_id": 999}

        self.etsy.session.request.return_value = mock_resp

        result = self.etsy._request("GET", "/shops/123/listings")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["listing_id"], 999)
        self.etsy.session.request.assert_called_once()

    def test_request_error_raises_etsy_error(self):
        """_request should raise EtsyAPIError on non-OK response."""
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"

        self.etsy.session.request.return_value = mock_resp

        with self.assertRaises(EtsyAPIError) as cm:
            self.etsy._request("GET", "/shops/123/listings")

        self.assertIn("401", str(cm.exception))
        self.etsy.session.request.assert_called_once()

    # ------------------------------------------------------------------
    # sync_item_create_or_update
    # ------------------------------------------------------------------

    def test_sync_item_create_or_update_calls_request(self):
        """
        sync_item_create_or_update should route through create_or_update_listing
        and ultimately call _request.
        """
        self.etsy._request = MagicMock(return_value={"status": "ok", "listing_id": 555})

        item = {
            "item_id": 1,
            "sku": "ETSY-TEST-SKU",
            "title": "Etsy Test Item",
            "description": "Unit testing Etsy interface",
            "category": "Test",
            "quantity": 2,
            "price": "12.34",
        }

        result = self.etsy.sync_item_create_or_update(item)
        self.etsy._request.assert_called()
        self.assertEqual(result.get("listing_id"), 555)

    # ------------------------------------------------------------------
    # sync_item_delete
    # ------------------------------------------------------------------

    def test_sync_item_delete_without_listing_id_logs_warning_but_not_crash(self):
        """
        If sync_item_delete is called without an etsy_listing_id, implementation
        logs a warning but should NOT throw by default.
        """
        # We don't care about _request here because there is no listing_id.
        self.etsy._request = MagicMock()

        item = {"sku": "ETSY-TEST-SKU-NO-LISTING"}
        # Should not raise
        self.etsy.sync_item_delete(item)
        self.etsy._request.assert_not_called()

    def test_sync_item_delete_with_listing_id_calls_request(self):
        """If etsy_listing_id is present, _request should be called."""
        self.etsy._request = MagicMock(return_value={})

        item = {"etsy_listing_id": "999999999"}
        self.etsy.sync_item_delete(item)

        self.etsy._request.assert_called()


if __name__ == "__main__":
    unittest.main()