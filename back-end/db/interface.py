import psycopg2
from psycopg2 import OperationalError, Error
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, ID3

import os
import time
import socket

# Get envirnment variables from linux container
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
            with socket.create_connection((DB_HOST, DB_PORT), timeout=2):
                print(f"[INFO] Database is available at port {DB_PORT}")
                return
        except OSError:
            print(f"[INFO] Waiting for database at {DB_HOST}:{DB_PORT}...")
            time.sleep(1)
            if time.time() - start_time > timeout:
                print("[INFO] Server timeout reached waiting for db!")
                exit()


class conn_pool(object):
    def __init__(self, min_conn, max_conn): # Take max and min db connections as parameter
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
            print(f"[ERROR] Unable to initialize connection pool! [conn_pool::__init__]\n Error: {e}")
            exit()

    def get_conn(self): # Borrow a connection from the pool
        try:
            return self.db_pool.getconn()
        except Exception as e:
            print(f"[ERROR] Unable to borrow connection [conn_pool::get_conn]\n Error: {e}")
            exit()
    
    def return_conn(self, conn):
        try:
            self.db_pool.putconn(conn)
        except Exception as e:
            print(f"[ERROR] Unable to return conn to pool! [conn_pool::return_conn]\n Error: {e}")
            exit()
    
    def close_pool(self):
        try:
            self.db_pool.closeall()
            print("[INFO] Pool has been closed!")
        except Exception as e:
            print(f"[ERROR] Unable to close conn pool! [conn_pool::close_pool]\n Error: {e}")


# Method to load database schema into Postgres container -------------------------------------------------------
def load_schema(schema_file_path) -> bool:
    if not os.path.exists(schema_file_path):
        print("[ERROR] Schema file does not exist! [db_interface::load_schema]")
        return False

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
        conn.autocommit = True  # Schema setup typically needs autocommit
        curr = conn.cursor()
        
        curr.execute(sql_script)
        print(f"[INFO] Schema from '{schema_file_path}' loaded successfully! [db_interface::load_schema]")
        return True
    except psycopg2.Error as e:
        print(f"[ERROR] Schema file from '{schema_file_path}' could not be loaded/read! [db_interface::load_schema] \nError: {e}")
        if not conn.autocommit:
            conn.rollback()
        return False
    finally: # Return the conn after use
        if curr:
            curr.close()
        if conn:
            conn.close()


