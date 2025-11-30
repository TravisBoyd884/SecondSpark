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

def test_register_user():
    """Tests the /api/register route functionality."""
    
    # --- Test 1: Successful Registration ---
    # Use random numbers to ensure unique username and email for each test run
    unique_id = random.randint(10000, 99999) 
    new_user_data = {
        "username": f"test_reg_user_{unique_id}",
        "password": "testpassword123",
        "email": f"test.reg.user.{unique_id}@example.com",
        "organization_id": TEST_DATA["EXISTING_ORG_ID"], # Assuming 1 is a valid ID from schema
    }

    result = run_test(
        "Register New User - SUCCESS",
        'POST',
        f"{BASE_URL}/register",
        data=new_user_data,
        expected_status=201
    )
    
    if result and "user_id" in result:
        print(f"[INFO] Successfully created user with ID: {result['user_id']}")
        # Note: If you add user cleanup to test_cleanup(), you would save the ID here.
        
    # --- Test 2: Missing Required Fields (Missing password) ---
    missing_fields_data = {
        "username": "fail_no_pass",
        "email": "fail@example.com",
        "organization_id": TEST_DATA["EXISTING_ORG_ID"],
    }
    run_test(
        "Register User - FAIL (Missing password)",
        'POST',
        f"{BASE_URL}/register",
        data=missing_fields_data,
        expected_status=400
    )

    # --- Test 3: Non-existent Organization ---
    nonexistent_org_data = {
        "username": "fail_no_org",
        "password": "p",
        "email": "fail_org@example.com",
        "organization_id": 99999,
    }
    run_test(
        "Register User - FAIL (Non-existent Organization ID)",
        'POST',
        f"{BASE_URL}/register",
        data=nonexistent_org_data,
        expected_status=404
    )
    
    # --- Test 4: Duplicate Registration ---
    # Use the same data as the successful test (Test 1). 
    # Since the user was created, the second attempt should fail the unique constraint check.
    if result and "user_id" in result:
        run_test(
            "Register User - FAIL (Duplicate username/email)",
            'POST',
            f"{BASE_URL}/register",
            data=new_user_data,
            expected_status=500 # Route logic returns 500 on DB unique constraint failure
        )

# ======================================================================
# 2. ORGANIZATION CRUD TESTS
# ======================================================================

def test_organization_users_fetch():
    """Tests the /api/organizations/<id>/users route functionality."""
    
    # --- Test 1: Successful Fetch for Organization 1 ---
    org_id = TEST_DATA["EXISTING_ORG_ID"] # Assuming Org 1 has multiple users (alice, bob, carol, dave, eve, etc.)
    
    result = run_test(
        f"Fetch Users for Existing Organization {org_id}",
        'GET',
        f"{BASE_URL}/organizations/{org_id}/users",
        expected_status=200
    )
    
    if result is not None:
        print(f"[INFO] Fetched {len(result)} users for Organization {org_id}.")
        
        # ASSERT 1: Check if we got a list and it has a reasonable size (at least 5 users are in the default schema)
        assert isinstance(result, list), "Result should be a list of users"
        assert len(result) >= 1, f"Expected at least 1 users in Org {org_id}, got {len(result)}"

        # ASSERT 2: Check the structure of the first user object
        first_user = result[0]
        assert "password" not in first_user, "User response should NOT contain the password field"
        assert "user_id" in first_user and isinstance(first_user["user_id"], int), "User object missing 'user_id'"
        assert first_user["organization_id"] == org_id, "User organization ID is incorrect"

    # --- Test 2: Fetch for a Non-Existent Organization ---
    non_existent_org_id = 99999
    run_test(
        f"Fetch Users for Non-Existent Organization {non_existent_org_id}",
        'GET',
        f"{BASE_URL}/organizations/{non_existent_org_id}/users",
        expected_status=404 # Should fail with a 404 since the organization is not found
    )
    
    # --- Test 3: Fetch for an Existing Organization with (Assumed) No Users ---
    # Assuming 'Gamma Trading Co.' (Org 3) exists but may have no users linked after cleanup/reset. 
    # Use the max existing ID + 1 if you cannot reliably get Org ID 3's value
    # Let's assume you've populated your DB with an org that has 0 users for a robust test.
    # For simplicity, we'll assume the Organization ID 2 (Beta Resale Group) has a predictable number of users from the new schema.
    
    org_id_with_users = org_id + 1 # Assuming Org 2 is the next in sequence
    result_org_2 = run_test(
        f"Fetch Users for Organization {org_id_with_users}",
        'GET',
        f"{BASE_URL}/organizations/{org_id_with_users}/users",
        expected_status=200
    )
    
    if result_org_2 is not None:
        # Based on the sample data provided previously (frank, grace, henry), Org 2 (Beta) has 2 users (frank, grace)
        # and Org 3 (Gamma) has 1 user (henry)
        # Let's verify Org 2 has exactly 2 users
        expected_user_count = 1 # Based on the last generated data for Org 'Beta Resale Group'
        assert isinstance(result_org_2, list), "Result for Org 2 should be a list"
        assert len(result_org_2) == expected_user_count, f"Expected {expected_user_count} users in Org {org_id_with_users}, got {len(result_org_2)}"

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

