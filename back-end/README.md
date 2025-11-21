# Dockerized back-end instructions
### Running the back-end itself
- `docker build -t back-end`
- `docker run -p 5000:5000 back-end .`

### Running the back-end AND database:
- `docker compose up`

# Unit Tests:
- `/tests/test_routes.py` contains unit tests for the python backend.
- *This script is designed to be run while the Postgresql and Python back-end Docker containers are running.* These can be run with the compose file located at `/back-end/docker-compose.yaml`.

# Route Reference for Developers

# API Endpoints Documentation

This document serves as a guide for front-end developers, detailing all available API endpoints, their methods, required data, and expected responses.

All endpoints are prefixed under the `api` Blueprint, which will typically be hosted at a base URL (e.g., `https://api.yourapp.com/`).

---

## User Authentication

### `POST /login`

| Detail | Description |
| :--- | :--- |
| **Purpose** | Authenticates a user and retrieves their ID. |
| **Method** | `POST` |
| **Body (JSON)** | `{"username": "string", "password": "string"}` |
| **Success (200)** | `{"user_id": 1}` |
| **Failure (401)** | `{"error": "Invalid credentials"}` |

---

## Item Endpoints (`/items`)

These endpoints manage the items available in the application.

| Endpoint | Method | Purpose | Body (JSON) | Success Code/Body | Failure Code/Body |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `**POST /items**` | `POST` | Create a new item. | `{"title": "str", "description": "str (opt)", "category": "str (opt)", "list_date": "YYYY-MM-DD", "creator_id": "int"}` | `201`, `{"message": "Item created successfully"}` | `400` (Missing fields), `500` (Failed to create) |
| `**GET /items**` | `GET` | Retrieve **all** items. | *(None)* | `200`, `[{"item_id": 1, "title": "...", ...}, ...]` | `404`, `{"message": "No items found"}` |
| `**GET /items/<int:item_id>**` | `GET` | Retrieve a **single** item by ID. | *(None)* | `200`, `{"item_id": 1, "title": "...", ...}` | `404`, `{"error": "Item with ID X not found"}` |
| `**PUT /items/<int:item_id>**` | `PUT` | Update item details (description/category). | `{"description": "str (opt)", "category": "str (opt)"}` | `200`, `{"message": "Item X updated successfully"}` | `400` (No update fields), `500` (Failed to update) |
| `**DELETE /items/<int:item_id>**` | `DELETE` | Delete an item by ID. | *(None)* | `200`, `{"message": "Item X deleted successfully"}` | `500`, `{"error": "Failed to delete item X. Check if it is linked to a transaction."}` |

---

## Organization Endpoints (`/organizations`)

These endpoints manage organizations.

| Endpoint | Method | Purpose | Body (JSON) | Success Code/Body | Failure Code/Body |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `**POST /organizations**` | `POST` | Create a new organization. | `{"name": "string"}` | `201`, `{"message": "Organization created successfully"}` | `400` (Name required), `500` (Failed to create) |
| `**GET /organizations/<int:org_id>**` | `GET` | Retrieve a single organization by ID. | *(None)* | `200`, `{"org_id": 1, "name": "..."}` | `404`, `{"error": "Organization with ID X not found"}` |
| `**DELETE /organizations/<int:org_id>**` | `DELETE` | Delete an organization by ID. | *(None)* | `200`, `{"message": "Organization X deleted successfully"}` | `500`, `{"error": "Failed to delete organization X. Check for linked users."}` |

---

## Reseller Endpoints (`/resellers`)

These endpoints manage reseller accounts.

| Endpoint | Method | Purpose | Body (JSON) | Success Code/Body | Failure Code/Body |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `**POST /resellers**` | `POST` | Create a new reseller. | `{"reseller_name": "string"}` | `201`, `{"message": "Reseller created successfully"}` | `400` (Name required), `500` (Failed to create) |
| `**GET /resellers/<int:reseller_id>**` | `GET` | Retrieve a single reseller by ID. | *(None)* | `200`, `{"reseller_id": 1, "reseller_name": "..."}` | `404`, `{"error": "Reseller with ID X not found"}` |
| `**DELETE /resellers/<int:reseller_id>**` | `DELETE` | Delete a reseller by ID. | *(None)* | `200`, `{"message": "Reseller X deleted successfully"}` | `500`, `{"error": "Failed to delete reseller X. Check for linked transactions."}` |

---

## Transaction Endpoints (`/transactions`)

These endpoints manage sales transactions.

### `POST /transactions`

| Detail | Description |
| :--- | :--- |
| **Purpose** | Create a new sales transaction. |
| **Method** | `POST` |
| **Body (JSON)** | `{"sale_date": "YYYY-MM-DD", "total": "float", "tax": "float", "reseller_comission": "float", "reseller_id": "int"}` |
| **Success (201)** | `{"message": "Transaction created successfully"}` |
| **Failure (400)** | `{"error": "Missing required fields: sale_date, total, tax, reseller_comission, reseller_id"}` |
| **Failure (500)** | `{"error": "Failed to create transaction"}` |

### `GET /transactions/<int:transaction_id>`

| Detail | Description |
| :--- | :--- |
| **Purpose** | Retrieve a single transaction and all items associated with it. |
| **Method** | `GET` |
| **Success (200)** | `{"transaction": {...}, "items": [{...}, {...}, ...]}` |
| **Failure (404)** | `{"error": "Transaction with ID X not found"}` |

---

## Transaction Item Linking Endpoints (`/transactions/link`)

These endpoints manage the many-to-many relationship between transactions and items.

| Endpoint | Method | Purpose | Body (JSON) | Success Code/Body | Failure Code/Body |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `**POST /transactions/link**` | `POST` | Link an existing item to an existing transaction. (Creates an entry in the intermediate `AppTransaction_Item` table.) | `{"item_id": "int", "transaction_id": "int"}` | `201`, `{"message": "Item X linked to transaction Y"}` | `400` (Missing IDs), `500` (Failed to link) |
| `**DELETE /transactions/unlink/<int:transaction_item_id>**` | `DELETE` | Remove a link between an item and a transaction using the link's ID. | *(None)* | `200`, `{"message": "Transaction item link X removed"}` | `500`, `{"error": "Failed to remove transaction item link X"}` |