class db_interface(object):
    def __init__(self):
        # Composition of conn_pool object for conn management
        self.pool = conn_pool(1, 15)

        # Show current directory in container
        print(f"[INFO] Current directory '{os.getcwd()}' [db_interface::__init__]")


    # General method for PostgreSQL queries ------------------------------------------------------------------------
    def execute_query(self, sql, params=None ,fetch_one=False, fetch_all=False, commit=False):
        try:
            result = None
            conn = self.pool.get_conn()
            curr = conn.cursor()
            
            curr.execute(sql, params)
            
            if fetch_all == True and fetch_one == False and commit == False:
                result = curr.fetchall()
            elif fetch_one == True and fetch_all == False and commit == False:
                result = curr.fetchone()
            # If a commit is requested for a DML opteration
            elif commit == True and fetch_all == False and fetch_one == False: 
                conn.commit()
            elif commit == False and fetch_one == False and fetch_all == False:
                pass # For DDL operation or SELECT where fetch is not needed.
            else:  
                print(f"[ERROR] Improper parameter sent to execute_query [db_interface::execute_query]\n Error: {e}")

        except psycopg2.Error as e:
            print(f"[ERROR] Unable fullfill transaction! [db_interface::execute_query]\n Error: {e}")
            conn.rollback()
        except Exception as e:
            print(f"[ERROR] Unable fullfill transaction! [db_interface::execute_query]\n Error: {e}")
            conn.rollback()
        finally:
            if curr:
                curr.close()
            if conn:
                conn.commit()
                self.pool.return_conn(conn)

        return result

    # Wrapper for the execute_query method ---------------------------------------------------------------------

    def _execute_dml(self, sql, params=None) -> bool:
        """Helper method for DML (INSERT, UPDATE, DELETE) operations that require commit."""
        try:
            self.execute_query(sql, params=params, commit=True)
            return True
        except Exception as e:
            # The general error handling is already in execute_query, but this allows for a DML specific catch if needed.
            print(f"[ERROR] DML operation failed. SQL: {sql[:50]}... \n Error: {e}")
            return False
    

    # Organization CRUD ----------------------------------------------------------------------------------------

    def create_organization(self, name: str) -> bool:
        """Inserts a new organization into the Organization table."""
        sql = "INSERT INTO Organization (name) VALUES (%s);"
        return self._execute_dml(sql, (name,))

    def get_organization_by_id(self, organization_id: int):
        """Retrieves an organization record by its ID."""
        sql = "SELECT organization_id, name FROM Organization WHERE organization_id = %s;"
        return self.execute_query(sql, params=(organization_id,), fetch_one=True)

    def update_organization_name(self, organization_id: int, new_name: str) -> bool:
        """Updates the name of an existing organization."""
        sql = "UPDATE Organization SET name = %s WHERE organization_id = %s;"
        return self._execute_dml(sql, (new_name, organization_id))

    def delete_organization(self, organization_id: int) -> bool:
        """Deletes an organization record by its ID."""
        sql = "DELETE FROM Organization WHERE organization_id = %s;"
        return self._execute_dml(sql, (organization_id,))

    # AppUser CRUD ---------------------------------------------------------------------------------------------

    def create_user(self, username: str, password: str, email: str, organization_id: int, organization_role: str) -> bool:
        """Inserts a new user into the AppUser table."""
        sql = "INSERT INTO AppUser (username, password, email, organization_id, organization_role) VALUES (%s, %s, %s, %s, %s);"
        return self._execute_dml(sql, (username, password, email, organization_id, organization_role))

    def get_user_by_username(self, username: str):
        """Retrieves a user record by their username."""
        sql = "SELECT user_id, username, password, email, organization_id, organization_role FROM AppUser WHERE username = %s;"
        return self.execute_query(sql, params=(username,), fetch_one=True)

    def get_user_by_id(self, user_id: int):
        """Retrieves a user record by their ID (including password hash)."""
        # Note: Selects all columns, including password hash (index 2), which is filtered in the Flask endpoint.
        sql = "SELECT user_id, username, password, email, organization_id, organization_role FROM AppUser WHERE user_id = %s;"
        return self.execute_query(sql, params=(user_id,), fetch_one=True)
    
    def update_user_role(self, user_id: int, new_role: str, new_org_id: int = None) -> bool:
        """Updates a user's organization role and optionally their organization."""
        if new_org_id is None:
            sql = "UPDATE AppUser SET organization_role = %s WHERE user_id = %s;"
            return self._execute_dml(sql, (new_role, user_id))
        else:
            sql = "UPDATE AppUser SET organization_role = %s, organization_id = %s WHERE user_id = %s;"
            return self._execute_dml(sql, (new_role, new_org_id, user_id))

    def delete_user(self, user_id: int) -> bool:
        """Deletes a user record by its ID."""
        # Note: Will fail if the user is a creator for any existing Item due to FK constraint.
        sql = "DELETE FROM AppUser WHERE user_id = %s;"
        return self._execute_dml(sql, (user_id,))

    def validate_user_credentials(self, username: str, password: str) -> int or None:
        """
        [INSECURE] Validates raw username and password against the database. 
        Returns: user_id (int) if valid, None otherwise.
        """
        sql = "SELECT user_id FROM AppUser WHERE username = %s AND password = %s;"
        
        # Execute query fetches the single row (user_id,)
        result = self.execute_query(sql, params=(username, password), fetch_one=True)
        
        # Returns the user_id (the first element of the result tuple) or None
        return result[0] if result else None

    # Item CRUD ------------------------------------------------------------------------------------------------

    def create_item(self, title: str, description: str, category: str, list_date: str, creator_id: int) -> bool:
        """Inserts a new item into the Item table."""
        sql = "INSERT INTO Item (title, description, category, list_date, creator_id) VALUES (%s, %s, %s, %s, %s);"
        return self._execute_dml(sql, (title, description, category, list_date, creator_id))

    def get_item_by_id(self, item_id: int):
        """Retrieves an item record by its ID."""
        sql = "SELECT item_id, title, description, category, list_date, creator_id FROM Item WHERE item_id = %s;"
        return self.execute_query(sql, params=(item_id,), fetch_one=True)

    def update_item_details(self, item_id: int, description: str, category: str) -> bool:
        """Updates the description and category of an existing item."""
        sql = "UPDATE Item SET description = %s, category = %s WHERE item_id = %s;"
        return self._execute_dml(sql, (description, category, item_id))

    def delete_item(self, item_id: int) -> bool:
        """Deletes an item record by its ID."""
        # Note: Will fail if the item is linked to any AppTransaction_Item due to FK constraint.
        sql = "DELETE FROM Item WHERE item_id = %s;"
        return self._execute_dml(sql, (item_id,))

    # Reseller CRUD --------------------------------------------------------------------------------------------

    def create_reseller(self, reseller_name: str) -> bool:
        """Inserts a new reseller into the Reseller table."""
        sql = "INSERT INTO Reseller (reseller_name) VALUES (%s);"
        return self._execute_dml(sql, (reseller_name,))

    def get_reseller_by_id(self, reseller_id: int):
        """Retrieves a reseller record by its ID."""
        sql = "SELECT reseller_id, reseller_name FROM Reseller WHERE reseller_id = %s;"
        return self.execute_query(sql, params=(reseller_id,), fetch_one=True)

    def update_reseller_name(self, reseller_id: int, new_name: str) -> bool:
        """Updates the name of an existing reseller."""
        sql = "UPDATE Reseller SET reseller_name = %s WHERE reseller_id = %s;"
        return self._execute_dml(sql, (new_name, reseller_id))

    def delete_reseller(self, reseller_id: int) -> bool:
        """Deletes a reseller record by its ID."""
        # Note: Will fail if the reseller is linked to any AppTransaction due to FK constraint.
        sql = "DELETE FROM Reseller WHERE reseller_id = %s;"
        return self._execute_dml(sql, (reseller_id,))

    # AppTransaction CRUD --------------------------------------------------------------------------------------

    def create_transaction(self, sale_date: str, total: float, tax: float, reseller_comission: float, reseller_id: int) -> bool:
        """Inserts a new transaction into the AppTransaction table."""
        sql = "INSERT INTO AppTransaction (sale_date, total, tax, reseller_comission, reseller_id) VALUES (%s, %s, %s, %s, %s);"
        return self._execute_dml(sql, (sale_date, total, tax, reseller_comission, reseller_id))

    def get_transaction_by_id(self, transaction_id: int):
        """Retrieves a transaction record by its ID."""
        sql = "SELECT transaction_id, sale_date, total, tax, reseller_comission, reseller_id FROM AppTransaction WHERE transaction_id = %s;"
        return self.execute_query(sql, params=(transaction_id,), fetch_one=True)

    def update_transaction_totals(self, transaction_id: int, total: float, tax: float, reseller_comission: float) -> bool:
        """Updates the financial totals of an existing transaction."""
        sql = "UPDATE AppTransaction SET total = %s, tax = %s, reseller_comission = %s WHERE transaction_id = %s;"
        return self._execute_dml(sql, (total, tax, reseller_comission, transaction_id))

    def delete_transaction(self, transaction_id: int) -> bool:
        """Deletes a transaction record by its ID."""
        # Note: Will fail if the transaction is linked to any AppTransaction_Item due to FK constraint.
        sql = "DELETE FROM AppTransaction WHERE transaction_id = %s;"
        return self._execute_dml(sql, (transaction_id,))

    def get_transactions_by_creator_id(self, creator_id: int):
        """
        Retrieves all transactions that include items created by the specified user (creator_id).
        
        Performs a three-way join: AppTransaction <- AppTransaction_Item <- Item <- AppUser.
        """
        sql = """
            SELECT DISTINCT
                t.transaction_id,
                t.sale_date,
                t.total,
                t.tax,
                t.reseller_comission,
                r.reseller_name AS reseller
            FROM
                AppTransaction t
            JOIN
                AppTransaction_Item ati ON t.transaction_id = ati.transaction_id
            JOIN
                Item i ON ati.item_id = i.item_id
            JOIN
                Reseller r ON t.reseller_id = r.reseller_id
            WHERE
                i.creator_id = %s
            ORDER BY
                t.sale_date DESC;
        """
        return self.execute_query(sql, params=(creator_id,), fetch_all=True)

    # AppTransaction_Item CRUD (Link Table) --------------------------------------------------------------------

    def link_item_to_transaction(self, item_id: int, transaction_id: int) -> bool:
        """Links an item to a transaction."""
        sql = "INSERT INTO AppTransaction_Item (item_id, transaction_id) VALUES (%s, %s);"
        return self._execute_dml(sql, (item_id, transaction_id))

    def get_items_for_transaction(self, transaction_id: int):
        """Retrieves all linked items (with item details) for a given transaction ID."""
        sql = """
            SELECT ati.transaction_item_id, i.title, i.description, i.category 
            FROM AppTransaction_Item ati
            JOIN Item i ON ati.item_id = i.item_id
            WHERE ati.transaction_id = %s;
        """
        return self.execute_query(sql, params=(transaction_id,), fetch_all=True)

    def update_transaction_item_link(self, transaction_item_id: int, new_item_id: int) -> bool:
        """Updates the item linked in a transaction_item record."""
        sql = "UPDATE AppTransaction_Item SET item_id = %s WHERE transaction_item_id = %s;"
        return self._execute_dml(sql, (new_item_id, transaction_item_id))

    def unlink_item_from_transaction(self, transaction_item_id: int) -> bool:
        """Deletes a link between an item and a transaction."""
        sql = "DELETE FROM AppTransaction_Item WHERE transaction_item_id = %s;"
        return self._execute_dml(sql, (transaction_item_id,))

    # Primary key lookup methods -------------------------------------------------------------

    def get_organization_id_by_name(self, name: str) -> int or None:
        """Retrieves the organization_id from the Organization table using its name."""
        sql = "SELECT organization_id FROM Organization WHERE name = %s;"
        result = self.execute_query(sql, params=(name,), fetch_one=True)
        return result[0] if result else None

    def get_user_id_by_username(self, username: str) -> int or None:
        """Retrieves the user_id from the AppUser table using their username."""
        sql = "SELECT user_id FROM AppUser WHERE username = %s;"
        result = self.execute_query(sql, params=(username,), fetch_one=True)
        return result[0] if result else None

    def get_item_id_by_title(self, title: str) -> int or None:
        """Retrieves the item_id from the Item table using its title."""
        sql = "SELECT item_id FROM Item WHERE title = %s;"
        result = self.execute_query(sql, params=(title,), fetch_one=True)
        return result[0] if result else None
    
    def get_reseller_id_by_name(self, reseller_name: str) -> int or None:
        """Retrieves the reseller_id from the Reseller table using its name."""
        sql = "SELECT reseller_id FROM Reseller WHERE reseller_name = %s;"
        result = self.execute_query(sql, params=(reseller_name,), fetch_one=True)
        return result[0] if result else None

    def get_transaction_ids_by_date(self, sale_date: str) -> list or None:
        """Retrieves all transaction_ids from AppTransaction using the sale_date."""
        # Returns a list of IDs since dates may not be unique
        sql = "SELECT transaction_id FROM AppTransaction WHERE sale_date = %s;"
        results = self.execute_query(sql, params=(sale_date,), fetch_all=True)
        return [r[0] for r in results] if results else None

    def get_transaction_item_id_by_link(self, item_id: int, transaction_id: int) -> int or None:
        """Retrieves the transaction_item_id using the item_id and transaction_id."""
        sql = "SELECT transaction_item_id FROM AppTransaction_Item WHERE item_id = %s AND transaction_id = %s;"
        result = self.execute_query(sql, params=(item_id, transaction_id), fetch_one=True)
        return result[0] if result else None

    # General Read Methods -------------------------------------------------------------------------------------

    def get_all_items(self):
        """Retrieves all records from the Item table."""
        sql = "SELECT item_id, title, description, category, list_date, creator_id FROM Item;"
        return self.execute_query(sql, fetch_all=True)

    def get_all_organizations(self):
        """Retrieves all records from the Organization table."""
        sql = "SELECT organization_id, name FROM Organization;"
        return self.execute_query(sql, fetch_all=True)

    def get_all_resellers(self):
        """Retrieves all records from the Reseller table."""
        sql = "SELECT reseller_id, reseller_name FROM Reseller;"
        return self.execute_query(sql, fetch_all=True)

    # Note: A 'get_all_users' is usually omitted or protected for security reasons.
    # Note: Listing all transactions might be too slow/large and is usually limited by date/pagination.