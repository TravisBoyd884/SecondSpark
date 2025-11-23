-- ============================================================
--  ORGANIZATION
-- ============================================================

CREATE TABLE Organization (
    organization_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- ============================================================
--  APP USER
-- ============================================================

CREATE TABLE AppUser (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    organization_id INT,
    organization_role VARCHAR(255),
    ebay_account_id INT,
    etsy_account_id INT,

    CONSTRAINT fk_appuser_org
        FOREIGN KEY (organization_id)
        REFERENCES Organization(organization_id)
);

-- ============================================================
--  ITEM
-- ============================================================

CREATE TABLE Item (
    item_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    category VARCHAR(255),
    list_date DATE,
    creator_id INT NOT NULL,

    CONSTRAINT fk_item_creator
        FOREIGN KEY (creator_id)
        REFERENCES AppUser(user_id)
);

-- ============================================================
--  TRANSACTION
-- ============================================================

CREATE TABLE AppTransaction (
    transaction_id SERIAL PRIMARY KEY,
    sale_date DATE,
    total MONEY,
    tax MONEY,
    seller_comission MONEY,
    seller_id INT NOT NULL,

    CONSTRAINT fk_transaction_seller
        FOREIGN KEY (seller_id)
        REFERENCES AppUser(user_id)
);

-- ============================================================
--  TRANSACTION-ITEM LINK
-- ============================================================

CREATE TABLE AppTransaction_Item (
    transaction_item_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    transaction_id INT NOT NULL,

    CONSTRAINT fk_transitem_item
        FOREIGN KEY (item_id)
        REFERENCES Item(item_id),

    CONSTRAINT fk_transitem_transaction
        FOREIGN KEY (transaction_id)
        REFERENCES AppTransaction(transaction_id)
);

-- ============================================================
--  EBAY ACCOUNT
-- ============================================================

CREATE TABLE Ebay (
    account_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    client_id VARCHAR(255),
    client_secret VARCHAR(255),

    CONSTRAINT fk_ebay_user
        FOREIGN KEY (user_id)
        REFERENCES AppUser(user_id)
);

-- ============================================================
--  ETSY ACCOUNT
-- ============================================================

CREATE TABLE Etsy (
    account_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    client_id VARCHAR(255),
    client_secret VARCHAR(255),

    CONSTRAINT fk_etsy_user
        FOREIGN KEY (user_id)
        REFERENCES AppUser(user_id)
);

-- ============================================================
--  EBAY ITEM
-- ============================================================

CREATE TABLE EbayItem (
    sku VARCHAR(255) PRIMARY KEY,
    item_id INT NOT NULL,
    quantity INT,
    ebay_item_id VARCHAR(255),
    ebay_offer_id VARCHAR(255),
    ebay_listing_id VARCHAR(255),
    ebay_status VARCHAR(255),
    last_synced_at TIMESTAMP,
    source_of_truth VARCHAR(255),
    ebay_account_id INT NOT NULL,

    CONSTRAINT fk_ebayitem_item
        FOREIGN KEY (item_id)
        REFERENCES Item(item_id),

    CONSTRAINT fk_ebayitem_account
        FOREIGN KEY (ebay_account_id)
        REFERENCES Ebay(account_id)
);

-- ============================================================
--  ETSY ITEM
-- ============================================================

CREATE TABLE EtsyItem (
    sku VARCHAR(255) PRIMARY KEY,
    item_id INT NOT NULL,
    quantity INT,
    etsy_account_id INT NOT NULL,

    CONSTRAINT fk_etsyitem_item
        FOREIGN KEY (item_id)
        REFERENCES Item(item_id),

    CONSTRAINT fk_etsyitem_account
        FOREIGN KEY (etsy_account_id)
        REFERENCES Etsy(account_id)
);


-- ============================================================
-- ADD FK FROM APPUSER → EBAY & ETSY
-- ============================================================

ALTER TABLE AppUser
ADD CONSTRAINT fk_appuser_ebay
    FOREIGN KEY (ebay_account_id)
    REFERENCES Ebay(account_id);

ALTER TABLE AppUser
ADD CONSTRAINT fk_appuser_etsy
    FOREIGN KEY (etsy_account_id)
    REFERENCES Etsy(account_id);


-- ============================================================
-- TEST DATA
-- ============================================================

-- Organization
INSERT INTO Organization (name) VALUES
('TechCorp'),
('GreenSoft'),
('EduSmart'),
('HealthWave'),
('AeroLabs');

-- AppUser
INSERT INTO AppUser (username, password, email, organization_id, organization_role) VALUES
('alice', 'pass123', 'alice@techcorp.com',  (SELECT organization_id FROM Organization WHERE name='TechCorp'), 'Admin'),
('bob',   'securepwd', 'bob@greensoft.com', (SELECT organization_id FROM Organization WHERE name='GreenSoft'), 'Manager'),
('carol', 'qwerty', 'carol@edusmart.com',   (SELECT organization_id FROM Organization WHERE name='EduSmart'), 'User'),
('dave',  'letmein', 'dave@healthwave.com', (SELECT organization_id FROM Organization WHERE name='HealthWave'), 'Analyst'),
('eve',   'mypassword', 'eve@aerolabs.com', (SELECT organization_id FROM Organization WHERE name='AeroLabs'), 'User');

-- Item
INSERT INTO Item (title, description, category, list_date, creator_id) VALUES
('Wireless Mouse', 'Ergonomic wireless mouse', 'Electronics', '2024-01-15', (SELECT user_id FROM AppUser WHERE username='alice')),
('Eco Bottle', 'Reusable eco-friendly water bottle', 'Lifestyle', '2024-02-10', (SELECT user_id FROM AppUser WHERE username='bob')),
('AI Textbook', 'Comprehensive guide to AI basics', 'Education', '2024-03-05', (SELECT user_id FROM AppUser WHERE username='carol')),
('Heart Monitor', 'Wearable heart monitoring device', 'Health', '2024-04-01', (SELECT user_id FROM AppUser WHERE username='dave')),
('Drone Kit', 'DIY drone assembly kit', 'Technology', '2024-05-12', (SELECT user_id FROM AppUser WHERE username='eve'));

-- AppTransaction
INSERT INTO AppTransaction (sale_date, total, tax, seller_comission, seller_id) VALUES
('2024-06-01', 120.00, 10.00, 5.00, (SELECT user_id FROM AppUser WHERE username='alice')),
('2024-06-02', 45.00,  3.50, 2.00, (SELECT user_id FROM AppUser WHERE username='bob')),
('2024-06-03', 80.00,  6.40, 4.00, (SELECT user_id FROM AppUser WHERE username='carol'));

-- AppTransaction_Item (ALL FIXED)
INSERT INTO AppTransaction_Item (item_id, transaction_id) VALUES
((SELECT item_id FROM Item WHERE title='Wireless Mouse'),
 (SELECT transaction_id FROM AppTransaction WHERE sale_date='2024-06-01')),

((SELECT item_id FROM Item WHERE title='Eco Bottle'),
 (SELECT transaction_id FROM AppTransaction WHERE sale_date='2024-06-02')),

((SELECT item_id FROM Item WHERE title='AI Textbook'),
 (SELECT transaction_id FROM AppTransaction WHERE sale_date='2024-06-03')),

((SELECT item_id FROM Item WHERE title='Heart Monitor'),
 (SELECT transaction_id FROM AppTransaction WHERE sale_date='2024-06-01'));


-- END OF TEST DATA
