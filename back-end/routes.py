# app/routes.py

from flask import Blueprint, request, jsonify, send_from_directory, abort
from db.interface import db_interface  # Our DB interface class

api = Blueprint('api', __name__)  # This stays global

class APIRoutes:
    def __init__(self):
        self.db = db_interface()
        self.register_routes()

    def register_routes(self):
        # Login
        @api.route('/login', methods=['POST'])
        def login():
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            user_id = self.db.get_user_id(username, password)
            if user_id:
                return jsonify({"user_id": user_id}), 200
            return jsonify({"error": "Invalid credentials"}), 401
