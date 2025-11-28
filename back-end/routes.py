# app/routes.py

from flask import Blueprint, request, jsonify
from db.interface import DBInterface  # Our DB interface class

# eBay and Etsy integration (kept for future use, but initialization logic is removed)
from utils.ebay_interface import EbayInterface, EbayAPIError
from utils.etsy_interface import EtsyInterface, EtsyAPIError

api = Blueprint("api", __name__)  # This stays global


class APIRoutes:
    def __init__(self):
        # NOTE: The DBInterface class now uses RealDictCursor, so all fetch_one/fetch_all 
        # calls return dictionaries (or a list of dictionaries).
        self.db = DBInterface()

        try:
            self.ebay = EbayInterface()
        except EbayAPIError as e:
            print(f"[Err] Unable to initialize Ebay Interface \n Err: {e}")
        try:
            self.etsy = EtsyInterface()
        except EtsyAPIError as e:
            print(f"[Err] Unable to initialize Etsy Interface \n Err: {e}")

        # WARNING: MARKETPLACE CREDENTIALS REFACTORING
        # The logic below for fetching global credentials has been removed 
        # as the 'MarketplaceCredentials' table is not in your schema.
        print("[WARN] Global marketplace credential fetching removed. Implement per-user auth.")

        self.register_routes()

    # ------------------------------------------------------------------
    # Helper methods 
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_money_to_float(money_str):
        """
        Safely converts a PostgreSQL MONEY string (e.g., '$120.00') to a float.
        """
        if money_str is None:
            return None
        try:
            # Strip currency symbols, commas (thousands separators), and spaces
            cleaned_str = str(money_str).strip().replace('$', '').replace('£', '').replace('€', '').replace(',', '')
            return float(cleaned_str)
        except ValueError:
            return None
    
    @staticmethod
    def _item_row_to_dict(row: dict):
        """
        Convert an Item row (dictionary) into a JSON-serializable dict.
        """
        if row is None:
            return None

        return {
            "item_id": row.get("item_id"),
            "title": row.get("title"),
            "price": APIRoutes._safe_money_to_float(row.get("price")) if row.get("price") else None,
            "description": row.get("description"),
            "category": row.get("category"),
            "list_date": row.get("list_date").isoformat() if row.get("list_date") else None,
            "creator_id": row.get("creator_id"),
        }

    @staticmethod
    def _org_row_to_dict(row: dict):
        if row is None:
            return None
        return {"organization_id": row.get("organization_id"), "name": row.get("name")}

    @staticmethod
    def _transaction_row_to_dict(row: dict):
        """
        Converts AppTransaction row to a dict.
        NOTE: The output keys are mapped back to 'reseller_id' and 'reseller_comission'
              to ensure compatibility with the existing test_routes.py file.
        """
        if row is None:
            return None
        
        return {
            "transaction_id": row.get("transaction_id"),
            "sale_date": row.get("sale_date").isoformat() if row.get("sale_date") else None,
            "total": APIRoutes._safe_money_to_float(row.get("total")),
            "tax": APIRoutes._safe_money_to_float(row.get("tax")),
            "reseller_comission": APIRoutes._safe_money_to_float(row.get("seller_comission")),
            "reseller_id": row.get("seller_id"),
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

            user_row = self.db.get_app_user_by_username(username)
            if not user_row:
                return jsonify({"error": "Invalid username or password"}), 401
            
            db_password = user_row["password"]

            # NOTE: plain-text comparison; replace with hashed auth in production
            if password != db_password:
                return jsonify({"error": "Invalid username or password"}), 401

            user = {
                "user_id": user_row["user_id"],
                "username": user_row["username"],
                "email": user_row["email"],
                "organization_id": user_row["organization_id"],
                "organization_role": user_row["organization_role"],
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

            items = [self._item_row_to_dict(row) for row in rows]
            return jsonify(items), 200

        @api.route("/users/<int:user_id>/items", methods=["GET"])
        def get_user_items(user_id):
            """Retrieves all Item records created by the specified AppUser."""
            rows = self.db.get_all_items_by_appuser_id(user_id)
            if not rows:
                return jsonify([]), 200
            
            items = [self._item_row_to_dict(row) for row in rows]
            return jsonify(items), 200

        @api.route("/items/<int:item_id>", methods=["GET"])
        def get_item(item_id):
            row = self.db.get_item_by_id(item_id)
            if not row:
                return jsonify({"error": f"Item {item_id} not found"}), 404

            item = self._item_row_to_dict(row)
            return jsonify(item), 200

        @api.route("/items", methods=["POST"])
        def create_item():
            data = request.get_json(force=True) or {}

            title = data.get("title")
            price = data.get("price")
            description = data.get("description")
            category = data.get("category")
            list_date = data.get("list_date") 
            creator_id = data.get("creator_id")
            
            if not title or not creator_id:
                return jsonify({"error": "title and creator_id are required"}), 400

            if not list_date:
                list_date = None

            # Price is included
            success = self.db.create_item(title, price, description, category, list_date, creator_id)
            if not success:
                return jsonify({"error": "Failed to create item"}), 500

            # Retrieve the new item's ID using a custom query with RETURNING
            # Note: Using RETURNING is more robust than ordering by DESC
            sql = "INSERT INTO Item (title, price, description , category, list_date, creator_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING item_id, title, price, description, category, list_date, creator_id;"
            params = (title, price, description, category, list_date, creator_id)
            row = self.db.execute_query(sql, params=params, fetch_one=True, commit=True)
            
            if not row:
                 return jsonify({"error": "Item created but could not retrieve details"}), 500

            item = self._item_row_to_dict(row)

            item["ebay_sync"] = "disabled (no credentials/logic in route)"
            item["etsy_sync"] = "disabled (no credentials/logic in route)"

            return jsonify(item), 201

        @api.route("/items/<int:item_id>", methods=["PUT", "PATCH"])
        def update_item(item_id):
            data = request.get_json(force=True) or {}

            # Fetch existing data to ensure all fields are available for the comprehensive update method
            row = self.db.get_item_by_id(item_id)
            if not row:
                return jsonify({"error": f"Item {item_id} not found"}), 404

            # Use new data if provided, otherwise use existing data
            title = data.get("title", row["title"])
            price = data.get("price", APIRoutes._safe_money_to_float(row["price"]))
            description = data.get("description", row["description"])
            category = data.get("category", row["category"])
            list_date = data.get("list_date", row["list_date"].isoformat() if row["list_date"] else None)

            success = self.db.update_item(item_id, title, price, description, category, list_date)
            if not success:
                return jsonify({"error": f"Failed to update item {item_id}"}), 500

            # Reload full row
            row = self.db.get_item_by_id(item_id)
            item = self._item_row_to_dict(row)

            item["ebay_sync"] = "disabled (no credentials/logic in route)"
            item["etsy_sync"] = "disabled (no credentials/logic in route)"

            return jsonify(item), 200

        @api.route("/items/<int:item_id>", methods=["DELETE"])
        def delete_item(item_id):
            # Load row first (optional, kept for original logic's structure)
            row = self.db.get_item_by_id(item_id)
            if not row:
                return jsonify({"error": f"Item {item_id} not found"}), 404

            ebay_status = "not_configured_in_route"
            etsy_status = "not_configured_in_route"

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

            # Use custom query with RETURNING to get the new ID efficiently
            sql = "INSERT INTO Organization (name) VALUES (%s) RETURNING organization_id;"
            result = self.db.execute_query(sql, params=(name,), fetch_one=True, commit=True)
            org_id = result["organization_id"] if result else None

            if not org_id:
                return jsonify({"error": "Failed to create organization"}), 500
            
            return jsonify({"organization_id": org_id, "name": name}), 201

        @api.route("/organizations/<int:organization_id>", methods=["PUT", "PATCH"])
        def update_organization(organization_id):
            data = request.get_json(force=True) or {}
            name = data.get("name")
            if not name:
                return jsonify({"error": "name is required"}), 400

            success = self.db.update_organization(organization_id, name)
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
        # Transactions
        # ----------------------------

        @api.route("/transactions/<int:transaction_id>", methods=["GET"])
        def get_transaction(transaction_id):
            row = self.db.get_app_transaction_by_id(transaction_id)
            if not row:
                return jsonify({"error": f"Transaction {transaction_id} not found"}), 404
            
            tx = self._transaction_row_to_dict(row)
            
            # Pull items for this transaction
            sql = """
                SELECT ati.transaction_item_id, i.item_id, i.title, i.description, i.category 
                FROM AppTransaction_Item ati
                JOIN Item i ON ati.item_id = i.item_id
                WHERE ati.transaction_id = %s;
            """
            items_rows = self.db.execute_query(sql, params=(transaction_id,), fetch_all=True) or []

            tx["items"] = [
                {
                    "transaction_item_id": r["transaction_item_id"],
                    "item_id": r["item_id"],
                    "title": r["title"],
                    "description": r["description"],
                    "category": r["category"],
                }
                for r in items_rows
            ]
            return jsonify(tx), 200

        @api.route("/transactions", methods=["POST"])
        def create_transaction():
            data = request.get_json(force=True) or {}
            sale_date = data.get("sale_date")
            total = data.get("total", 0.0)
            tax = data.get("tax", 0.0)
            
            # MAPPING FOR TEST COMPATIBILITY: Test script sends reseller_*, DB needs seller_*
            seller_comission = data.get("reseller_comission", 0.0)
            seller_id = data.get("reseller_id")

            if not sale_date or seller_id is None:
                return jsonify({"error": "sale_date and reseller_id are required"}), 400

            # Use a custom query with RETURNING to get the new ID efficiently
            sql = "INSERT INTO AppTransaction (sale_date, total, tax, seller_comission, seller_id) VALUES (%s, %s, %s, %s, %s) RETURNING transaction_id, sale_date, total, tax, seller_comission, seller_id;"
            params = (sale_date, total, tax, seller_comission, seller_id)
            result = self.db.execute_query(sql, params=params, fetch_one=True, commit=True)
            
            if not result:
                return jsonify({"error": "Failed to create transaction"}), 500
            
            # Use the helper to map the output columns back to the test script's expected keys
            return jsonify(self._transaction_row_to_dict(result)), 201

        @api.route("/transactions/<int:transaction_id>", methods=["PUT", "PATCH"])
        def update_transaction(transaction_id):
            data = request.get_json(force=True) or {}
            
            # Fetch existing transaction to fill in missing required fields 
            row = self.db.get_app_transaction_by_id(transaction_id)
            if not row:
                return jsonify({"error": f"Transaction {transaction_id} not found"}), 404
            
            # MAPPING FOR TEST COMPATIBILITY: Test script sends reseller_*, DB needs seller_*
            # Use new data if provided, otherwise use existing data (converting from DB's seller_* to internal variables)
            sale_date = data.get("sale_date", row["sale_date"].isoformat() if row["sale_date"] else None)
            total = data.get("total", APIRoutes._safe_money_to_float(row["total"]))
            tax = data.get("tax", APIRoutes._safe_money_to_float(row["tax"]))
            seller_comission = data.get("reseller_comission", APIRoutes._safe_money_to_float(row["seller_comission"]))
            seller_id = data.get("reseller_id", row["seller_id"])

            # Call the DB method with the correct (new) schema names
            success = self.db.update_app_transaction(transaction_id, sale_date, total, tax, seller_comission, seller_id)
            if not success:
                return jsonify({"error": f"Failed to update transaction {transaction_id}"}), 500

            # Reload to get the latest data and use helper for output mapping
            updated_row = self.db.get_app_transaction_by_id(transaction_id)
            return jsonify(self._transaction_row_to_dict(updated_row)), 200

        @api.route("/transactions/<int:transaction_id>", methods=["DELETE"])
        def delete_transaction(transaction_id):
            success = self.db.delete_app_transaction(transaction_id)
            if not success:
                return jsonify({"error": f"Failed to delete transaction {transaction_id}"}), 500
            return jsonify({"message": f"Transaction {transaction_id} deleted successfully"}), 200

        # Get all transaction rows for a given user.
        @api.route("/users/<int:user_id>/transactions", methods=["GET"])
        def get_user_transactions(user_id):
            """Retrieves all AppTransaction records sold by the specified AppUser."""
            # Calls the corresponding function in db.interface
            rows = self.db.get_app_transactions_by_seller_id(user_id)
            if not rows:
                return jsonify([]), 200
            
            # Use the helper to map output columns to the test script's expected keys 
            # and safely convert the MONEY fields to float.
            transactions = [self._transaction_row_to_dict(row) for row in rows]
            return jsonify(transactions), 200

        # ----------------------------
        # Link Items to Transactions
        # ----------------------------

        @api.route("/items/<int:item_id>/transactions", methods=["GET"])
        def get_item_transactions(item_id):
            """Retrieves all AppTransaction records associated with the specified item_id."""
            rows = self.db.get_app_transactions_by_item_id(item_id)
            if not rows:
                return jsonify([]), 200
            
            transactions = [self._transaction_row_to_dict(row) for row in rows]
            return jsonify(transactions), 200

        @api.route("/transactions/link", methods=["POST"])
        def link_transaction_item():
            data = request.get_json(force=True) or {}
            item_id = data.get("item_id")
            transaction_id = data.get("transaction_id")

            if item_id is None or transaction_id is None:
                return jsonify({"error": "Both item_id and transaction_id are required"}), 400

            success = self.db.create_app_transaction_item(item_id, transaction_id)
            if not success:
                return jsonify({"error": "Failed to link item and transaction"}), 500

            # Retrieve the new link id using a custom query since the new interface doesn't use RETURNING
            sql = "SELECT transaction_item_id FROM AppTransaction_Item WHERE item_id = %s AND transaction_id = %s ORDER BY transaction_item_id DESC LIMIT 1;"
            result = self.db.execute_query(sql, params=(item_id, transaction_id), fetch_one=True)
            link_id = result["transaction_item_id"] if result else None
            
            return jsonify(
                {
                    "message": f"Item {item_id} linked to transaction {transaction_id}",
                    "transaction_item_id": link_id,
                }
            ), 201

        @api.route("/transactions/unlink/<int:transaction_item_id>", methods=["DELETE"])
        def unlink_transaction_item(transaction_item_id):
            success = self.db.delete_app_transaction_item(transaction_item_id)
            if not success:
                return jsonify({"error": f"Failed to remove transaction item link {transaction_item_id}"}), 500
            return jsonify({"message": f"Transaction item link {transaction_item_id} removed"}), 200