def test_transaction_crud_and_fetch():
    print("\n\n#####################################################")
    print("## 💸 TRANSACTION CRUD & CUSTOM FETCH TESTS")
    print("#####################################################")
    
    # POST /transactions (IMPORTANT: Use 'reseller_id' and 'reseller_comission' for test compatibility)
    post_data = {
        "sale_date": datetime.now().strftime("%Y-%m-%d"),
        "total": 550.00,
        "tax": 35.00,
        "reseller_comission": 25.00, # Maps to seller_comission in DB
        "reseller_id": TEST_DATA["EXISTING_USER_ID"] # Maps to seller_id in DB
    }
    res = run_test("POST Create Transaction", 'POST', f"{BASE_URL}/transactions", 
             data=post_data, expected_status=201)
    
    if res and res.get('transaction_id'):
        TEST_DATA["new_transaction_id"] = res['transaction_id']
        print(f"[INFO] New Transaction ID: {TEST_DATA['new_transaction_id']}")
    else:
        print("[FATAL] Failed to create transaction. Cannot proceed with dependent tests.")
        return

    # GET /transactions/<id>
    run_test(f"GET Transaction {TEST_DATA['new_transaction_id']} Details (No items yet)", 'GET', 
             f"{BASE_URL}/transactions/{TEST_DATA['new_transaction_id']}")

    # GET /users/<id>/transactions (New Custom Route)
    res_txs = run_test(f"GET Transactions for User {TEST_DATA['EXISTING_USER_ID']}", 'GET', 
             f"{BASE_URL}/users/{TEST_DATA['EXISTING_USER_ID']}/transactions", expected_status=200)
    if res_txs and isinstance(res_txs, list):
         print(f"[INFO] Fetched {len(res_txs)} transactions for user {TEST_DATA['EXISTING_USER_ID']}")

    # PUT /transactions/<id>
    put_data = {
        "sale_date": "2025-02-02",
        "total": 600.00,
        "tax": 40.00,
        "reseller_comission": 30.00, # Maps to seller_comission in DB
        "reseller_id": TEST_DATA["EXISTING_USER_ID"] # Maps to seller_id in DB
    }
    run_test(f"PUT Update Transaction {TEST_DATA['new_transaction_id']}", 'PUT', 
             f"{BASE_URL}/transactions/{TEST_DATA['new_transaction_id']}", data=put_data, expected_status=200)

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

    # GET /transactions/<id>/items (New Custom Route)
    res_items = run_test(f"GET Items for Transaction {TEST_DATA['new_transaction_id']}", 'GET', 
             f"{BASE_URL}/transactions/{TEST_DATA['new_transaction_id']}/items", expected_status=200)
    if res_items and isinstance(res_items, list) and len(res_items) > 0:
         print(f"[PASS] Successfully fetched {len(res_items)} items for the new transaction.")
         
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
    test_organization_users_fetch()
    test_transaction_item_link()
    test_register_user()
    
    # Optional: Run cleanup to remove test data
    # test_cleanup() 
    
    print("\n#####################################################")
    print("## API ROUTE TESTS COMPLETE")
    print("#####################################################")