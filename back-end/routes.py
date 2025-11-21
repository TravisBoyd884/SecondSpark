# app/routes.py

from flask import Blueprint, request, jsonify, send_from_directory, abort
from db.interface import db_interface  # Our DB interface class

api = Blueprint('api', __name__)  # This stays global

class APIRoutes:
    def __init__(self):
        self.db = db_interface()
        self.register_routes()

    def register_routes(self):

        # ----------------------------------------------------------------------
# 📦 ITEM ENDPOINTS (/items)
        # ----------------------------------------------------------------------

        # CREATE Item
        @api.route('/items', methods=['POST'])
        def create_item():
            data = request.get_json()
            title = data.get("title")
            description = data.get("description")
            category = data.get("category")
            list_date = data.get("list_date")  # e.g., "YYYY-MM-DD"
            creator_id = data.get("creator_id")
            
            if not all([title, creator_id, list_date]):
                return jsonify({"error": "Missing required fields: title, list_date, creator_id"}), 400
            
            success = self.db.create_item(title, description, category, list_date, creator_id)
            
            if success:
                return jsonify({"message": "Item created successfully"}), 201
            return jsonify({"error": "Failed to create item"}), 500

        # READ All Items
        @api.route('/items', methods=['GET'])
        def get_all_items():
            # Assuming you have a get_all_items method in your db_interface
            items = self.db.execute_query("SELECT * FROM Item;", fetch_all=True)
            if items is not None:
                # Need to convert list of tuples to list of dictionaries for proper JSON response
                # Assuming the result is a list of tuples: (item_id, title, description, ...)
                # If using RealDictCursor, this step is simpler.
                
                # For simplicity, returning raw data structure here:
                return jsonify(items), 200
            return jsonify({"message": "No items found"}), 404

        # READ Single Item
        @api.route('/items/<int:item_id>', methods=['GET'])
        def get_item(item_id):
            item = self.db.get_item_by_id(item_id)
            if item:
                return jsonify(item), 200
            return jsonify({"error": f"Item with ID {item_id} not found"}), 404

        # UPDATE Item
        @api.route('/items/<int:item_id>', methods=['PUT'])
        def update_item(item_id):
            data = request.get_json()
            description = data.get("description")
            category = data.get("category")

            if not any([description, category]):
                return jsonify({"error": "Must provide 'description' or 'category' to update"}), 400

            success = self.db.update_item_details(item_id, description, category)

            if success:
                return jsonify({"message": f"Item {item_id} updated successfully"}), 200
            return jsonify({"error": f"Failed to update item {item_id}"}), 500

        # DELETE Item
        @api.route('/items/<int:item_id>', methods=['DELETE'])
        def delete_item(item_id):
            success = self.db.delete_item(item_id)
            if success:
                return jsonify({"message": f"Item {item_id} deleted successfully"}), 200
            return jsonify({"error": f"Failed to delete item {item_id}. Check if it is linked to a transaction."}), 500


        # ----------------------------------------------------------------------
# 🏢 ORGANIZATION ENDPOINTS (/organizations)
        # ----------------------------------------------------------------------
        
        # CREATE Organization
        @api.route('/organizations', methods=['POST'])
        def create_organization():
            name = request.get_json().get("name")
            if not name:
                return jsonify({"error": "Organization name is required"}), 400

            success = self.db.create_organization(name)
            if success:
                return jsonify({"message": "Organization created successfully"}), 201
            return jsonify({"error": "Failed to create organization"}), 500

        # READ Single Organization
        @api.route('/organizations/<int:org_id>', methods=['GET'])
        def get_organization(org_id):
            org = self.db.get_organization_by_id(org_id)
            if org:
                return jsonify(org), 200
            return jsonify({"error": f"Organization with ID {org_id} not found"}), 404
            
        # DELETE Organization
        @api.route('/organizations/<int:org_id>', methods=['DELETE'])
        def delete_organization(org_id):
            success = self.db.delete_organization(org_id)
            if success:
                return jsonify({"message": f"Organization {org_id} deleted successfully"}), 200
            return jsonify({"error": f"Failed to delete organization {org_id}. Check for linked users."}), 500


        # ----------------------------------------------------------------------
# 🏷️ RESELLER ENDPOINTS (/resellers)
        # ----------------------------------------------------------------------
        
        # CREATE Reseller
        @api.route('/resellers', methods=['POST'])
        def create_reseller():
            name = request.get_json().get("reseller_name")
            if not name:
                return jsonify({"error": "Reseller name is required"}), 400

            success = self.db.create_reseller(name)
            if success:
                return jsonify({"message": "Reseller created successfully"}), 201
            return jsonify({"error": "Failed to create reseller"}), 500

        # READ Single Reseller
        @api.route('/resellers/<int:reseller_id>', methods=['GET'])
        def get_reseller(reseller_id):
            reseller = self.db.get_reseller_by_id(reseller_id)
            if reseller:
                return jsonify(reseller), 200
            return jsonify({"error": f"Reseller with ID {reseller_id} not found"}), 404
            
        # DELETE Reseller
        @api.route('/resellers/<int:reseller_id>', methods=['DELETE'])
        def delete_reseller(reseller_id):
            success = self.db.delete_reseller(reseller_id)
            if success:
                return jsonify({"message": f"Reseller {reseller_id} deleted successfully"}), 200
            return jsonify({"error": f"Failed to delete reseller {reseller_id}. Check for linked transactions."}), 500

        
        # ----------------------------------------------------------------------
