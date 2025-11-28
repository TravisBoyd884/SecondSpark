import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
import os
import time
import socket

# --- Environment Configuration (Keep as is) ---
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# A function to pause execution untill the database is online
def wait_for_db(timeout=int):
    time.sleep(4)
    start_time = time.time()

    while True:
        try:
            # Note: DB_PORT from env is a string, but socket.create_connection handles it.
            with socket.create_connection((DB_HOST, DB_PORT), timeout=2):
                print(f"[INFO] Database is available at port {DB_PORT}")
                return
        except OSError:
            print(f"[INFO] Waiting for database at {DB_HOST}:{DB_PORT}...")
            time.sleep(1)
            if time.time() - start_time > timeout:
                print("[INFO] Server timeout reached waiting for db!")
                exit()


class ConnectionPool:
    def __init__(self, min_conn, max_conn):
        # Renamed class to follow standard Python capitalization convention
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.db_pool = None

        try:
            self.db_pool = SimpleConnectionPool(
                minconn=self.min_conn,
                maxconn=self.max_conn,
                database=DB_NAME,
                user=DB_USER,
                host=DB_HOST,
                port=DB_PORT,
                password=DB_PASS
            )
            print("[INFO] Successfully connected to database!")
            print(f"[INFO] psycopg2 connection pool initialized with max={self.max_conn} and min={self.min_conn}")
        except Exception as e:
            print(f"[ERROR] Unable to initialize connection pool! [ConnectionPool::__init__]\n Error: {e}")
            exit()

    def get_conn(self):
        try:
            return self.db_pool.getconn()
        except Exception as e:
            print(f"[ERROR] Unable to borrow connection [ConnectionPool::get_conn]\n Error: {e}")
            raise  # Re-raise for the caller to handle
    
    def return_conn(self, conn):
        try:
            self.db_pool.putconn(conn)
        except Exception as e:
            print(f"[ERROR] Unable to return conn to pool! [ConnectionPool::return_conn]\n Error: {e}")
            exit()
    
    def close_pool(self):
        try:
            self.db_pool.closeall()
            print("[INFO] Pool has been closed!")
        except Exception as e:
            print(f"[ERROR] Unable to close conn pool! [ConnectionPool::close_pool]\n Error: {e}")


# Method to load database schema into Postgres container
def load_schema(schema_file_path) -> bool:
    if not os.path.exists(schema_file_path):
        print("[ERROR] Schema file does not exist! [db_interface::load_schema]")
        return False

    conn = None
    curr = None
    try:
        with open(schema_file_path, "r") as file:
            sql_script = file.read()

        # Get connection
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        curr = conn.cursor()
        
        curr.execute(sql_script)
        print(f"[INFO] Schema from '{schema_file_path}' loaded successfully! [db_interface::load_schema]")
        return True
    except psycopg2.Error as e:
        print(f"[ERROR] Schema file from '{schema_file_path}' could not be loaded/read! [db_interface::load_schema] \nError: {e}")
        # Note: autocommit=True means no need for conn.rollback() on error here.
        return False
    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()


