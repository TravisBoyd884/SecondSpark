-- 1. Create the Organization Table
CREATE TABLE Organization (
    organization_id INT PRIMARY KEY,
    name CHAR(50) NOT NULL
);

---

-- 2. Create the User Table
CREATE TABLE AppUser (
    user_id INT PRIMARY KEY,
    username CHAR(50) NOT NULL,
    password CHAR(50) NOT NULL,
    email CHAR(50) NOT NULL,
    organization_id INT,
    organization_role CHAR(50),
    CONSTRAINT fk_organization
        FOREIGN KEY (organization_id)
        REFERENCES Organization(organization_id)
);

---

-- 3. Create the Item Table
CREATE TABLE Item (
    item_id INT PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    category CHAR(50),
    list_date DATE,
    creator_id INT NOT NULL,
    CONSTRAINT fk_creator
        FOREIGN KEY (creator_id)
        REFERENCES AppUser (user_id)
);

---

-- 4. Create the Reseller Table
CREATE TABLE Reseller (
    reseller_id INT PRIMARY KEY,
    reseller_name CHAR(50) NOT NULL
);

---

-- 5. Create the Transaction Table
-- Note: 'MONEY' is a standard PostgreSQL type for currency.
CREATE TABLE AppTransaction (
    transaction_id INT PRIMARY KEY,
    sale_date DATE,
    total MONEY,
    tax MONEY,
    reseller_comission MONEY,
    reseller_id INT NOT NULL,
    CONSTRAINT fk_reseller
        FOREIGN KEY (reseller_id)
        REFERENCES Reseller(reseller_id)
);

---

-- 6. Create the AppTransaction_Item Table
-- A composite primary key could also be used here, but for simplicity based on the ERD, 
-- we'll use a single transaction_item_id as the PK.
CREATE TABLE AppTransaction_Item (
    transaction_item_id INT PRIMARY KEY,
    item_id INT NOT NULL,
    transaction_id INT NOT NULL,
    CONSTRAINT fk_item
        FOREIGN KEY (item_id)
        REFERENCES Item(item_id),
    CONSTRAINT fk_transaction
        FOREIGN KEY (transaction_id)
        REFERENCES AppTransaction (transaction_id)
);


---

--- TEST DATA

-- Insert a test Organization
INSERT INTO Organization (organization_id, name)
VALUES (101, 'TestOrg');

-- Insert a test Reseller
INSERT INTO Reseller (reseller_id, reseller_name)
VALUES (201, 'TestReseller');

---

-- Insert the Test User
INSERT INTO AppUser (user_id, username, password, email, organization_id, organization_role)
VALUES (
    1,
    'testuser',
    'password123', -- ! In a real application, NEVER store passwords in plain text! Use hashing (e.g., bcrypt).
    'test@example.com',
    101,
    'Creator'
);

---

-- Optional: Insert a test Item associated with the test user (user_id 1)
INSERT INTO Item (item_id, title, description, category, list_date, creator_id)
VALUES (
    501,
    'Sample Widget',
    'A sample item for testing.',
    'Gadget',
    '2025-11-06',
    1
);
