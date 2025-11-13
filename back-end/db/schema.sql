-- 1. Create the Organization Table
CREATE TABLE Organization (
    organization_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL
);

---

-- 2. Create the User Table
CREATE TABLE AppUser (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    organization_id INT,
    organization_role VARCHAR,
    CONSTRAINT fk_organization
        FOREIGN KEY (organization_id)
        REFERENCES Organization(organization_id)
);

---

-- 3. Create the Item Table
CREATE TABLE Item (
    item_id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    category VARCHAR,
    list_date DATE,
    creator_id INT NOT NULL,
    CONSTRAINT fk_creator
        FOREIGN KEY (creator_id)
        REFERENCES AppUser (user_id)
);

---

-- 4. Create the Reseller Table
CREATE TABLE Reseller (
    reseller_id SERIAL PRIMARY KEY,
    reseller_name VARCHAR NOT NULL
);

---

-- 5. Create the Transaction Table
-- Note: 'MONEY' is a standard PostgreSQL type for currency.
CREATE TABLE AppTransaction (
    transaction_id SERIAL PRIMARY KEY,
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
    transaction_item_id SERIAL PRIMARY KEY,
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

-- ==========================================
-- INSERT TEST DATA (SERIAL / AUTO-INCREMENT KEYS)
-- ==========================================

-- 1. Organization
INSERT INTO Organization (name) VALUES
('TechCorp'),
('GreenSoft'),
('EduSmart'),
('HealthWave'),
('AeroLabs');

-- 2. AppUser
INSERT INTO AppUser (username, password, email, organization_id, organization_role) VALUES
('alice', 'pass123', 'alice@techcorp.com', (SELECT organization_id FROM Organization WHERE name='TechCorp'), 'Admin'),
('bob', 'securepwd', 'bob@greensoft.com', (SELECT organization_id FROM Organization WHERE name='GreenSoft'), 'Manager'),
('carol', 'qwerty', 'carol@edusmart.com', (SELECT organization_id FROM Organization WHERE name='EduSmart'), 'User'),
('dave', 'letmein', 'dave@healthwave.com', (SELECT organization_id FROM Organization WHERE name='HealthWave'), 'Analyst'),
('eve', 'mypassword', 'eve@aerolabs.com', (SELECT organization_id FROM Organization WHERE name='AeroLabs'), 'User');

-- 3. Item
INSERT INTO Item (title, description, category, list_date, creator_id) VALUES
('Wireless Mouse', 'Ergonomic wireless mouse', 'Electronics', '2024-01-15', (SELECT user_id FROM AppUser WHERE username='alice')),
('Eco Bottle', 'Reusable eco-friendly water bottle', 'Lifestyle', '2024-02-10', (SELECT user_id FROM AppUser WHERE username='bob')),
('AI Textbook', 'Comprehensive guide to AI basics', 'Education', '2024-03-05', (SELECT user_id FROM AppUser WHERE username='carol')),
('Heart Monitor', 'Wearable heart monitoring device', 'Health', '2024-04-01', (SELECT user_id FROM AppUser WHERE username='dave')),
('Drone Kit', 'DIY drone assembly kit', 'Technology', '2024-05-12', (SELECT user_id FROM AppUser WHERE username='eve'));

-- 4. Reseller
INSERT INTO Reseller (reseller_name) VALUES
('BestBuy'),
('EcoMart'),
('BookWorld'),
('MediSupply'),
('TechStore');

-- 5. AppTransaction
INSERT INTO AppTransaction (sale_date, total, tax, reseller_comission, reseller_id) VALUES
('2024-06-01', 120.00, 10.00, 5.00, (SELECT reseller_id FROM Reseller WHERE reseller_name='BestBuy')),
('2024-06-02', 45.00, 3.50, 2.00, (SELECT reseller_id FROM Reseller WHERE reseller_name='EcoMart')),
('2024-06-03', 80.00, 6.40, 4.00, (SELECT reseller_id FROM Reseller WHERE reseller_name='BookWorld')),
('2024-06-04', 300.00, 24.00, 15.00, (SELECT reseller_id FROM Reseller WHERE reseller_name='MediSupply')),
('2024-06-05', 150.00, 12.00, 7.50, (SELECT reseller_id FROM Reseller WHERE reseller_name='TechStore'));

-- 6. AppTransaction_Item
INSERT INTO AppTransaction_Item (item_id, transaction_id) VALUES
((SELECT item_id FROM Item WHERE title='Wireless Mouse'), (SELECT transaction_id FROM AppTransaction WHERE sale_date='2024-06-01')),
((SELECT item_id FROM Item WHERE title='Eco Bottle'), (SELECT transaction_id FROM AppTransaction WHERE sale_date='2024-06-02')),
((SELECT item_id FROM Item WHERE title='AI Textbook'), (SELECT transaction_id FROM AppTransaction WHERE sale_date='2024-06-03')),
((SELECT item_id FROM Item WHERE title='Heart Monitor'), (SELECT transaction_id FROM AppTransaction WHERE sale_date='2024-06-04')),
((SELECT item_id FROM Item WHERE title='Drone Kit'), (SELECT transaction_id FROM AppTransaction WHERE sale_date='2024-06-05'));

-- ==========================================
-- END OF TEST DATA INSERTS
-- ==========================================
