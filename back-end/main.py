# flask imports
from flask import Flask
from flask_cors import CORS
from flask import Blueprint, request, jsonify, abort, send_from_directory
from routes import api, APIRoutes

# Imports for database interface
from db.interface import wait_for_db, load_schema
import os

# Constants for file/folder uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Wait for database to initialize before running backend
wait_for_db(40)
if not os.path.exists("db/.setup_done"):
    load_schema("db/schema.sql")
    with open("db/.setup_done", "w") as f:
        f.write("setup complete")
    print("[INFO] Setup complete.")
else:
    print("[INFO] Database already set, skipping setup process.")

# Configure flask app to support file upload/download
def create_app():
    app = Flask(__name__)
    CORS(app)
    APIRoutes()  # Initializes and binds the routes
    # 1. Set the configuration for the upload directory
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # 2. Register your API routes Blueprint
    # You may add url prefix with argument <url_prefix='/api'>
    app.register_blueprint(api)

    # 3. Create the upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Created upload directory: {UPLOAD_FOLDER}")

    # 4. (Optional but recommended) Serve the uploads directory
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        """Allows direct retrieval of uploaded images via URL, e.g., /uploads/my_pic.jpg"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Route to serve a specific image file by name
    @app.route('/images/<filename>')
    def get_uploaded_image(filename):
        """
        Serves the requested file securely from the UPLOAD_FOLDER (static/uploads).
        Example: GET /images/item_1.jpg will look for static/uploads/item_1.jpg.
        """
        # UPLOAD_FOLDER is expected to be configured in app.config (e.g., 'static/uploads')
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)





