# app/routes.py

from flask import Blueprint, request, jsonify
from db.interface import db_interface  # Our DB interface class

# eBay and Etsy integration
from utils.ebay_interface import EbayInterface, EbayAPIError
from utils.etsy_interface import EtsyInterface, EtsyAPIError

api = Blueprint("api", __name__)  # This stays global


class APIRoutes:
    def __init__(self):
        self.db = db_interface()

        self.ebay = None
        self.etsy = None

        # ---- eBay credentials from DB ----
        try:
            ebay_creds = self.db.get_marketplace_credentials("EBAY", organization_id=None)
            if ebay_creds:
                ebay_client_id, ebay_client_secret, ebay_env = ebay_creds
                self.ebay = EbayInterface(
                    client_id=ebay_client_id,
                    client_secret=ebay_client_secret,
                    env=ebay_env,
                )
                print("[INFO] eBay integration enabled from DB credentials.")
            else:
                print("[WARN] No eBay credentials found; eBay integration disabled.")
        except Exception as e:
            print(f"[WARN] eBay integration disabled: {e}")

        # ---- Etsy credentials from DB ----
        try:
            etsy_creds = self.db.get_marketplace_credentials("ETSY", organization_id=None)
            if etsy_creds:
                etsy_client_id, etsy_client_secret, etsy_env = etsy_creds

                # TODO: wire in shop_id + access_token however you're storing them.
                # For now, stub with placeholder or additional columns in MarketplaceCredentials.
                self.etsy = EtsyInterface(
                    client_id=etsy_client_id,
                    client_secret=etsy_client_secret,
                    env=etsy_env,
                    shop_id="YOUR_SHOP_ID_HERE",
                    access_token="YOUR_ACCESS_TOKEN_HERE",
                )
                print("[INFO] Etsy integration enabled from DB credentials.")
            else:
                print("[WARN] No Etsy credentials found; Etsy integration disabled.")
        except Exception as e:
            print(f"[WARN] Etsy integration disabled: {e}")

        self.register_routes()

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    @staticmethod
    def _item_row_to_dict(row):
        """
        Convert an Item row (SELECT item_id, title, description, category,
        list_date, creator_id, sku, quantity) into a JSON-serializable dict.
        """
        if row is None:
            return None

        # row is a tuple in fixed order
        item_id, title, description, category, list_date, creator_id, sku, quantity = row
        return {
            "item_id": item_id,
            "title": title,
            "description": description,
            "category": category,
            "list_date": list_date.isoformat() if list_date else None,
            "creator_id": creator_id,
            "sku": sku,
            "quantity": quantity,
        }

    @staticmethod
    def _org_row_to_dict(row):
        # SELECT organization_id, name FROM Organization;
        if row is None:
            return None
        organization_id, name = row
        return {"organization_id": organization_id, "name": name}

    @staticmethod
    def _reseller_row_to_dict(row):
        # SELECT reseller_id, reseller_name FROM Reseller;
        if row is None:
            return None
        reseller_id, reseller_name = row
        return {"reseller_id": reseller_id, "reseller_name": reseller_name}

    @staticmethod
    def _transaction_row_to_dict(row):
        # SELECT transaction_id, sale_date, total, tax, reseller_comission, reseller_id FROM AppTransaction;
        if row is None:
            return None
        transaction_id, sale_date, total, tax, reseller_comission, reseller_id = row
        return {
            "transaction_id": transaction_id,
            "sale_date": sale_date.isoformat() if sale_date else None,
            "total": float(total) if total is not None else None,
            "tax": float(tax) if tax is not None else None,
            "reseller_comission": float(reseller_comission) if reseller_comission is not None else None,
            "reseller_id": reseller_id,
        }

    # ------------------------------------------------------------------
    # Route registration
    # ------------------------------------------------------------------

    def register_routes(self):
        # ----------------------------
        # Auth / Login
        # ----------------------------
        @api.route("/login", methods=["POST"])
        def login():
            data = request.get_json(force=True) or {}
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return jsonify({"error": "Username and password are required"}), 400

            user_row = self.db.get_user_by_username(username)
            if not user_row:
                return jsonify({"error": "Invalid username or password"}), 401

            # user_row = (user_id, username, password, email, organization_id, organization_role)
            user_id, db_username, db_password, email, organization_id, organization_role = user_row

            # NOTE: plain-text comparison; replace with hashed auth in production
            if password != db_password:
                return jsonify({"error": "Invalid username or password"}), 401

            user = {
                "user_id": user_id,
                "username": db_username,
                "email": email,
                "organization_id": organization_id,
                "organization_role": organization_role,
            }
            return jsonify({"message": "Login successful", "user": user}), 200

        # ----------------------------
        # Items
        # ----------------------------

        @api.route("/items", methods=["GET"])
        def get_items():
            rows = self.db.get_all_items()
            if not rows:
                return jsonify([]), 200

            # get_all_items currently selects:
            #   item_id, title, description, category, list_date, creator_id
            items = []
            for row in rows:
                item_id, title, description, category, list_date, creator_id = row
                items.append(
                    {
                        "item_id": item_id,
                        "title": title,
                        "description": description,
                        "category": category,
                        "list_date": list_date.isoformat() if list_date else None,
                        "creator_id": creator_id,
                    }
                )
            return jsonify(items), 200

        @api.route("/items/<int:item_id>", methods=["GET"])
        def get_item(item_id):
            # Custom query including sku & quantity
            sql = """
                SELECT item_id, title, description, category, list_date, creator_id, sku, quantity
                FROM Item
                WHERE item_id = %s;
            """
            row = self.db.execute_query(sql, params=(item_id,), fetch_one=True)
            if not row:
                return jsonify({"error": f"Item {item_id} not found"}), 404

            item = self._item_row_to_dict(row)
            return jsonify(item), 200

        @api.route("/items", methods=["POST"])
        def create_item():
            data = request.get_json(force=True) or {}

            title = data.get("title")
            description = data.get("description")
            category = data.get("category")
            list_date = data.get("list_date")  # "YYYY-MM-DD" or let DB cast
            creator_id = data.get("creator_id")

            sku = data.get("sku")
            quantity = data.get("quantity", 0)
            price = data.get("price")  # optional, used for eBay

            if not title or not creator_id:
                return jsonify({"error": "title and creator_id are required"}), 400

            if not list_date:
                list_date = None  # let DB handle default / NULL

            # Use existing DB helper for basic insert
            success = self.db.create_item(title, description, category, list_date, creator_id)
            if not success:
                return jsonify({"error": "Failed to create item"}), 500

            # Retrieve the new item's ID (assumes titles are unique enough for now)
            item_id = self.db.get_item_id_by_title(title)
            if not item_id:
                return jsonify({"error": "Item created but could not retrieve item_id"}), 500

            # If sku / quantity are provided, update them directly
            if sku is not None or quantity is not None:
                sql = "UPDATE Item SET "
                sets = []
                params = []
                if sku is not None:
                    sets.append("sku = %s")
                    params.append(sku)
                if quantity is not None:
                    sets.append("quantity = %s")
                    params.append(quantity)
                sql += ", ".join(sets) + " WHERE item_id = %s;"
                params.append(item_id)
                self.db.execute_query(sql, params=tuple(params), commit=True)

            # Reload full row including sku/quantity for response & eBay
            sql = """
                SELECT item_id, title, description, category, list_date, creator_id, sku, quantity
                FROM Item
                WHERE item_id = %s;
            """
            row = self.db.execute_query(sql, params=(item_id,), fetch_one=True)
            item = self._item_row_to_dict(row)

            # Prepare dict used for eBay sync
            item_dict = {
                "item_id": item["item_id"],
                "sku": item.get("sku") or sku,
                "title": item["title"],
                "description": item.get("description") or "",
                "category": item.get("category") or "",
                "quantity": item.get("quantity") if item.get("quantity") is not None else (quantity or 0),
                "price": str(price) if price is not None else "0.00",
            }

            # Push to eBay
            if self.ebay and item_dict["sku"]:
                try:
                    ebay_result = self.ebay.sync_item_create_or_update(item_dict)
                    item["ebay_sync"] = "ok"
                    item["ebay_response"] = ebay_result
                except EbayAPIError as e:
                    item["ebay_sync"] = "failed"
                    item["ebay_error"] = str(e)

            # Same for Etsy
            if self.etsy:
                try:
                    etsy_result = self.etsy.sync_item_create_or_update(item_dict)
                    item["etsy_sync"] = "ok"
                    item["etsy_response"] = etsy_result
                    # TODO: item["etsy_listing_id"] = etsy_result.get("listing_id")
                except EtsyAPIError as e:
                    item["etsy_sync"] = "failed"
                    item["etsy_error"] = str(e)
            return jsonify(item), 201

        @api.route("/items/<int:item_id>", methods=["PUT", "PATCH"])
        def update_item(item_id):
            data = request.get_json(force=True) or {}

            description = data.get("description")
            category = data.get("category")
            sku = data.get("sku")
            quantity = data.get("quantity")
            price = data.get("price")

            # Build dynamic update so we can handle sku/quantity too
            fields = []
            params = []

            if description is not None:
                fields.append("description = %s")
                params.append(description)
            if category is not None:
                fields.append("category = %s")
                params.append(category)
            if sku is not None:
                fields.append("sku = %s")
                params.append(sku)
            if quantity is not None:
                fields.append("quantity = %s")
                params.append(quantity)

            if not fields:
                return jsonify({"error": "No updatable fields provided"}), 400

            sql = "UPDATE Item SET " + ", ".join(fields) + " WHERE item_id = %s;"
            params.append(item_id)
            self.db.execute_query(sql, params=tuple(params), commit=True)

            # Reload full row
            sql = """
                SELECT item_id, title, description, category, list_date, creator_id, sku, quantity
                FROM Item
                WHERE item_id = %s;
            """
            row = self.db.execute_query(sql, params=(item_id,), fetch_one=True)
            if not row:
                return jsonify({"error": f"Item {item_id} not found after update"}), 404

            item = self._item_row_to_dict(row)

            # Prepare dict for eBay sync
            item_dict = {
                "item_id": item["item_id"],
                "sku": item.get("sku") or sku,
                "title": item["title"],
                "description": item.get("description") or "",
                "category": item.get("category") or "",
                "quantity": item.get("quantity") if item.get("quantity") is not None else (quantity or 0),
                "price": str(price) if price is not None else "0.00",
            }

            # Push to eBay (Same routine as create_item)
            if self.ebay and item_dict["sku"]:
                try:
                    ebay_result = self.ebay.sync_item_create_or_update(item_dict)
                    item["ebay_sync"] = "ok"
                    item["ebay_response"] = ebay_result
                except EbayAPIError as e:
                    item["ebay_sync"] = "failed"
                    item["ebay_error"] = str(e)

            # Same for Etsy
            if self.etsy:
                try:
                    etsy_result = self.etsy.sync_item_create_or_update(item_dict)
                    item["etsy_sync"] = "ok"
                    item["etsy_response"] = etsy_result
                    # TODO: item["etsy_listing_id"] = etsy_result.get("listing_id")
                except EtsyAPIError as e:
                    item["etsy_sync"] = "failed"
                    item["etsy_error"] = str(e)

            return jsonify(item), 200

        @api.route("/items/<int:item_id>", methods=["DELETE"])
        def delete_item(item_id):
            # Load row first so we know the SKU for eBay
            sql = """
                SELECT item_id, title, description, category, list_date, creator_id, sku, quantity
                FROM Item
                WHERE item_id = %s;
            """
            row = self.db.execute_query(sql, params=(item_id,), fetch_one=True)
            if not row:
                return jsonify({"error": f"Item {item_id} not found"}), 404

            item = self._item_row_to_dict(row)

            # Try to delete from eBay first (but don't hard-fail if it breaks)
            if self.ebay and item.get("sku"):
                try:
                    self.ebay.sync_item_delete({"sku": item["sku"]})
                    ebay_status = "ok"
                except EbayAPIError as e:
                    ebay_status = f"failed: {e}"
            else:
                ebay_status = "not_configured"

            # Same routine for Etsy
            if self.etsy:
                try:
                    self.etsy.sync_item_delete(item)
                    etsy_status = "ok"
                except EtsyAPIError as e:
                    etsy_status = f"failed: {e}"
            else:
                etsy_status = "not_configured"

            success = self.db.delete_item(item_id)
            if not success:
                return jsonify({"error": f"Failed to delete item {item_id}"}), 500

            return jsonify(
                {
                    "message": f"Item {item_id} deleted successfully",
                    "ebay_sync": ebay_status,
                    "etsy_sync": etsy_status,
                }
            ), 200

        # ----------------------------
        # Organizations
        # ----------------------------

        @api.route("/organizations", methods=["GET"])
        def get_organizations():
            rows = self.db.get_all_organizations()
            orgs = [self._org_row_to_dict(r) for r in rows] if rows else []
            return jsonify(orgs), 200

        @api.route("/organizations/<int:organization_id>", methods=["GET"])
        def get_organization(organization_id):
            row = self.db.get_organization_by_id(organization_id)
            if not row:
                return jsonify({"error": f"Organization {organization_id} not found"}), 404
            org = self._org_row_to_dict(row)
            return jsonify(org), 200

        @api.route("/organizations", methods=["POST"])
        def create_organization():
            data = request.get_json(force=True) or {}
            name = data.get("name")
            if not name:
                return jsonify({"error": "name is required"}), 400

            success = self.db.create_organization(name)
            if not success:
                return jsonify({"error": "Failed to create organization"}), 500

            org_id = self.db.get_organization_id_by_name(name)
            return jsonify({"organization_id": org_id, "name": name}), 201

        @api.route("/organizations/<int:organization_id>", methods=["PUT", "PATCH"])
        def update_organization(organization_id):
            data = request.get_json(force=True) or {}
            name = data.get("name")
            if not name:
                return jsonify({"error": "name is required"}), 400

            success = self.db.update_organization_name(organization_id, name)
            if not success:
                return jsonify({"error": f"Failed to update organization {organization_id}"}), 500

            return jsonify({"organization_id": organization_id, "name": name}), 200

        @api.route("/organizations/<int:organization_id>", methods=["DELETE"])
        def delete_organization(organization_id):
            success = self.db.delete_organization(organization_id)
            if not success:
                return jsonify({"error": f"Failed to delete organization {organization_id}"}), 500
            return jsonify({"message": f"Organization {organization_id} deleted successfully"}), 200

        # ----------------------------
        # Resellers
        # ----------------------------

        @api.route("/resellers", methods=["GET"])
        def get_resellers():
            rows = self.db.get_all_resellers()
            resellers = [self._reseller_row_to_dict(r) for r in rows] if rows else []
            return jsonify(resellers), 200

        @api.route("/resellers/<int:reseller_id>", methods=["GET"])
        def get_reseller(reseller_id):
            row = self.db.get_reseller_by_id(reseller_id)
            if not row:
                return jsonify({"error": f"Reseller {reseller_id} not found"}), 404
            reseller = self._reseller_row_to_dict(row)
            return jsonify(reseller), 200

        @api.route("/resellers", methods=["POST"])
        def create_reseller():
            data = request.get_json(force=True) or {}
            reseller_name = data.get("reseller_name")
            if not reseller_name:
                return jsonify({"error": "reseller_name is required"}), 400

            success = self.db.create_reseller(reseller_name)
            if not success:
                return jsonify({"error": "Failed to create reseller"}), 500

            reseller_id = self.db.get_reseller_id_by_name(reseller_name)
            return jsonify({"reseller_id": reseller_id, "reseller_name": reseller_name}), 201

        @api.route("/resellers/<int:reseller_id>", methods=["PUT", "PATCH"])
        def update_reseller(reseller_id):
            data = request.get_json(force=True) or {}
            reseller_name = data.get("reseller_name")
            if not reseller_name:
                return jsonify({"error": "reseller_name is required"}), 400

            success = self.db.update_reseller_name(reseller_id, reseller_name)
            if not success:
                return jsonify({"error": f"Failed to update reseller {reseller_id}"}), 500

            return jsonify({"reseller_id": reseller_id, "reseller_name": reseller_name}), 200

        @api.route("/resellers/<int:reseller_id>", methods=["DELETE"])
        def delete_reseller(reseller_id):
            success = self.db.delete_reseller(reseller_id)
            if not success:
                return jsonify({"error": f"Failed to delete reseller {reseller_id}"}), 500
            return jsonify({"message": f"Reseller {reseller_id} deleted successfully"}), 200

        # ----------------------------
        # Transactions
        # ----------------------------

        @api.route("/transactions/<int:transaction_id>", methods=["GET"])
        def get_transaction(transaction_id):
            row = self.db.get_transaction_by_id(transaction_id)
            if not row:
                return jsonify({"error": f"Transaction {transaction_id} not found"}), 404
            tx = self._transaction_row_to_dict(row)
            # Also pull items for this transaction
            items = self.db.get_items_for_transaction(transaction_id) or []
            tx["items"] = [
                {
                    "transaction_item_id": r[0],
                    "title": r[1],
                    "description": r[2],
                    "category": r[3],
                }
                for r in items
            ]
            return jsonify(tx), 200

        @api.route("/transactions", methods=["POST"])
        def create_transaction():
            data = request.get_json(force=True) or {}
            sale_date = data.get("sale_date")
            total = data.get("total", 0.0)
            tax = data.get("tax", 0.0)
            reseller_comission = data.get("reseller_comission", 0.0)
            reseller_id = data.get("reseller_id")

            if not sale_date or reseller_id is None:
                return jsonify({"error": "sale_date and reseller_id are required"}), 400

            success = self.db.create_transaction(sale_date, total, tax, reseller_comission, reseller_id)
            if not success:
                return jsonify({"error": "Failed to create transaction"}), 500

            # sale_date might not be unique, so we grab the latest ID for that date
            ids = self.db.get_transaction_ids_by_date(sale_date) or []
            transaction_id = ids[-1] if ids else None

            return jsonify(
                {
                    "transaction_id": transaction_id,
                    "sale_date": sale_date,
                    "total": total,
                    "tax": tax,
                    "reseller_comission": reseller_comission,
                    "reseller_id": reseller_id,
                }
            ), 201

        @api.route("/transactions/<int:transaction_id>", methods=["PUT", "PATCH"])
        def update_transaction(transaction_id):
            data = request.get_json(force=True) or {}
            total = data.get("total")
            tax = data.get("tax")
            reseller_comission = data.get("reseller_comission")

            if total is None or tax is None or reseller_comission is None:
                return jsonify({"error": "total, tax, and reseller_comission are required"}), 400

            success = self.db.update_transaction_totals(transaction_id, total, tax, reseller_comission)
            if not success:
                return jsonify({"error": f"Failed to update transaction {transaction_id}"}), 500

            return jsonify(
                {
                    "transaction_id": transaction_id,
                    "total": total,
                    "tax": tax,
                    "reseller_comission": reseller_comission,
                }
            ), 200

        @api.route("/transactions/<int:transaction_id>", methods=["DELETE"])
        def delete_transaction(transaction_id):
            success = self.db.delete_transaction(transaction_id)
            if not success:
                return jsonify({"error": f"Failed to delete transaction {transaction_id}"}), 500
            return jsonify({"message": f"Transaction {transaction_id} deleted successfully"}), 200

        # ----------------------------
        # Link Items to Transactions
        # ----------------------------

        @api.route("/transactions/link", methods=["POST"])
        def link_transaction_item():
            data = request.get_json(force=True) or {}
            item_id = data.get("item_id")
            transaction_id = data.get("transaction_id")

            if item_id is None or transaction_id is None:
                return jsonify({"error": "Both item_id and transaction_id are required"}), 400

            success = self.db.link_item_to_transaction(item_id, transaction_id)
            if not success:
                return jsonify({"error": "Failed to link item and transaction"}), 500

            # Retrieve the new link id (optional)
            link_id = self.db.get_transaction_item_id_by_link(item_id, transaction_id)
            return jsonify(
                {
                    "message": f"Item {item_id} linked to transaction {transaction_id}",
                    "transaction_item_id": link_id,
                }
            ), 201

        @api.route("/transactions/unlink/<int:transaction_item_id>", methods=["DELETE"])
        def unlink_transaction_item(transaction_item_id):
            success = self.db.unlink_item_from_transaction(transaction_item_id)
            if not success:
                return jsonify({"error": f"Failed to remove transaction item link {transaction_item_id}"}), 500
            return jsonify({"message": f"Transaction item link {transaction_item_id} removed"}), 200
