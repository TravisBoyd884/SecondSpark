# app/routes.py

from flask import Blueprint, request, jsonify
from db.interface import DBInterface  # Our DB interface class

# eBay and Etsy integration (kept for future use, but initialization logic is removed)
from utils.ebay_interface import EbayInterface, EbayAPIError
from utils.etsy_interface import EtsyInterface, EtsyAPIError

# For file uploads (photos)
from werkzeug.utils import secure_filename
import uuid

api = Blueprint("api", __name__)  # This stays global


# --- Configuration for file uploads (You will need to define this in your main Flask app config) ---
UPLOAD_FOLDER = 'static/uploads' # This should be configured in app.config
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class APIRoutes:
    def __init__(self):
        # NOTE: The DBInterface class now uses RealDictCursor, so all fetch_one/fetch_all 
        # calls return dictionaries (or a list of dictionaries).
        self.db = DBInterface()

        try:
            self.ebay = EbayInterface()
        except EbayAPIError as e:
            print(f"[Err] Unable to initialize Ebay Interface \n Err: {e}")
        except Exception as e:
            print(f"[Err] Exception occured on eBay interface\n Err: {e}")
        try:
            self.etsy = EtsyInterface()
        except EtsyAPIError as e:
            print(f"[Err] Unable to initialize Etsy Interface \n Err: {e}")
        except Exception as e:
            print(f"[Err] Exception occured on Etsy interface\n Err: {e}")


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
    def _user_row_to_dict(row: dict):
        """
        Convert an AppUser row (dictionary) into a JSON-serializable dict,
        excluding the password.
        """
        if row is None:
            return None

        return {
            "user_id": row.get("user_id"),
            "username": row.get("username"),
            "email": row.get("email"),
            "organization_id": row.get("organization_id"),
            "organization_role": row.get("organization_role"),
            "ebay_account_id": row.get("ebay_account_id"),
            "etsy_account_id": row.get("etsy_account_id"),
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
            "seller_comission": APIRoutes._safe_money_to_float(row.get("seller_comission")),
            "seller_id": row.get("seller_id"),
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

        @api.route("/register", methods=["POST"])
        def register_user():
            """
            Creates a new user and assigns them to an organization with a default 'member' role.
            This route is intended for public-facing user sign-up.
            """
            data = request.get_json(force=True) or {}
            username = data.get("username")
            password = data.get("password")
            email = data.get("email")
            organization_id = data.get("organization_id")
            organization_role = "member"  # Default role for self-registration

            if not all([username, password, email, organization_id]):
                return (
                    jsonify(
                        {
                            "error": "Username, password, email, and organization_id are required for registration"
                        }
                    ),
                    400,
                )
            
            # Check if organization exists
            if not self.db.get_organization_by_id(organization_id):
                return jsonify({"error": f"Organization with ID {organization_id} not found"}), 404

            # Perform the creation
            success = self.db.create_app_user(
                username, password, email, organization_id, organization_role
            )
            
            if not success:
                return jsonify({"error": "Failed to create user. Username or email may already be in use."}), 500

            user_id = self.db.get_user_id_by_username(username)
            return (
                jsonify({"message": "User registered successfully", "user_id": user_id}),
                201,
            )

        @api.route("/users/<int:user_id>", methods=["GET"])
        def get_user_by_id(user_id):
            """Retrieves an AppUser record by their ID."""
            row = self.db.get_app_user_by_id(user_id)
            if not row:
                return jsonify({"error": f"User {user_id} not found"}), 404
            
            user = self._user_row_to_dict(row)
            return jsonify(user), 200

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

        # Upload an image for a given item id
        @api.route('/item/<int:item_id>/image', methods=['POST'])
        def upload_item_image(item_id):
            # Check if the post request has the file part
            if 'file' not in request.files:
                return jsonify({"error": "No file part in the request"}), 400
            file = request.files['file']
            
            # If user does not select file, browser also submits an empty part without filename
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            
            if file and allowed_file(file.filename):
                # 1. Generate a unique filename (important to prevent clashes)
                filename = secure_filename(file.filename)
                unique_filename = str(uuid.uuid4()) + "_" + filename
                
                # You'll need access to the main application's config to get UPLOAD_FOLDER
                # For simplicity, we'll use the hardcoded path from the config example above
                save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(save_path)
                
                # 2. Store the public-facing URL/path in the database
                # In a real app, this would be a full URL (e.g., S3 URL or your server's static path)
                # Assuming 'static' folder is served at '/' path:
                image_url = f"/uploads/{unique_filename}"
                
                # Optional: Check for 'is_primary' in form data
                is_primary = request.form.get('is_primary', 'false').lower() in ('true', '1', 't')
                
                success = self.db.create_item_image(item_id, image_url, is_primary)
                
                if success:
                    return jsonify({"message": "Image uploaded successfully", "image_url": image_url}), 201
                else:
                    return jsonify({"error": "Failed to save image reference to DB"}), 500

            return jsonify({"error": "Invalid file type"}), 400

        # Get images for a given item id
        @api.route('/item/<int:item_id>/images', methods=['GET'])
        def get_item_images(item_id):
            images = self.db.get_images_by_item_id(item_id)
            if images:
                return jsonify(images), 200
            return jsonify({"message": "No images found for this item"}), 404

        # ----------------------------
        # Organizations
        # ----------------------------

        @api.route("/organizations/<int:organization_id>/users", methods=["GET"])
        def get_organization_users(organization_id):
            """
            Retrieves all AppUser records belonging to a specific organization ID.
            """
            # 1. Check if the organization exists for a clean 404 response
            org_row = self.db.get_organization_by_id(organization_id)
            if not org_row:
                return jsonify({"error": f"Organization {organization_id} not found"}), 404

            # 2. Fetch all users for that organization
            rows = self.db.get_app_users_by_organization_id(organization_id)
            
            if not rows:
                # Organization exists but has no users (returns an empty list)
                return jsonify([]), 200 

            # 3. Clean and return the list of user dictionaries (removes password)
            users = [self._user_row_to_dict(row) for row in rows]
            return jsonify(users), 200

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

        @api.route("/transactions/<int:transaction_id>/items", methods=["GET"])
        def get_transaction_items(transaction_id):
            """Retrieves all Item records associated with the specified transaction_id via AppTransaction_Item."""
            rows = self.db.get_items_for_app_transaction(transaction_id)
            if not rows:
                return jsonify([]), 200
            
            return jsonify(rows), 200

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

        #################
        # Ebay Routes
        #################

        @api.route("/users/<int:user_id>/ebay_account", methods=["GET"])
        def get_ebay_account_for_user(user_id):
            """
            Retrieves the associated Ebay account record for a given user.
            Requires two DB calls: User -> Ebay Account ID -> Ebay Record.
            """
            # 1. Get the user record to find the ebay_account_id
            user_row = self.db.get_app_user_by_id(user_id)
            if not user_row:
                return jsonify({"error": f"User {user_id} not found"}), 404

            ebay_account_id = user_row.get("ebay_account_id")

            if not ebay_account_id:
                return jsonify({"error": f"User {user_id} does not have an eBay account linked"}), 404

            # 2. Get the Ebay account details
            ebay_row = self.db.get_ebay_account_by_id(ebay_account_id)
            if not ebay_row:
                # Should not happen if FKs are correct, but good for robustness
                return jsonify({"error": f"eBay account with ID {ebay_account_id} not found"}), 404

            # NOTE: We return the row directly as it is a dictionary and does not contain
            # highly sensitive, non-API-related fields like 'password'.
            return jsonify(ebay_row), 200

        @api.route("/users/<int:user_id>/ebay_items", methods=["GET"])
        def get_ebay_items_for_user(user_id):
            """
            Retrieves all EbayItem records directly from the database that are
            linked to the user's Ebay account via the AppUser and Ebay tables.
            """
            # 1. Fetch items using the new DB interface function
            rows = self.db.get_ebay_items_by_user_id(user_id)

            if rows is None:
                # Handles potential SQL errors, e.g., if the 'EbayItem' table doesn't exist
                return jsonify(
                    {"error": f"Failed to fetch eBay items for user {user_id} due to a database issue."}), 500

            if not rows:
                # Check if the user exists/is linked to an account to provide a more accurate error message
                user_row = self.db.get_app_user_by_id(user_id)
                if not user_row:
                    return jsonify({"error": f"User {user_id} not found"}), 404
                if not user_row.get("ebay_account_id"):
                    return jsonify({"error": f"User {user_id} does not have an eBay account linked"}), 404

                # User and account exist but no items found in the database
                return jsonify([]), 200

            # 2. Return the list of dictionaries (from RealDictCursor)
            return jsonify(rows), 200

        @api.route("/ebay/inventory/<string:sku>", methods=["GET"])
        def ebay_get_inventory_item(sku):
            """
            Directly fetch a single eBay inventory item by SKU using the EbayInterface.
            This does NOT touch the local Item table; it's a thin proxy to eBay.

            Response:
              200: JSON payload from eBay (via EbayInterface._request)
              502: Error talking to eBay
              503: eBay integration not configured
            """
            if not getattr(self, "ebay", None):
                return jsonify({"error": "eBay integration not configured"}), 503

            try:
                # Assuming EbayInterface._request(path=...) talks to the Sell Inventory API
                data = self.ebay._request("GET", f"/inventory_item/{sku}")
                return jsonify(data), 200
            except EbayAPIError as e:
                return jsonify({"error": str(e)}), 502

        @api.route("/ebay/inventory/<string:sku>", methods=["POST", "PUT"])
        def ebay_upsert_inventory_item(sku):
            """
            Create or update an eBay inventory item for the given SKU.

            Expected JSON body (example):
            {
              "title": "My Item",
              "description": "Some description",
              "category": "Electronics",
              "quantity": 5,
              "price": 19.99
            }

            This builds an item_dict compatible with EbayInterface.sync_item_create_or_update.
            """
            if not getattr(self, "ebay", None):
                return jsonify({"error": "eBay integration not configured"}), 503

            data = request.get_json(force=True) or {}

            # Build the generic item_dict we’ve been using everywhere for marketplace sync
            item_dict = {
                "item_id": data.get("item_id"),  # optional, for local reference
                "sku": sku,
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "category": data.get("category", ""),
                "quantity": data.get("quantity", 0),
                "price": str(data.get("price", "0.00")),
            }

            try:
                ebay_result = self.ebay.sync_item_create_or_update(item_dict)
                return jsonify(
                    {
                        "message": "eBay inventory item upserted",
                        "sku": sku,
                        "ebay_response": ebay_result,
                    }
                ), 200
            except EbayAPIError as e:
                return jsonify(
                    {
                        "error": f"Failed to upsert eBay inventory item for SKU {sku}",
                        "details": str(e),
                    }
                ), 502

        @api.route("/ebay/inventory/<string:sku>", methods=["DELETE"])
        def ebay_delete_inventory_item(sku):
            """
            Delete an eBay inventory item by SKU.

            This delegates to EbayInterface.sync_item_delete and does not
            remove anything from the local Item table.
            """
            if not getattr(self, "ebay", None):
                return jsonify({"error": "eBay integration not configured"}), 503

            try:
                # Our sync_item_delete helper expects a dict with at least 'sku'
                self.ebay.sync_item_delete({"sku": sku})
                return jsonify(
                    {
                        "message": f"eBay inventory item with SKU {sku} deleted",
                        "ebay_sync": "ok",
                    }
                ), 200
            except EbayAPIError as e:
                return jsonify(
                    {
                        "error": f"Failed to delete eBay inventory item with SKU {sku}",
                        "details": str(e),
                        "ebay_sync": "failed",
                    }
                ), 502