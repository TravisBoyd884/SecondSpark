# test_routes_organized.py

import requests
import time
import json
import random
from datetime import datetime

# --- Configuration ---
BASE_URL = "http://localhost:5000"  # Assuming your blueprint is registered at /api
HEADERS = {"Content-Type": "application/json"}

# Global variable to store IDs for dependent tests
TEST_DATA = {
    # Existing IDs from schema.sql for read tests
    "EXISTING_USER_ID": 1,
    "EXISTING_ITEM_ID": 1, 
    "EXISTING_ORG_ID": 1,
    "EXISTING_TRANSACTION_ID": 1,

    # IDs for new objects created during tests
    "new_org_id": None,
    "new_item_id": None,
    "new_transaction_id": None,
    "new_transaction_item_id": None
}

# --- Helper Function (Copied from previous context for completeness) ---

def run_test(name, method, url, data=None, expected_status=200):
    """
    Executes an API request and prints the result.
    Returns the JSON response data or None on failure.
    """
    print(f"\n--- Running Test: {name} ---")
    try:
        if method == 'GET':
            response = requests.get(url, headers=HEADERS)
        elif method == 'POST':
            response = requests.post(url, headers=HEADERS, data=json.dumps(data))
        elif method == 'PUT':
            response = requests.put(url, headers=HEADERS, data=json.dumps(data))
        elif method == 'PATCH':
            response = requests.patch(url, headers=HEADERS, data=json.dumps(data))
        elif method == 'DELETE':
            response = requests.delete(url, headers=HEADERS)
        else:
            print(f"[FAIL] Invalid HTTP method: {method}")
            return None

        status_match = response.status_code == expected_status
        print(f"[{'PASS' if status_match else 'FAIL'}] {method} {url}")
        print(f"Status: {response.status_code} (Expected: {expected_status})")

        try:
            res_data = response.json()
            if not status_match:
                 print(f"Response: {res_data}")
            elif status_match and method != 'DELETE':
                 print(f"Success Payload: {res_data}")
            return res_data
        except json.JSONDecodeError:
            print(f"[ERROR] Could not decode JSON response: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print(f"[FATAL] Could not connect to {BASE_URL}. Is the Flask app running?")
        return None
    except Exception as e:
        print(f"[FATAL] An unexpected error occurred: {e}")
        return None


# ======================================================================
# 1. AUTHENTICATION TEST
# ======================================================================

def test_auth():
    print("\n\n#####################################################")
    print("## 🔐 AUTHENTICATION TEST")
    print("#####################################################")

    login_data = {
        "username": "alice", # Assuming this user exists in schema.sql
        "password": "pass123"
    }

    res = run_test("POST Login (Success)", 'POST', f"{BASE_URL}/login", 
             data=login_data, expected_status=200)

    if res and res.get('user') and res['user'].get('user_id'):
        print(f"[INFO] Alice's user_id: {res['user']['user_id']}")
        # Store for item creation dependency
        TEST_DATA["EXISTING_USER_ID"] = res['user']['user_id']
    else:
        # If login fails, subsequent tests will likely fail, so we exit early
        print("[FATAL] Login failed. Cannot proceed with dependent tests.")
        exit()
    
    # Negative test
    run_test("POST Login (Failure)", 'POST', f"{BASE_URL}/login", 
             data={"username": "alice", "password": "wrong_password"}, expected_status=401)


# ======================================================================
# 2. ORGANIZATION CRUD TESTS
# ======================================================================

def test_organization_crud():
    print("\n\n#####################################################")
    print("## 🏢 ORGANIZATION CRUD TESTS")
    print("#####################################################")
    
    # POST /organizations
    org_name = f"TestOrg-{random.randint(1000, 9999)}"
    post_data = {"name": org_name}
    res = run_test("POST Create Organization", 'POST', f"{BASE_URL}/organizations", 
             data=post_data, expected_status=201)
    
    if res and res.get('organization_id'):
        TEST_DATA["new_org_id"] = res['organization_id']
        print(f"[INFO] New Organization ID: {TEST_DATA['new_org_id']}")
    else:
        print("[FATAL] Failed to create organization. Cannot proceed with CRUD.")
        return

    # GET /organizations/<id>
    run_test(f"GET Organization {TEST_DATA['new_org_id']} Details", 'GET', 
             f"{BASE_URL}/organizations/{TEST_DATA['new_org_id']}")

    # GET /organizations
    run_test("GET All Organizations", 'GET', f"{BASE_URL}/organizations")

    # PUT /organizations/<id>
    updated_name = f"{org_name}-Updated"
    put_data = {"name": updated_name}
    run_test(f"PUT Update Organization {TEST_DATA['new_org_id']}", 'PUT', 
             f"{BASE_URL}/organizations/{TEST_DATA['new_org_id']}", data=put_data, expected_status=200)

    # DELETE /organizations/<id>
    run_test(f"DELETE Organization {TEST_DATA['new_org_id']}", 'DELETE', 
             f"{BASE_URL}/organizations/{TEST_DATA['new_org_id']}", expected_status=200)


# ======================================================================
# 3. ITEM CRUD & Custom Fetch TESTS
# ======================================================================

def test_item_crud_and_fetch():
    print("\n\n#####################################################")
    print("## 📦 ITEM CRUD & CUSTOM FETCH TESTS")
    print("#####################################################")

    # POST /items
    item_title = f"NewTestItem-{random.randint(1000, 9999)}"
    post_data = {
        "title": item_title,
        "price": 99.99,
        "description": "A new gadget for testing.",
        "category": "Gadgets",
        "list_date": datetime.now().strftime("%Y-%m-%d"),
        "creator_id": TEST_DATA["EXISTING_USER_ID"], 
    }
    res = run_test("POST Create Item", 'POST', f"{BASE_URL}/items", 
             data=post_data, expected_status=201)

    if res and res.get('item_id'):
        TEST_DATA["new_item_id"] = res['item_id']
        print(f"[INFO] New Item ID: {TEST_DATA['new_item_id']}")
    else:
        print("[FATAL] Failed to create item. Cannot proceed with dependent tests.")
        return

    # GET /items/<id>
    run_test(f"GET Item {TEST_DATA['new_item_id']} Details", 'GET', 
             f"{BASE_URL}/items/{TEST_DATA['new_item_id']}")

    # GET /items
    run_test("GET All Items", 'GET', f"{BASE_URL}/items")

    # GET /users/<id>/items (New Custom Route)
    res_items = run_test(f"GET Items for User {TEST_DATA['EXISTING_USER_ID']}", 'GET', 
             f"{BASE_URL}/users/{TEST_DATA['EXISTING_USER_ID']}/items", expected_status=200)
    if res_items and isinstance(res_items, list):
         print(f"[INFO] Fetched {len(res_items)} items for user {TEST_DATA['EXISTING_USER_ID']}")

    res_txs = run_test(f"GET Transactions for Item {TEST_DATA['EXISTING_ITEM_ID']}", 'GET', 
             f"{BASE_URL}/items/{TEST_DATA['EXISTING_ITEM_ID']}/transactions", expected_status=200)
    if res_txs and isinstance(res_txs, list):
         print(f"[INFO] Fetched {len(res_txs)} transactions associated with item {TEST_DATA['EXISTING_ITEM_ID']}")

    # PUT /items/<id>
    updated_title = f"{item_title}-Updated"
    put_data = {
        "title": updated_title,
        "price": 109.99,
        "description": "Updated description.",
        "category": "Updated Gadgets",
        "list_date": "2025-01-01",
        "creator_id": TEST_DATA["EXISTING_USER_ID"] # Required to maintain data integrity
    }
    run_test(f"PUT Update Item {TEST_DATA['new_item_id']}", 'PUT', 
             f"{BASE_URL}/items/{TEST_DATA['new_item_id']}", data=put_data, expected_status=200)


# ======================================================================
# 4. TRANSACTION CRUD & Custom Fetch TESTS
# ======================================================================

def test_item_crud_and_fetch():
    print("\n\n#####################################################")
    print("## 📦 ITEM CRUD & CUSTOM FETCH TESTS")
    print("#####################################################")

    # POST /items
    item_title = f"NewTestItem-{random.randint(1000, 9999)}"
    post_data = {
        "title": item_title,
        "price": 99.99,
        "description": "A new gadget for testing.",
        "category": "Gadgets",
        "list_date": datetime.now().strftime("%Y-%m-%d"),
        "creator_id": TEST_DATA["EXISTING_USER_ID"], 
    }
    res = run_test("POST Create Item", 'POST', f"{BASE_URL}/items", 
             data=post_data, expected_status=201)

    if res and res.get('item_id'):
        TEST_DATA["new_item_id"] = res['item_id']
        print(f"[INFO] New Item ID: {TEST_DATA['new_item_id']}")
    else:
        print("[FATAL] Failed to create item. Cannot proceed with dependent tests.")
        return

    # GET /items/<id>
    run_test(f"GET Item {TEST_DATA['new_item_id']} Details", 'GET', 
             f"{BASE_URL}/items/{TEST_DATA['new_item_id']}")

    # GET /items
    run_test("GET All Items", 'GET', f"{BASE_URL}/items")

    # 👇 NEW ROUTE TEST: GET /users/<id>/items
    res_items = run_test(f"GET Items for User {TEST_DATA['EXISTING_USER_ID']}", 'GET', 
             f"{BASE_URL}/users/{TEST_DATA['EXISTING_USER_ID']}/items", expected_status=200)
    if res_items and isinstance(res_items, list):
         print(f"[INFO] Fetched {len(res_items)} items for user {TEST_DATA['EXISTING_USER_ID']}")
    # 👆 END NEW ROUTE TEST

    # PUT /items/<id>
    updated_title = f"{item_title}-Updated"
    put_data = {
        "title": updated_title,
        "price": 109.99,
        "description": "Updated description.",
        "category": "Updated Gadgets",
        "list_date": "2025-01-01",
        "creator_id": TEST_DATA["EXISTING_USER_ID"] # Required to maintain data integrity
    }
    run_test(f"PUT Update Item {TEST_DATA['new_item_id']}", 'PUT', 
             f"{BASE_URL}/items/{TEST_DATA['new_item_id']}", data=put_data, expected_status=200)


# ======================================================================
# 5. TRANSACTION ITEM LINK TESTS
# ======================================================================

def test_transaction_item_link():
    print("\n\n#####################################################")
    print("## 🔗 TRANSACTION ITEM LINK TESTS")
    print("#####################################################")

    if not TEST_DATA["new_item_id"] or not TEST_DATA["new_transaction_id"]:
        print("[SKIP] Item or Transaction ID missing. Skipping link tests.")
        return

    # POST /transactions/link
    link_data = {
        "item_id": TEST_DATA["new_item_id"],
        "transaction_id": TEST_DATA["new_transaction_id"]
    }
    res = run_test("POST Link Item to Transaction", 'POST', f"{BASE_URL}/transactions/link", 
             data=link_data, expected_status=201)

    if res and res.get('transaction_item_id'):
        TEST_DATA["new_transaction_item_id"] = res['transaction_item_id']
        print(f"[INFO] New Link ID: {TEST_DATA['new_transaction_item_id']}")
    else:
        print("[FATAL] Failed to create link. Cannot proceed with unlink test.")
        return

    # GET /transactions/<id> (Verify the link is included in the transaction details)
    run_test(f"GET Transaction {TEST_DATA['new_transaction_id']} Details (Verify Link)", 'GET', 
             f"{BASE_URL}/transactions/{TEST_DATA['new_transaction_id']}")
    
    # DELETE /transactions/unlink/<id>
    run_test(f"DELETE Unlink Transaction Item {TEST_DATA['new_transaction_item_id']}", 'DELETE', 
             f"{BASE_URL}/transactions/unlink/{TEST_DATA['new_transaction_item_id']}", expected_status=200)


# ======================================================================
# 6. CLEANUP (DELETE Tests)
# ======================================================================

def test_cleanup():
    print("\n\n#####################################################")
    print("## 🧹 CLEANUP (DELETE) TESTS")
    print("#####################################################")

    # Order matters due to foreign key constraints: Transaction -> Item -> Organization
    
    if TEST_DATA["new_transaction_id"]:
        run_test(f"DELETE Transaction {TEST_DATA['new_transaction_id']}", 'DELETE', 
                 f"{BASE_URL}/transactions/{TEST_DATA['new_transaction_id']}", expected_status=200)

    if TEST_DATA["new_item_id"]:
        run_test(f"DELETE Item {TEST_DATA['new_item_id']}", 'DELETE', 
                 f"{BASE_URL}/items/{TEST_DATA['new_item_id']}", expected_status=200)
    
    if TEST_DATA["new_org_id"]:
        run_test(f"DELETE Organization {TEST_DATA['new_org_id']}", 'DELETE', 
                 f"{BASE_URL}/organizations/{TEST_DATA['new_org_id']}", expected_status=200)


# ======================================================================
# MAIN EXECUTION
# ======================================================================

if __name__ == "__main__":
    print("#####################################################")
    print("## STARTING API ROUTE TESTS")
    print("#####################################################")

    test_auth()
    test_organization_crud()
    test_item_crud_and_fetch()
    test_transaction_crud_and_fetch()
    test_transaction_item_link()
    
    # Optional: Run cleanup to remove test data
    # test_cleanup() 
    
    print("\n#####################################################")
    print("## API ROUTE TESTS COMPLETE")
    print("#####################################################")