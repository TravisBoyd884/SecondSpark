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
    price MONEY,
    description VARCHAR(255),
    category VARCHAR(255),
    list_date DATE,
    creator_id INT NOT NULL,

    CONSTRAINT fk_item_creator
        FOREIGN KEY (creator_id)
        REFERENCES AppUser(user_id)
);

-- ============================================================
--  ITEM IMAGE
-- ============================================================

CREATE TABLE ItemImage (
    image_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    image_url VARCHAR(512) NOT NULL, -- Path or URL where the image file is stored
    is_primary BOOLEAN DEFAULT FALSE,
    upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_itemimage_item
        FOREIGN KEY (item_id)
        REFERENCES Item(item_id)
        ON DELETE CASCADE -- If the item is deleted, delete its images too
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
    environment VARCHAR(255) NOT NULL DEFAULT 'sandbox',

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
    environment VARCHAR(255) NOT NULL,

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
('bob',   'securepwd', 'bob@greensoft.com', (SELECT organization_id FROM Organization WHERE name='GreenSoft'), 'User'),
('carol', 'qwerty', 'carol@edusmart.com',   (SELECT organization_id FROM Organization WHERE name='EduSmart'), 'Admin'),
('dave',  'letmein', 'dave@healthwave.com', (SELECT organization_id FROM Organization WHERE name='HealthWave'), 'User'),
('eve',   'mypassword', 'eve@aerolabs.com', (SELECT organization_id FROM Organization WHERE name='AeroLabs'), 'User');


-- ============================================================
-- ITEM (20 Items with Prices)
-- ============================================================
-- Creator IDs used: 1=alice, 2=bob, 3=carol, 4=dave, 5=eve

INSERT INTO Item (title, price, description, category, list_date, creator_id) VALUES
-- Existing 5 Items
('Wireless Mouse', 25.99, 'Ergonomic wireless mouse', 'Electronics', '2024-01-15', 1),
('Eco Bottle', 15.50, 'Reusable eco-friendly water bottle', 'Lifestyle', '2024-02-10', 2),
('AI Textbook', 49.99, 'Comprehensive guide to AI basics', 'Education', '2024-03-05', 3),
('Heart Monitor', 199.99, 'Wearable heart monitoring device', 'Health', '2024-04-01', 4),
('Drone Kit', 500.00, 'DIY drone assembly kit', 'Technology', '2024-05-12', 5),

-- 15 New Items
('Mechanical Keyboard', 120.00, 'TKL keyboard with brown switches', 'Electronics', '2024-06-01', 1),
('Smart Watch', 249.99, 'Fitness tracker and notification display', 'Electronics', '2024-06-05', 1),
('Organic Cotton Tee', 35.00, 'Soft, sustainably sourced t-shirt', 'Apparel', '2024-06-10', 2),
('Bamboo Sunglasses', 55.99, 'Polarized lenses with bamboo frames', 'Apparel', '2024-06-15', 2),
('Digital Art Tablet', 350.00, 'Pressure-sensitive drawing device', 'Art', '2024-06-20', 3),
('Learn Python Book', 29.99, 'Beginner guide to Python programming', 'Education', '2024-06-25', 3),
('Resistance Bands Set', 40.00, 'Set of five exercise resistance bands', 'Fitness', '2024-07-01', 4),
('Yoga Mat (Premium)', 75.00, 'Thick, non-slip yoga and exercise mat', 'Fitness', '2024-07-05', 4),
('3D Printer Filament', 22.50, 'PLA filament in various colors', 'Technology', '2024-07-10', 5),
('Robotics Starter Kit', 150.00, 'Introductory kit for robotics projects', 'Technology', '2024-07-15', 5),
('Coffee Maker (Pour Over)', 65.00, 'Classic pour-over coffee system', 'Kitchen', '2024-07-20', 1),
('Cast Iron Skillet', 45.00, 'Pre-seasoned 10-inch cast iron pan', 'Kitchen', '2024-07-25', 2),
('Noise Cancelling Headphones', 199.00, 'Over-ear headphones with ANC', 'Electronics', '2024-08-01', 3),
('Portable Bluetooth Speaker', 85.00, 'Waterproof portable speaker', 'Electronics', '2024-08-05', 4),
('Camping Tent (2-Person)', 130.00, 'Lightweight two-person hiking tent', 'Outdoors', '2024-08-10', 5);


-- ============================================================
-- ITEM IMAGE (20 Images - one for each item)
-- ============================================================
-- Note: item_id 1 is 'Wireless Mouse', item_id 20 is 'Camping Tent (2-Person)'

INSERT INTO ItemImage (item_id, image_url, is_primary)
SELECT item_id, '/uploads/item_' || item_id || '.jpg', TRUE
FROM Item
ORDER BY item_id;


-- ============================================================
-- AppTransaction
-- ============================================================
-- Seller IDs used: 1=alice, 2=bob, 3=carol

INSERT INTO AppTransaction (sale_date, total, tax, seller_comission, seller_id) VALUES
('2024-09-01', 390.00, 30.00, 15.00, (SELECT user_id FROM AppUser WHERE username='alice')), -- Items 1, 6, 17
('2024-09-02', 170.00,  12.50, 6.00, (SELECT user_id FROM AppUser WHERE username='bob')),   -- Items 2, 7, 12
('2024-09-03', 295.00,  20.00, 10.00, (SELECT user_id FROM AppUser WHERE username='carol')); -- Items 3, 10, 19


-- ============================================================
-- AppTransaction_Item (Link Items to Transactions)
-- ============================================================
-- Transaction 1 (alice)
INSERT INTO AppTransaction_Item (item_id, transaction_id) VALUES
(1, 1),  -- Wireless Mouse
(6, 1),  -- Mechanical Keyboard
(17, 1); -- Coffee Maker (Pour Over)

-- Transaction 2 (bob)
INSERT INTO AppTransaction_Item (item_id, transaction_id) VALUES
(2, 2),  -- Eco Bottle
(7, 2),  -- Smart Watch
(12, 2); -- Cast Iron Skillet

-- Transaction 3 (carol)
INSERT INTO AppTransaction_Item (item_id, transaction_id) VALUES
(3, 3),  -- AI Textbook
(10, 3), -- Digital Art Tablet
(19, 3); -- Portable Bluetooth Speaker