class DBInterface:
    def __init__(self):
        # Composition of ConnectionPool object for conn management
        self.pool = ConnectionPool(1, 15)

    # General method for PostgreSQL queries
    def execute_query(self, sql, params=None, fetch_one=False, fetch_all=False, commit=False):
        conn = None
        curr = None
        result = None
        try:
            conn = self.pool.get_conn()
            # Use RealDictCursor to return results as dictionaries (better for Flask/JSON)
            curr = conn.cursor(cursor_factory=RealDictCursor) 
            
            curr.execute(sql, params)
            
            if fetch_all:
                result = curr.fetchall()
            elif fetch_one:
                result = curr.fetchone()

            if commit:
                conn.commit()

        except psycopg2.Error as e:
            print(f"[ERROR] Unable to fulfill transaction! [DBInterface::execute_query]\n Error: {e}")
            if conn and not conn.autocommit:
                conn.rollback()
            raise # Re-raise the exception to the caller
        except Exception as e:
            print(f"[ERROR] General error in transaction! [DBInterface::execute_query]\n Error: {e}")
            if conn and not conn.autocommit:
                conn.rollback()
            raise # Re-raise the exception to the caller
        finally:
            if curr:
                curr.close()
            if conn:
                self.pool.return_conn(conn)

        return result

    # Wrapper for the execute_query method
    def _execute_dml(self, sql, params=None) -> bool:
        """Helper method for DML (INSERT, UPDATE, DELETE) operations that require commit."""
        try:
            self.execute_query(sql, params=params, commit=True)
            return True
        except Exception:
            return False # execute_query already prints the error

    # =======================================================================================
    # Organization CRUD
    # =======================================================================================

    def create_organization(self, name: str) -> bool:
        """Inserts a new organization."""
        sql = "INSERT INTO Organization (name) VALUES (%s);"
        return self._execute_dml(sql, (name,))

    def get_organization_by_id(self, organization_id: int):
        """Retrieves an organization record by its ID."""
        sql = "SELECT organization_id, name FROM Organization WHERE organization_id = %s;"
        return self.execute_query(sql, params=(organization_id,), fetch_one=True)

    def get_all_organizations(self):
        """Retrieves all organization records."""
        sql = "SELECT organization_id, name FROM Organization;"
        return self.execute_query(sql, fetch_all=True)

    def update_organization(self, organization_id: int, new_name: str) -> bool:
        """Updates the name of an existing organization."""
        sql = "UPDATE Organization SET name = %s WHERE organization_id = %s;"
        return self._execute_dml(sql, (new_name, organization_id))

    def delete_organization(self, organization_id: int) -> bool:
        """Deletes an organization record by its ID."""
        sql = "DELETE FROM Organization WHERE organization_id = %s;"
        return self._execute_dml(sql, (organization_id,))

    # =======================================================================================
    # AppUser CRUD
    # =======================================================================================

    def create_app_user(self, username: str, password: str, email: str, organization_id: int = None, organization_role: str = None, ebay_account_id: int = None, etsy_account_id: int = None) -> bool:
        """Inserts a new user into the AppUser table."""
        sql = "INSERT INTO AppUser (username, password, email, organization_id, organization_role, ebay_account_id, etsy_account_id) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        params = (username, password, email, organization_id, organization_role, ebay_account_id, etsy_account_id)
        return self._execute_dml(sql, params)

    def get_app_user_by_id(self, user_id: int):
        """Retrieves an AppUser record by their ID."""
        sql = "SELECT * FROM AppUser WHERE user_id = %s;"
        return self.execute_query(sql, params=(user_id,), fetch_one=True)
    
    def get_app_user_by_username(self, username: str):
        """Retrieves an AppUser record by their username."""
        sql = "SELECT * FROM AppUser WHERE username = %s;"
        return self.execute_query(sql, params=(username,), fetch_one=True)

    def get_all_app_users(self):
        """Retrieves all AppUser records (Be cautious with security)."""
        sql = "SELECT user_id, username, email, organization_id, organization_role FROM AppUser;"
        return self.execute_query(sql, fetch_all=True)

    def update_app_user(self, user_id: int, password: str, email: str, organization_id: int, organization_role: str, ebay_account_id: int = None, etsy_account_id: int = None) -> bool:
        """Updates all mutable details of an existing AppUser."""
        sql = "UPDATE AppUser SET password = %s, email = %s, organization_id = %s, organization_role = %s, ebay_account_id = %s, etsy_account_id = %s WHERE user_id = %s;"
        params = (password, email, organization_id, organization_role, ebay_account_id, etsy_account_id, user_id)
        return self._execute_dml(sql, params)

    def delete_app_user(self, user_id: int) -> bool:
        """Deletes an AppUser record by its ID."""
        sql = "DELETE FROM AppUser WHERE user_id = %s;"
        return self._execute_dml(sql, (user_id,))

    # =======================================================================================
    # Item CRUD
    # =======================================================================================

    def create_item(self, title: str, price: float, description: str, category: str, list_date: str, creator_id: int) -> bool:
        """Inserts a new item into the Item table."""
        # Note: PostgreSQL MONEY type should accept float from Python.
        sql = "INSERT INTO Item (title, price, description , category, list_date, creator_id) VALUES (%s, %s, %s, %s, %s, %s);"
        params = (title, price, description, category, list_date, creator_id)
        return self._execute_dml(sql, params)

    def get_item_by_id(self, item_id: int):
        """Retrieves an item record by its ID."""
        sql = "SELECT * FROM Item WHERE item_id = %s;"
        return self.execute_query(sql, params=(item_id,), fetch_one=True)
    
    def get_all_items(self):
        """Retrieves all records from the Item table."""
        sql = "SELECT * FROM Item;"
        return self.execute_query(sql, fetch_all=True)

    def get_all_items_by_appuser_id(self, user_id: int):
        """Retrieves all Item records created by the specified AppUser (user_id is mapped to creator_id)."""
        sql = "SELECT item_id, title, price, description, category, list_date, creator_id FROM Item WHERE creator_id = %s;"
        return self.execute_query(sql, params=(user_id,), fetch_all=True)

    def update_item(self, item_id: int, title: str, price: float, description: str, category: str, list_date: str) -> bool:
        """Updates all mutable details of an existing item."""
        sql = "UPDATE Item SET title = %s, price = %s, description = %s, category = %s, list_date = %s WHERE item_id = %s;"
        params = (title, price, description, category, list_date, item_id)
        return self._execute_dml(sql, params)

    def delete_item(self, item_id: int) -> bool:
        """Deletes an item record by its ID."""
        sql = "DELETE FROM Item WHERE item_id = %s;"
        return self._execute_dml(sql, (item_id,))

    # =======================================================================================
    # AppTransaction CRUD
    # =======================================================================================

    def create_app_transaction(self, sale_date: str, total: float, tax: float, seller_comission: float, seller_id: int) -> bool:
        """Inserts a new transaction into the AppTransaction table."""
        sql = "INSERT INTO AppTransaction (sale_date, total, tax, seller_comission, seller_id) VALUES (%s, %s, %s, %s, %s);"
        params = (sale_date, total, tax, seller_comission, seller_id)
        return self._execute_dml(sql, params)

    def get_app_transaction_by_id(self, transaction_id: int):
        """Retrieves a transaction record by its ID."""
        sql = "SELECT * FROM AppTransaction WHERE transaction_id = %s;"
        return self.execute_query(sql, params=(transaction_id,), fetch_one=True)
    
    def get_all_app_transactions(self):
        """Retrieves all AppTransaction records."""
        sql = "SELECT * FROM AppTransaction;"
        return self.execute_query(sql, fetch_all=True)

    def update_app_transaction(self, transaction_id: int, sale_date: str, total: float, tax: float, seller_comission: float, seller_id: int) -> bool:
        """Updates all details of an existing transaction."""
        sql = "UPDATE AppTransaction SET sale_date = %s, total = %s, tax = %s, seller_comission = %s, seller_id = %s WHERE transaction_id = %s;"
        params = (sale_date, total, tax, seller_comission, seller_id, transaction_id)
        return self._execute_dml(sql, params)

    def delete_app_transaction(self, transaction_id: int) -> bool:
        """Deletes a transaction record by its ID."""
        sql = "DELETE FROM AppTransaction WHERE transaction_id = %s;"
        return self._execute_dml(sql, (transaction_id,))

    # =======================================================================================
    # AppTransaction_Item CRUD (Link Table)
    # =======================================================================================

    def create_app_transaction_item(self, item_id: int, transaction_id: int) -> bool:
        """Links an item to a transaction."""
        sql = "INSERT INTO AppTransaction_Item (item_id, transaction_id) VALUES (%s, %s);"
        return self._execute_dml(sql, (item_id, transaction_id))

    def get_app_transaction_item_by_id(self, transaction_item_id: int):
        """Retrieves a link record by its ID."""
        sql = "SELECT * FROM AppTransaction_Item WHERE transaction_item_id = %s;"
        return self.execute_query(sql, params=(transaction_item_id,), fetch_one=True)
    
    def get_all_app_transaction_items(self):
        """Retrieves all AppTransaction_Item records."""
        sql = "SELECT * FROM AppTransaction_Item;"
        return self.execute_query(sql, fetch_all=True)

    def update_app_transaction_item(self, transaction_item_id: int, new_item_id: int, new_transaction_id: int) -> bool:
        """Updates the item and transaction linked in a transaction_item record."""
        sql = "UPDATE AppTransaction_Item SET item_id = %s, transaction_id = %s WHERE transaction_item_id = %s;"
        params = (new_item_id, new_transaction_id, transaction_item_id)
        return self._execute_dml(sql, params)

    def delete_app_transaction_item(self, transaction_item_id: int) -> bool:
        """Deletes a link record."""
        sql = "DELETE FROM AppTransaction_Item WHERE transaction_item_id = %s;"
        return self._execute_dml(sql, (transaction_item_id,))

    def get_app_transactions_by_item_id(self, item_id: int):
        """Retrieves all AppTransaction records associated with the specified item_id via AppTransaction_Item."""
        sql = """
            SELECT
                t.transaction_id, t.sale_date, t.total, t.tax, t.seller_comission, t.seller_id
            FROM
                AppTransaction t
            JOIN
                AppTransaction_Item ati ON t.transaction_id = ati.transaction_id
            WHERE
                ati.item_id = %s;
        """
        return self.execute_query(sql, params=(item_id,), fetch_all=True)

    # =======================================================================================
    # Ebay CRUD
    # =======================================================================================

    def create_ebay_account(self, user_id: int, client_id: str = None, client_secret: str = None, environment: str = 'sandbox') -> int or None:
        """Inserts a new Ebay account and returns its ID."""
        sql = "INSERT INTO Ebay (user_id, client_id, client_secret, environment) VALUES (%s, %s, %s, %s) RETURNING account_id;"
        params = (user_id, client_id, client_secret, environment)
        result = self.execute_query(sql, params, fetch_one=True, commit=True)
        return result['account_id'] if result else None

    def get_ebay_account_by_id(self, account_id: int):
        """Retrieves an Ebay account record by its ID."""
        sql = "SELECT * FROM Ebay WHERE account_id = %s;"
        return self.execute_query(sql, params=(account_id,), fetch_one=True)
    
    def get_all_ebay_accounts(self):
        """Retrieves all Ebay account records."""
        sql = "SELECT * FROM Ebay;"
        return self.execute_query(sql, fetch_all=True)

    def update_ebay_account(self, account_id: int, client_id: str, client_secret: str, environment: str) -> bool:
        """Updates client details of an existing Ebay account."""
        sql = "UPDATE Ebay SET client_id = %s, client_secret = %s, environment = %s WHERE account_id = %s;"
        params = (client_id, client_secret, environment, account_id)
        return self._execute_dml(sql, params)

    def delete_ebay_account(self, account_id: int) -> bool:
        """Deletes an Ebay account record by its ID."""
        sql = "DELETE FROM Ebay WHERE account_id = %s;"
        return self._execute_dml(sql, (account_id,))

    # =======================================================================================
    # Etsy CRUD
    # =======================================================================================

    def create_etsy_account(self, user_id: int, client_id: str = None, client_secret: str = None, environment: str = None) -> int or None:
        """Inserts a new Etsy account and returns its ID."""
        sql = "INSERT INTO Etsy (user_id, client_id, client_secret, environment) VALUES (%s, %s, %s, %s) RETURNING account_id;"
        params = (user_id, client_id, client_secret, environment)
        result = self.execute_query(sql, params, fetch_one=True, commit=True)
        return result['account_id'] if result else None

    def get_etsy_account_by_id(self, account_id: int):
        """Retrieves an Etsy account record by its ID."""
        sql = "SELECT * FROM Etsy WHERE account_id = %s;"
        return self.execute_query(sql, params=(account_id,), fetch_one=True)
    
    def get_all_etsy_accounts(self):
        """Retrieves all Etsy account records."""
        sql = "SELECT * FROM Etsy;"
        return self.execute_query(sql, fetch_all=True)

    def update_etsy_account(self, account_id: int, client_id: str, client_secret: str, environment: str) -> bool:
        """Updates client details of an existing Etsy account."""
        sql = "UPDATE Etsy SET client_id = %s, client_secret = %s, environment = %s WHERE account_id = %s;"
        params = (client_id, client_secret, environment, account_id)
        return self._execute_dml(sql, params)

    def delete_etsy_account(self, account_id: int) -> bool:
        """Deletes an Etsy account record by its ID."""
        sql = "DELETE FROM Etsy WHERE account_id = %s;"
        return self._execute_dml(sql, (account_id,))
    
    # =======================================================================================
    # EbayItem CRUD
    # =======================================================================================

    def create_ebay_item(self, sku: str, item_id: int, quantity: int, ebay_item_id: str, ebay_offer_id: str, ebay_listing_id: str, ebay_status: str, last_synced_at: str, source_of_truth: str, ebay_account_id: int) -> bool:
        """Inserts a new EbayItem."""
        sql = "INSERT INTO EbayItem (sku, item_id, quantity, ebay_item_id, ebay_offer_id, ebay_listing_id, ebay_status, last_synced_at, source_of_truth, ebay_account_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        params = (sku, item_id, quantity, ebay_item_id, ebay_offer_id, ebay_listing_id, ebay_status, last_synced_at, source_of_truth, ebay_account_id)
        return self._execute_dml(sql, params)

    def get_ebay_item_by_sku(self, sku: str):
        """Retrieves an EbayItem record by its SKU (Primary Key)."""
        sql = "SELECT * FROM EbayItem WHERE sku = %s;"
        return self.execute_query(sql, params=(sku,), fetch_one=True)
    
    def get_all_ebay_items(self):
        """Retrieves all EbayItem records."""
        sql = "SELECT * FROM EbayItem;"
        return self.execute_query(sql, fetch_all=True)

    def update_ebay_item(self, sku: str, quantity: int, ebay_status: str, last_synced_at: str, source_of_truth: str) -> bool:
        """Updates mutable details of an existing EbayItem."""
        sql = "UPDATE EbayItem SET quantity = %s, ebay_status = %s, last_synced_at = %s, source_of_truth = %s WHERE sku = %s;"
        params = (quantity, ebay_status, last_synced_at, source_of_truth, sku)
        return self._execute_dml(sql, params)

    def delete_ebay_item(self, sku: str) -> bool:
        """Deletes an EbayItem record by its SKU."""
        sql = "DELETE FROM EbayItem WHERE sku = %s;"
        return self._execute_dml(sql, (sku,))

    # =======================================================================================
    # EtsyItem CRUD
    # =======================================================================================

    def create_etsy_item(self, sku: str, item_id: int, quantity: int, etsy_account_id: int) -> bool:
        """Inserts a new EtsyItem."""
        sql = "INSERT INTO EtsyItem (sku, item_id, quantity, etsy_account_id) VALUES (%s, %s, %s, %s);"
        params = (sku, item_id, quantity, etsy_account_id)
        return self._execute_dml(sql, params)

    def get_etsy_item_by_sku(self, sku: str):
        """Retrieves an EtsyItem record by its SKU (Primary Key)."""
        sql = "SELECT * FROM EtsyItem WHERE sku = %s;"
        return self.execute_query(sql, params=(sku,), fetch_one=True)
    
    def get_all_etsy_items(self):
        """Retrieves all EtsyItem records."""
        sql = "SELECT * FROM EtsyItem;"
        return self.execute_query(sql, fetch_all=True)

    def update_etsy_item(self, sku: str, quantity: int) -> bool:
        """Updates mutable details of an existing EtsyItem."""
        sql = "UPDATE EtsyItem SET quantity = %s WHERE sku = %s;"
        params = (quantity, sku)
        return self._execute_dml(sql, (quantity, sku))

    def delete_etsy_item(self, sku: str) -> bool:
        """Deletes an EtsyItem record by its SKU."""
        sql = "DELETE FROM EtsyItem WHERE sku = %s;"
        return self._execute_dml(sql, (sku,))

    # =======================================================================================
    # Custom Retrieval Methods
    # =======================================================================================

    def get_all_items_by_appuser_id(self, user_id: int):
        """
        Retrieves all Item records created by the specified AppUser.
        This directly relates to the fk_item_creator constraint.
        """
        sql = """
            SELECT 
                item_id, title, price, description, category, list_date, creator_id
            FROM 
                Item
            WHERE 
                creator_id = %s
            ORDER BY
                list_date DESC;
        """
        return self.execute_query(sql, params=(user_id,), fetch_all=True)

    def get_app_transactions_by_seller_id(self, seller_id: int):
        """
        Retrieves all AppTransaction records sold by the specified AppUser.
        """
        sql = """
            SELECT 
                transaction_id, sale_date, total, tax, seller_comission
            FROM 
                AppTransaction
            WHERE 
                seller_id = %s
            ORDER BY
                sale_date DESC;
        """
        return self.execute_query(sql, params=(seller_id,), fetch_all=True)

    # --- Utility Methods (Keep as is) ---
    def validate_user_credentials(self, username: str, password: str) -> int or None:
        """
        [INSECURE] Validates raw username and password against the database. 
        Returns: user_id (int) if valid, None otherwise.
        """
        # Note: This is fine for a raw password example, but should use hashing in a production app.
        sql = "SELECT user_id FROM AppUser WHERE username = %s AND password = %s;"
        result = self.execute_query(sql, params=(username, password), fetch_one=True)
        return result['user_id'] if result else None

    def get_user_id_by_username(self, username: str) -> int or None:
        """Retrieves the user_id from the AppUser table using their username."""
        sql = "SELECT user_id FROM AppUser WHERE username = %s;"
        result = self.execute_query(sql, params=(username,), fetch_one=True)
        return result['user_id'] if result else None