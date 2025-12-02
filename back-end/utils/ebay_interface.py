# ebay_interface.py

import os
import time
import base64
import logging
from dotenv import load_dotenv
from typing import Any, Dict, Optional

import requests


class EbayAPIError(Exception):
    """Generic exception for eBay API errors."""
    pass


class EbayInterface:
    """
    Thin wrapper around the eBay Sell APIs (Inventory + Offer) for item sync.

    Typical flow for a new listing:
      1) upsert_inventory_item(sku, inventory_payload)
      2) create_offer(sku, offer_payload) -> offer_id
      3) publish_offer(offer_id)
    """

    def __init__(self, marketplace_id: str = "EBAY_US"):
        # load environment variables from '.env' file
        if (os.path.exists("utils/.env")):
            load_dotenv(dotenv_path="utils/.env")
            if 'EBAY_CLIENT_ID' in os.environ and 'EBAY_CLIENT_SECRET' in os.environ and 'EBAY_ENV' in os.environ:
                self.client_id = os.getenv("EBAY_CLIENT_ID")
                self.client_secret = os.getenv("EBAY_CLIENT_SECRET")
                # Get environment type for the Ebay api (sandbox or production)
                self.env = os.getenv("EBAY_ENV").lower()
                self.marketplace_id = marketplace_id
            else:
                raise Exception("[NOTICE] eBay credentials not provided.")
        else:
            raise EbayAPIError("Unable to locate/read .env file.")

        # OAuth token cache
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0.0

        # Base URLs
        if self.env == "production":
            self.oauth_url = "https://api.ebay.com/identity/v1/oauth2/token"
            self.sell_inventory_base = "https://api.ebay.com/sell/inventory/v1"
        else:
            # sandbox
            self.oauth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
            self.sell_inventory_base = "https://api.sandbox.ebay.com/sell/inventory/v1"

        # Default Sell API scope – adjust as needed
        self.scope = os.getenv(
            "EBAY_SCOPE",
            "https://api.ebay.com/oauth/api_scope/sell.inventory"
        )

        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    # ---------------------------------------------------------------------
    # OAuth helpers
    # ---------------------------------------------------------------------

    def _get_basic_auth_header(self) -> str:
        creds = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        return base64.b64encode(creds).decode("utf-8")

    def _refresh_access_token(self) -> None:
        """
        Get a new OAuth access token via client credentials grant.
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
                f"Failed to get access token: {resp.status_code} {resp.text}"
            )

        payload = resp.json()
        self._access_token = payload["access_token"]
        # 'expires_in' is in seconds
        self._token_expiry = time.time() + payload.get("expires_in", 7200) - 60

    def _get_access_token(self) -> str:
        if not self._access_token or time.time() >= self._token_expiry:
            self._refresh_access_token()
        return self._access_token

    def _auth_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
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
            return resp.json()
        return {}

    # ---------------------------------------------------------------------
    # Inventory item operations  (Sell Inventory API)
    # ---------------------------------------------------------------------

    def upsert_inventory_item(self, sku: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update an inventory item for the given SKU.
        Endpoint: PUT /inventory_item/{sku}
        """
        url = f"{self.sell_inventory_base}/inventory_item/{sku}"
        headers = self._auth_headers()
        return self._request("PUT", url, headers=headers, json=payload)

    def get_inventory_item(self, sku: str) -> Dict[str, Any]:
        """
        Retrieve inventory item details for a SKU.
        Endpoint: GET /inventory_item/{sku}
        """
        url = f"{self.sell_inventory_base}/inventory_item/{sku}"
        headers = self._auth_headers()
        return self._request("GET", url, headers=headers)

    def delete_inventory_item(self, sku: str) -> None:
        """
        Delete an inventory item for a SKU.
        Endpoint: DELETE /inventory_item/{sku}
        """
        url = f"{self.sell_inventory_base}/inventory_item/{sku}"
        headers = self._auth_headers()
        self._request("DELETE", url, headers=headers)

    # ---------------------------------------------------------------------
    # Offer & listing operations
    # ---------------------------------------------------------------------

    def create_offer(self, sku: str, price: str, quantity: int, listing_description: str,
                     category_id: Optional[str] = None,
                     listing_policies: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an offer for a previously upserted inventory item.
        Endpoint: POST /offer
        """
        url = f"{self.sell_inventory_base}/offer"
        headers = self._auth_headers()

        # Minimal payload – you can add shipping/return/payment policies, etc.
        payload: Dict[str, Any] = {
            "sku": sku,
            "marketplaceId": self.marketplace_id,
            "pricingSummary": {
                "price": {
                    "value": price,
                    "currency": "USD"
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
        """
        url = f"{self.sell_inventory_base}/offer/{offer_id}"
        headers = self._auth_headers({"Content-Type": "application/json"})
        return self._request("PATCH", url, headers=headers, json=partial_payload)

    def publish_offer(self, offer_id: str) -> Dict[str, Any]:
        """
        Publish an offer (goes live on eBay).
        Endpoint: POST /offer/{offerId}/publish
        """
        url = f"{self.sell_inventory_base}/offer/{offer_id}/publish"
        headers = self._auth_headers()
        return self._request("POST", url, headers=headers)

    def end_listing(self, offer_id: str, reason: str = "OUT_OF_STOCK") -> Dict[str, Any]:
        """
        End an active listing.
        This can be done by updating availableQuantity to 0 or using a dedicated endpoint,
        depending on your strategy.
        Here we PATCH the offer to set availableQuantity to 0.
        """
        payload = {
            "availableQuantity": 0,
            "listingPolicies": {
                # placeholder for any required policy adjustments
            }
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
            - description
            - quantity
            - category (optional mapping to eBay category_id)
        """
        sku = item["sku"]
        title = item["title"]
        description = item.get("description") or title
        quantity = item.get("quantity", 0)
        category = item.get("category")

        # 1) Upsert inventory item
        inventory_payload = {
            "product": {
                "title": title,
                "description": description,
                # Add UPC/brand/MNP details if you have them
            }
        }
        inv_result = self.upsert_inventory_item(sku, inventory_payload)

        # 2) Create offer (or update if one already exists)
        price = item.get("price", "0.00")  # you'll probably want price stored in DB
        offer = self.create_offer(
            sku=sku,
            price=str(price),
            quantity=quantity,
            listing_description=description,
            category_id=None  # TODO: map your category to eBay category id
        )

        # 3) Publish offer
        offer_id = offer.get("offerId")
        publish_result = self.publish_offer(offer_id)

        return {
            "inventory": inv_result,
            "offer": offer,
            "publish": publish_result,
        }

    def sync_item_delete(self, item: Dict[str, Any]) -> None:
        """
        End the eBay listing and/or delete the inventory item when the local item is deleted.
        """
        sku = item["sku"]
        offer_id = item.get("ebay_offer_id")

        # 1) End listing if we know the offer
        if offer_id:
            try:
                self.end_listing(offer_id)
            except EbayAPIError as e:
                self.logger.warning(f"Failed to end offer {offer_id}: {e}")

        # 2) Delete inventory item (optional)
        try:
            self.delete_inventory_item(sku)
        except EbayAPIError as e:
            self.logger.warning(f"Failed to delete inventory item {sku}: {e}")
