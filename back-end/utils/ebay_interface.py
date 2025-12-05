import os
import time
import base64
import logging
from dotenv import load_dotenv
from typing import Any, Dict, Optional, List

import requests


class EbayAPIError(Exception):
    """Generic exception for eBay API errors."""
    pass


class EbayInterface:
    """
    Thin wrapper around the eBay Sell APIs (Inventory + Offer) for item sync.

    Modes:
      - Application mode (client_credentials grant)
        Used for: inventory operations (upsert/get/delete inventory_item)

      - User mode (authorization_code grant; access token for a seller)
        Used for: offer + listing operations (create_offer, publish_offer, end_listing)

    Typical flow for a new listing:
      1) upsert_inventory_item(sku, inventory_payload)   [APP TOKEN]
      2) create_offer(...) -> offer_id                   [USER TOKEN]
      3) publish_offer(offer_id)                         [USER TOKEN]
    """

    def __init__(
        self,
        marketplace_id: str = "EBAY_US",
        user_access_token: Optional[str] = None,
        user_token_expiry: Optional[float] = None,
    ):
        """
        :param marketplace_id: eBay marketplace ID (e.g., 'EBAY_US')
        :param user_access_token: Optional seller user OAuth access token
                                  (authorization code flow).
        :param user_token_expiry: Optional epoch timestamp when the user token expires.
                                  (You will typically manage this outside and refresh as needed.)
        """

        # Load environment variables from '.env' file under utils
        if os.path.exists("utils/.env"):
            load_dotenv(dotenv_path="utils/.env")

        # Basic client credentials
        if (
            "EBAY_CLIENT_ID" in os.environ
            and "EBAY_CLIENT_SECRET" in os.environ
            and "EBAY_ENV" in os.environ
        ):
            self.client_id = os.getenv("EBAY_CLIENT_ID")
            self.client_secret = os.getenv("EBAY_CLIENT_SECRET")
            # Get environment type for the eBay API (sandbox or production)
            self.env = os.getenv("EBAY_ENV", "sandbox").lower()
            self.marketplace_id = marketplace_id
        else:
            raise EbayAPIError(
                "[NOTICE] eBay credentials not provided. "
                "Expected EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, EBAY_ENV in environment."
            )

        # ------------------------------------------------------------------
        # OAuth: app-level token (client_credentials)
        # ------------------------------------------------------------------
        self._app_access_token: Optional[str] = None
        self._app_token_expiry: float = 0.0

        # ------------------------------------------------------------------
        # OAuth: user-level token (authorization_code grant)
        #   You must obtain this elsewhere (browser login for seller), then
        #   inject it here or via set_user_access_token().
        # ------------------------------------------------------------------
        self._user_access_token: Optional[str] = user_access_token
        self._user_token_expiry: Optional[float] = user_token_expiry  # optional

        # Base URLs
        if self.env == "production":
            self.oauth_url = "https://api.ebay.com/identity/v1/oauth2/token"
            self.sell_inventory_base = "https://api.ebay.com/sell/inventory/v1"
        else:
            # sandbox
            self.oauth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
            self.sell_inventory_base = "https://api.sandbox.ebay.com/sell/inventory/v1"

        # ---------------------------------------------------------
        # OAuth Scopes — allow multiple scopes and environment matching
        # ---------------------------------------------------------
        if self.env == "production":
            default_scopes: List[str] = [
                "https://api.ebay.com/oauth/api_scope",
                "https://api.ebay.com/oauth/api_scope/sell.inventory",
                "https://api.ebay.com/oauth/api_scope/sell.account",
                "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
                "https://api.ebay.com/oauth/api_scope/sell.marketing",
            ]
        else:
            # Sandbox equivalent scopes
            default_scopes = [
                "https://api.sandbox.ebay.com/oauth/api_scope",
                "https://api.sandbox.ebay.com/oauth/api_scope/sell.inventory",
                "https://api.sandbox.ebay.com/oauth/api_scope/sell.account",
                "https://api.sandbox.ebay.com/oauth/api_scope/sell.fulfillment",
                "https://api.sandbox.ebay.com/oauth/api_scope/sell.marketing",
            ]

        env_scope = os.getenv("EBAY_SCOPE")
        if env_scope:
            # Allow comma or space-separated scope override from env
            self.scope = " ".join(
                s.strip() for s in env_scope.replace(",", " ").split()
            )
        else:
            self.scope = " ".join(default_scopes)

        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    # ---------------------------------------------------------------------
    # Public helpers to manage user tokens
    # ---------------------------------------------------------------------

    def set_user_access_token(self, token: str, expiry: Optional[float] = None) -> None:
        """
        Set (or update) the OAuth access token for a seller user.

        This token must be obtained via the ebay OAuth authorization code flow
        (browser login as sandbox/production seller).

        :param token: the user OAuth access_token
        :param expiry: optional epoch timestamp for when the token expires.
        """
        self._user_access_token = token
        self._user_token_expiry = expiry

    def has_user_token(self) -> bool:
        """
        Returns True if a user access_token is present.
        (No automatic refresh: you handle refreshing user tokens externally.)
        """
        return bool(self._user_access_token)

    # ---------------------------------------------------------------------
    # OAuth helpers (app-level / client_credentials)
    # ---------------------------------------------------------------------

    def _get_basic_auth_header(self) -> str:
        creds = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        return base64.b64encode(creds).decode("utf-8")

    def _refresh_app_access_token(self) -> None:
        """
        Get a new OAuth access token via client credentials grant.
        Used for application-level calls (inventory endpoints).
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self._get_basic_auth_header()}",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": self.scope,
        }

        resp = self.session.post(self.oauth_url, headers=headers, data=data, timeout=30)
        if not resp.ok:
            raise EbayAPIError(
                f"Failed to get app access token: {resp.status_code} {resp.text}"
            )

        payload = resp.json()
        self._app_access_token = payload["access_token"]
        # 'expires_in' is in seconds
        self._app_token_expiry = time.time() + payload.get("expires_in", 7200) - 60

    def _get_app_access_token(self) -> str:
        if not self._app_access_token or time.time() >= self._app_token_expiry:
            self._refresh_app_access_token()
        return self._app_access_token

    # ---------------------------------------------------------------------
    # Generic header / request helpers
    # ---------------------------------------------------------------------

    def _auth_headers(
        self,
        use_user_token: bool = False,
        extra: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Build Authorization headers.

        :param use_user_token:
            - False: use app-level client_credentials token
            - True:  use caller-provided user access token (authorization_code grant)
        """
        if use_user_token:
            if not self._user_access_token:
                raise EbayAPIError(
                    "User access token not set. "
                    "You must provide a seller OAuth token via set_user_access_token() "
                    "before calling offer/listing endpoints."
                )
            token = self._user_access_token
        else:
            token = self._get_app_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Generic HTTP wrapper that raises EbayAPIError on failure.
        """
        resp = self.session.request(method, url, timeout=30, **kwargs)
        if not resp.ok:
            raise EbayAPIError(
                f"eBay API error {resp.status_code}: {resp.text}"
            )
        if resp.text:
            try:
                return resp.json()
            except ValueError:
                # eBay occasionally returns empty or non-JSON body
                return {}
        return {}

    # ---------------------------------------------------------------------
    # Inventory item operations  (Sell Inventory API)
    #   These can be performed with the APP token (client_credentials).
    # ---------------------------------------------------------------------

    def upsert_inventory_item(self, sku: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update an inventory item for the given SKU.
        Endpoint: PUT /inventory_item/{sku}
        Uses: APP TOKEN (client_credentials)
        """
        url = f"{self.sell_inventory_base}/inventory_item/{sku}"
        headers = self._auth_headers(use_user_token=False)
        return self._request("PUT", url, headers=headers, json=payload)

    def get_inventory_item(self, sku: str) -> Dict[str, Any]:
        """
        Retrieve inventory item details for a SKU.
        Endpoint: GET /inventory_item/{sku}
        Uses: APP TOKEN (client_credentials)
        """
        url = f"{self.sell_inventory_base}/inventory_item/{sku}"
        headers = self._auth_headers(use_user_token=False)
        return self._request("GET", url, headers=headers)

    def delete_inventory_item(self, sku: str) -> None:
        """
        Delete an inventory item for a SKU.
        Endpoint: DELETE /inventory_item/{sku}
        Uses: APP TOKEN (client_credentials)
        """
        url = f"{self.sell_inventory_base}/inventory_item/{sku}"
        headers = self._auth_headers(use_user_token=False)
        self._request("DELETE", url, headers=headers)

    # ---------------------------------------------------------------------
    # Offer & listing operations
    #   These require USER token (authorization_code grant), i.e., a seller.
    # ---------------------------------------------------------------------

    def create_offer(
        self,
        sku: str,
        price: str,
        quantity: int,
        listing_description: str,
        category_id: Optional[str] = None,
        listing_policies: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an offer for a previously upserted inventory item.
        Endpoint: POST /offer
        Uses: USER TOKEN (seller's OAuth access token)
        """
        url = f"{self.sell_inventory_base}/offer"
        headers = self._auth_headers(use_user_token=True)

        payload: Dict[str, Any] = {
            "sku": sku,
            "marketplaceId": self.marketplace_id,
            "pricingSummary": {
                "price": {
                    "value": price,
                    "currency": "USD",
                }
            },
            "availableQuantity": quantity,
            "format": "FIXED_PRICE",
            "listingDescription": listing_description,
        }

        if category_id:
            payload["categoryId"] = category_id
        if listing_policies:
            payload.update(listing_policies)

        return self._request("POST", url, headers=headers, json=payload)

    def update_offer(self, offer_id: str, partial_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing offer (PATCH).
        Endpoint: PATCH /offer/{offerId}
        Uses: USER TOKEN
        """
        url = f"{self.sell_inventory_base}/offer/{offer_id}"
        headers = self._auth_headers(
            use_user_token=True,
            extra={"Content-Type": "application/json"},
        )
        return self._request("PATCH", url, headers=headers, json=partial_payload)

    def publish_offer(self, offer_id: str) -> Dict[str, Any]:
        """
        Publish an offer (goes live on eBay).
        Endpoint: POST /offer/{offerId}/publish
        Uses: USER TOKEN
        """
        url = f"{self.sell_inventory_base}/offer/{offer_id}/publish"
        headers = self._auth_headers(use_user_token=True)
        return self._request("POST", url, headers=headers)

    def end_listing(self, offer_id: str, reason: str = "OUT_OF_STOCK") -> Dict[str, Any]:
        """
        End an active listing by setting availableQuantity to 0.
        Endpoint: PATCH /offer/{offerId}
        Uses: USER TOKEN
        """
        payload = {
            "availableQuantity": 0,
            "listingPolicies": {
                # placeholder for any required policy adjustments
            },
        }
        self.logger.info(f"Ending listing for offer {offer_id} with reason={reason}")
        return self.update_offer(offer_id, payload)

    # ---------------------------------------------------------------------
    # High-level helpers: map local Item → eBay
    # ---------------------------------------------------------------------

    def sync_item_create_or_update(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        High-level helper to push a local item (from your DB) to eBay.

        Expected keys in `item`:
            - sku
            - title
            - description (optional)
            - quantity (optional)
            - category (optional)

        Flow:
            1) Upsert inventory item (APP TOKEN)
            2) Create offer (USER TOKEN)
            3) Publish offer (USER TOKEN)
        """
        sku = item["sku"]
        title = item["title"]
        description = item.get("description") or title
        quantity = item.get("quantity", 0)
        category = item.get("category")

        # 1) Upsert inventory item (app-level token)
        inventory_payload = {
            "product": {
                "title": title,
                "description": description,
                # Add UPC/brand/MNP details if you have them
            }
        }
        inv_result = self.upsert_inventory_item(sku, inventory_payload)

        # For offer + publish, we require a user token
        if not self.has_user_token():
            # You still get inventory sync even if no user token is present
            self.logger.warning(
                "User token not set; inventory updated but offer/listing not created."
            )
            return {
                "inventory": inv_result,
                "offer": None,
                "publish": None,
            }

        price = str(item.get("price", "0.00"))
        offer = self.create_offer(
            sku=sku,
            price=price,
            quantity=quantity,
            listing_description=description,
            category_id=None,  # TODO: map your category to eBay category id, if desired
        )

        offer_id = offer.get("offerId")
        if not offer_id:
            raise EbayAPIError(
                f"Offer creation did not return an offerId. Response: {offer}"
            )

        publish_result = self.publish_offer(offer_id)

        return {
            "inventory": inv_result,
            "offer": offer,
            "publish": publish_result,
        }

    def sync_item_delete(self, item: Dict[str, Any]) -> None:
        """
        End the eBay listing and/or delete the inventory item when the local item is deleted.

        Expected in `item`:
            - sku
            - ebay_offer_id (optional; if present we attempt to end listing)
        """
        sku = item["sku"]
        offer_id = item.get("ebay_offer_id")

        # 1) End listing if we know the offer and have user token
        if offer_id and self.has_user_token():
            try:
                self.end_listing(offer_id)
            except EbayAPIError as e:
                self.logger.warning(f"Failed to end offer {offer_id}: {e}")
        elif offer_id and not self.has_user_token():
            self.logger.warning(
                "Cannot end listing on eBay because no user token is configured."
            )

        # 2) Delete inventory item (app-level)
        try:
            self.delete_inventory_item(sku)
        except EbayAPIError as e:
            self.logger.warning(f"Failed to delete inventory item {sku}: {e}")