# 💸 TRANSACTION ENDPOINTS (/transactions)
        # ----------------------------------------------------------------------
        
        # CREATE Transaction
        @api.route('/transactions', methods=['POST'])
        def create_transaction():
            data = request.get_json()
            # sale_date, total, tax, reseller_comission, reseller_id
            required_fields = ["sale_date", "total", "tax", "reseller_comission", "reseller_id"]
            if not all(field in data for field in required_fields):
                return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

            success = self.db.create_transaction(
                data["sale_date"], 
                data["total"], 
                data["tax"], 
                data["reseller_comission"], 
                data["reseller_id"]
            )
            
            if success:
                return jsonify({"message": "Transaction created successfully"}), 201
            return jsonify({"error": "Failed to create transaction"}), 500

        # READ Single Transaction and its associated items
        @api.route('/transactions/<int:transaction_id>', methods=['GET'])
        def get_transaction_details(transaction_id):
            transaction = self.db.get_transaction_by_id(transaction_id)
            if not transaction:
                return jsonify({"error": f"Transaction with ID {transaction_id} not found"}), 404
            
            items = self.db.get_items_for_transaction(transaction_id)
            
            # Combine transaction data with item data
            response_data = {
                "transaction": transaction,
                "items": items if items else []
            }
            return jsonify(response_data), 200


        # ----------------------------------------------------------------------
# 🔗 TRANSACTION ITEM LINKING ENDPOINTS (/transactions/link)
        # ----------------------------------------------------------------------

        # LINK Item to Transaction (Create AppTransaction_Item)
        @api.route('/transactions/link', methods=['POST'])
        def link_transaction_item():
            data = request.get_json()
            item_id = data.get("item_id")
            transaction_id = data.get("transaction_id")

            if not all([item_id, transaction_id]):
                return jsonify({"error": "Both item_id and transaction_id are required"}), 400

            success = self.db.link_item_to_transaction(item_id, transaction_id)
            if success:
                return jsonify({"message": f"Item {item_id} linked to transaction {transaction_id}"}), 201
            return jsonify({"error": "Failed to link item and transaction"}), 500

        # UNLINK Item from Transaction (Delete AppTransaction_Item)
        @api.route('/transactions/unlink/<int:transaction_item_id>', methods=['DELETE'])
        def unlink_transaction_item(transaction_item_id):
            success = self.db.unlink_item_from_transaction(transaction_item_id)
            if success:
                return jsonify({"message": f"Transaction item link {transaction_item_id} removed"}), 200
            return jsonify({"error": f"Failed to remove transaction item link {transaction_item_id}"}), 500


        # ----------------------------------------------------------------------
# 👤 APPUSER ENDPOINTS (/users)
        # ----------------------------------------------------------------------

        # Login 
        @api.route('/login', methods=['POST'])
        def login():
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not all([username, password]):
                return jsonify({"error": "Username and password required"}), 400

            # This method directly checks the raw username and password in the database.
            # This is must be changed for production application
            user_id = self.db.validate_user_credentials(username, password)
            
            if user_id:
                return jsonify({"user_id": user_id, "message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401

        # CREATE / Register User
        @api.route('/users', methods=['POST'])
        def create_app_user():
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            email = data.get("email")
            organization_id = data.get("organization_id")
            organization_role = data.get("organization_role", "User") # Default to 'User'
            
            # Check for required fields
            if not all([username, password, email, organization_id]):
                return jsonify({
                    "error": "Missing required fields: username, password, email, organization_id"
                }), 400
            
            # Call the comprehensive create_user method (assuming it's updated in interface.py)
            success = self.db.create_user(username, password, email, organization_id, organization_role)
            
            if success:
                return jsonify({"message": "User registered successfully"}), 201
            return jsonify({"error": "Failed to register user. Username or email may exist."}), 500

        # READ Single User
        @api.route('/users/<int:user_id>', methods=['GET'])
        def get_app_user(user_id):
            # Requires a simple get_user_by_id in interface.py
            user = self.db.get_user_by_id(user_id)
            
            if user:
                # IMPORTANT: Filter out the password hash before sending to the client!
                user_data = {
                    "user_id": user[0],
                    "username": user[1],
                    "email": user[3],
                    "organization_id": user[4],
                    "organization_role": user[5]
                }
                return jsonify(user_data), 200
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        # UPDATE User Role/Organization
        @api.route('/users/<int:user_id>', methods=['PUT'])
        def update_app_user(user_id):
            data = request.get_json()
            new_role = data.get("organization_role")
            new_org_id = data.get("organization_id")

            if not any([new_role, new_org_id]):
                return jsonify({"error": "Must provide 'organization_role' or 'organization_id' to update"}), 400

            # Use the dedicated update method
            success = self.db.update_user_role(user_id, new_role, new_org_id)

            if success:
                return jsonify({"message": f"User {user_id} updated successfully"}), 200
            return jsonify({"error": f"Failed to update user {user_id}. Check if user or organization exists."}), 500

        # DELETE User
        @api.route('/users/<int:user_id>', methods=['DELETE'])
        def delete_app_user(user_id):
            success = self.db.delete_user(user_id)
            if success:
                return jsonify({"message": f"User {user_id} deleted successfully"}), 200
            # Deletion might fail if the user is linked as a creator to an Item (FK constraint)
            return jsonify({"error": f"Failed to delete user {user_id}. User may be a creator for existing items."}), 500
