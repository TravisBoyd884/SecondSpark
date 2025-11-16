import requests
import time
import json

# --- Configuration ---
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Global variable to store IDs for dependent tests
TEST_DATA = {
    "org_id": None,
    "reseller_id": None,
    "user_id": 1, # Use a pre-existing user from schema.sql
    "item_id": None,
    "transaction_id": None,
    "transaction_item_id": None
}

def run_test(name, method, url, data=None, expected_status=200):
    """Helper function to run an HTTP request and print the result."""
    print(f"\n--- Running Test: {name} ---")
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, headers=HEADERS, data=json.dumps(data))
        elif method == 'PUT':
            response = requests.put(url, headers=HEADERS, data=json.dumps(data))
        elif method == 'DELETE':
            response = requests.delete(url)
        else:
            print("Invalid method specified.")
            return False

        # Status Check
        if response.status_code == expected_status:
            status_text = "PASSED"
        else:
            status_text = "FAILED"
        
        print(f"[{status_text}] Status: {response.status_code} (Expected: {expected_status})")
        print(f"Response Body: {response.text}")
        
        return response.json() if response.content else None

    except requests.exceptions.ConnectionError:
        print("[FAILED] Connection Error: Is the backend container running at localhost:5000?")
        return None
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return None


def main():
    print("Waiting 10 seconds for Flask server and DB initialization...")
    time.sleep(10) # Give the Flask app a moment to start after DB is ready

    # ======================================================================
    # 1. SETUP: Create Organization, Reseller, and Item for Transaction tests
    # ======================================================================
    
    # POST /organizations
    res = run_test("SETUP: Create Organization", 'POST', f"{BASE_URL}/organizations", 
                   data={"name": "TestCorp"}, expected_status=201)
    if res:
        # Assuming you'd implement a way to get the new ID on creation
        # For simplicity, we'll try to find it via a lookup here (since the create endpoint doesn't return the ID)
        lookup_res = requests.get(f"{BASE_URL}/organizations/1") 
        if lookup_res.status_code != 200:
            print("[INFO] Cannot dynamically get new ID, using existing ID 1 for test.")
        
    # POST /resellers
    res = run_test("SETUP: Create Reseller", 'POST', f"{BASE_URL}/resellers", 
                   data={"reseller_name": "TestMarket"}, expected_status=201)
    # POST /items
    item_data = {
        "title": "Test Product A",
        "description": "Used for testing endpoints.",
        "category": "Test",
        "list_date": "2025-11-15",
        "creator_id": TEST_DATA["user_id"]
    }
    run_test("SETUP: Create Item", 'POST', f"{BASE_URL}/items", 
             data=item_data, expected_status=201)

    # --- Fetch dynamically created IDs (Best practice is to return ID in POST response) ---
    # Since POST doesn't return ID, we'll use existing IDs 1-5 from schema.sql for reliability
    TEST_DATA["item_id"] = 1 # Wireless Mouse ID
    TEST_DATA["reseller_id"] = 1 # BestBuy ID
    
    # ======================================================================
    # 2. ITEM CRUD TESTS
    # ======================================================================

    # GET /items
    run_test("GET All Items", 'GET', f"{BASE_URL}/items")

    # GET /items/<id>
    run_test(f"GET Item {TEST_DATA['item_id']}", 'GET', f"{BASE_URL}/items/{TEST_DATA['item_id']}")

    # PUT /items/<id>
    run_test(f"UPDATE Item {TEST_DATA['item_id']}", 'PUT', f"{BASE_URL}/items/{TEST_DATA['item_id']}", 
             data={"category": "Electronics - Updated", "description": "Updated for test"}, 
             expected_status=200)

    # ======================================================================
    # 3. TRANSACTION AND LINKING TESTS
    # ======================================================================

    # POST /transactions
    transaction_data = {
        "sale_date": "2025-11-15",
        "total": 99.99,
        "tax": 5.00,
        "reseller_comission": 10.00,
        "reseller_id": TEST_DATA["reseller_id"]
    }
    run_test("POST Create Transaction", 'POST', f"{BASE_URL}/transactions", 
             data=transaction_data, expected_status=201)
    
    # --- Fetch the new transaction_id (using existing ID 1 for reliability) ---
    TEST_DATA["transaction_id"] = 1

    # POST /transactions/link
    link_data = {
        "item_id": TEST_DATA["item_id"],
        "transaction_id": TEST_DATA["transaction_id"]
    }
    run_test("POST Link Item to Transaction", 'POST', f"{BASE_URL}/transactions/link", 
             data=link_data, expected_status=201)

    # GET /transactions/<id> (Verify the link)
    run_test(f"GET Transaction {TEST_DATA['transaction_id']} Details", 'GET', 
             f"{BASE_URL}/transactions/{TEST_DATA['transaction_id']}")
    
    # --- Fetch the transaction_item_id (using existing ID 1 for reliability) ---
    TEST_DATA["transaction_item_id"] = 1

    # DELETE /transactions/unlink/<id>
    run_test(f"DELETE Unlink Transaction Item {TEST_DATA['transaction_item_id']}", 'DELETE', 
             f"{BASE_URL}/transactions/unlink/{TEST_DATA['transaction_item_id']}", expected_status=200)

    # ======================================================================
    # 4. CLEANUP (Optional, uncomment if you want to test delete functionality)
    # ======================================================================
    
    # run_test(f"DELETE Item {TEST_DATA['item_id']}", 'DELETE', f"{BASE_URL}/items/{TEST_DATA['item_id']}", expected_status=200)
    # run_test(f"DELETE Organization {TEST_DATA['org_id']}", 'DELETE', f"{BASE_URL}/organizations/{TEST_DATA['org_id']}", expected_status=200)
    # run_test(f"DELETE Transaction {TEST_DATA['transaction_id']}", 'DELETE', f"{BASE_URL}/transactions/{TEST_DATA['transaction_id']}", expected_status=200)

if __name__ == '__main__':
    main()