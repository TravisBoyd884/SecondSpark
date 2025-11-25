# etsy_interface.py

import time
import logging
from typing import Any, Dict, Optional

import requests


class EtsyAPIError(Exception):
    """Generic exception for Etsy API errors."""
    pass


class EtsyInterface:
    def __init__(
        self,
            client_id: str,
            client_secret: str,
            env: str = "production",
            shop_id: Optional[str] = None,
            access_token: Optional[str] = None,
    ):
        if not client_id or not client_secret:
            raise EtsyAPIError("Missing Etsy API credentials")

        self.client_id = client_id
        self.client_secret = client_secret
        self.env = env.lower()
        self.shop_id = shop_id
        self.access_token = access_token  # for now assume we have one

        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()

        # Base URL (Etsy doesn't have a sandbox like eBay; usually test with private listings)
        self.base_url = "https://openapi.etsy.com/v3/application"

    # ------------------------------------------------------------------
    # Low-level HTTP helpers
    # ------------------------------------------------------------------

    def _auth_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Etsy v3 uses OAuth2 Bearer tokens. You will need to manage access_token lifecycle
        (init, refresh) externally and pass it into this class.
        """
        if not self.access_token:
            raise EtsyAPIError("No Etsy access_token configured")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "x-api-key": self.client_id,
        }
        if extra:
            headers.update(extra)
        return headers

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self.session.request(method, url, timeout=30, **kwargs)
        if not resp.ok:
            raise EtsyAPIError(f"Etsy API error {resp.status_code}: {resp.text}")
        if resp.text:
            return resp.json()
        return {}

    # ------------------------------------------------------------------
    # Listing operations (simplified)
    # ------------------------------------------------------------------

    def create_or_update_listing(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a listing for the configured shop.

        Expected keys in `item`:
          - title
          - description
          - quantity
          - price
          - sku (optional)
        """
        if not self.shop_id:
            raise EtsyAPIError("No Etsy shop_id configured")

        headers = self._auth_headers()

        title = item["title"]
        description = item.get("description") or title
        quantity = int(item.get("quantity", 0))
        price = str(item.get("price", "0.00"))
        sku = item.get("sku")

        # This is a VERY simplified payload; Etsy requires more fields in production
        payload: Dict[str, Any] = {
            "title": title,
            "description": description,
            "quantity": quantity,
            "price": price,
            "who_made": "someone_else",   # TODO: fill appropriately
            "is_supply": False,           # TODO
            "when_made": "2020_2024",     # TODO
        }
        if sku:
            payload["skus"] = [sku]

        # For a real implementation, you'd check if an Etsy listing_id exists and PUT vs POST.
        # Here we assume "create" via POST to /shops/{shop_id}/listings
        path = f"/shops/{self.shop_id}/listings"
        return self._request("POST", path, headers=headers, json=payload)

    def delete_listing(self, listing_id: str) -> None:
        """
        Delete or deactivate an Etsy listing.
        """
        if not self.shop_id:
            raise EtsyAPIError("No Etsy shop_id configured")

        headers = self._auth_headers()
        path = f"/shops/{self.shop_id}/listings/{listing_id}"
        self._request("DELETE", path, headers=headers)

    # ------------------------------------------------------------------
    # High-level helpers to mirror EbayInterface API
    # ------------------------------------------------------------------

    def sync_item_create_or_update(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        High-level sync helper to align with EbayInterface API.
        """
        return self.create_or_update_listing(item)

    def sync_item_delete(self, item: Dict[str, Any]) -> None:
        """
        High-level delete helper. Expects 'etsy_listing_id' in the item dict.
        """
        listing_id = item.get("etsy_listing_id")
        if not listing_id:
            # If you haven't stored the listing id yet, you may decide to do nothing
            self.logger.warning("No etsy_listing_id set; cannot delete listing")
            return
        self.delete_listing(listing_id)
