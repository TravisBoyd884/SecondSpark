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
        ON DELETE SET NULL -- If an Organization is deleted, User's organization_id is set to NULL
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
        ON DELETE CASCADE -- If the Item's creator is deleted, delete the Item
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
        ON DELETE CASCADE -- If the Seller is deleted, delete their Transactions
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
        REFERENCES Item(item_id)
        ON DELETE CASCADE, -- If Item is deleted, delete this link

    CONSTRAINT fk_transitem_transaction
        FOREIGN KEY (transaction_id)
        REFERENCES AppTransaction(transaction_id)
        ON DELETE CASCADE -- If Transaction is deleted, delete this link
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
        ON DELETE CASCADE -- If User is deleted, delete their Ebay account
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
        ON DELETE CASCADE -- If User is deleted, delete their Etsy account
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
        REFERENCES Item(item_id)
        ON DELETE CASCADE, -- If Item is deleted, delete its Ebay listing

    CONSTRAINT fk_ebayitem_account
        FOREIGN KEY (ebay_account_id)
        REFERENCES Ebay(account_id)
        ON DELETE CASCADE -- If Ebay account is deleted, delete its listings
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
        REFERENCES Item(item_id)
        ON DELETE CASCADE, -- If Item is deleted, delete its Etsy listing

    CONSTRAINT fk_etsyitem_account
        FOREIGN KEY (etsy_account_id)
        REFERENCES Etsy(account_id)
        ON DELETE CASCADE -- If Etsy account is deleted, delete its listings
);

-- ============================================================
-- ADD FK FROM APPUSER → EBAY & ETSY
-- ============================================================

ALTER TABLE AppUser
ADD CONSTRAINT fk_appuser_ebay
    FOREIGN KEY (ebay_account_id)
    REFERENCES Ebay(account_id)
    ON DELETE SET NULL;

ALTER TABLE AppUser
ADD CONSTRAINT fk_appuser_etsy
    FOREIGN KEY (etsy_account_id)
    REFERENCES Etsy(account_id)
    ON DELETE SET NULL;


-- ============================================================
-- TEST DATA
-- ============================================================

INSERT INTO Organization (name) VALUES
('Quantum Solutions Inc.'), ('Innovate Labs'), ('Global Dynamics'),
('Eco-Vision Group'), ('Sentinel Security'), ('Horizon Media'),
('Apex Logistics'), ('Zenith Financial'), ('Starlight Tech'),
('Phoenix Automation'), ('Cross-Link Corp'), ('Digital Frontier'),
('Evergreen Ventures'), ('Prime Systems'), ('Velocity Trade'),
('Blue Sky Agency'), ('Crystal Clear Comms'), ('Hyperion Energy'),
('Fusion Analytics'), ('Titan Manufacturing');

----------------------------------------------------------------------
-- APP USER (20 Rows)
-- Note: Assuming Organization IDs 1-20, Ebay IDs 1-20, and Etsy IDs 1-20 exist.
----------------------------------------------------------------------

INSERT INTO AppUser (user_id, username, password, email, organization_id, organization_role) VALUES
(1, 'alice', 'pass', 'alice@qsi.com', 1, 'Admin'),
(2, 'bob_il', 'p2il', 'bob@ilabs.com', 2, 'Editor'),
(3, 'carol_gd', 'p3gd', 'carol@gd.com', 3, 'User'),
(4, 'dave_evg', 'p4evg', 'dave@evg.com', 4, 'Admin'),
(5, 'eve_ss', 'p5ss', 'eve@ss.com', 5, 'User'),
(6, 'frank_hm', 'p6hm', 'frank@hm.com', 6, 'Admin'),
(7, 'grace_al', 'p7al', 'grace@al.com', 7, 'Editor'),
(8, 'henry_zf', 'p8zf', 'henry@zf.com', 8, 'User'),
(9, 'ivy_st', 'p9st', 'ivy@st.com', 9, 'Admin'),
(10, 'jack_pa', 'p10pa', 'jack@pa.com', 10, 'Editor'),
(11, 'karen_clc', 'p11clc', 'karen@clc.com', 11, 'User'),
(12, 'leo_df', 'p12df', 'leo@df.com', 12, 'Admin'),
(13, 'mia_ev', 'p13ev', 'mia@ev.com', 13, 'Editor'),
(14, 'noah_ps', 'p14ps', 'noah@ps.com', 14, 'User'),
(15, 'olivia_vt', 'p15vt', 'olivia@vt.com', 15, 'Admin'),
(16, 'peter_bsa', 'p16bsa', 'peter@bsa.com', 16, 'Editor'),
(17, 'quinn_ccc', 'p17ccc', 'quinn@ccc.com', 17, 'User'),
(18, 'rachel_he', 'p18he', 'rachel@he.com', 18, 'Admin'),
(19, 'sam_fa', 'p19fa', 'sam@fa.com', 19, 'Editor'),
(20, 'tina_tm', 'p20tm', 'tina@tm.com', 20, 'User');

----------------------------------------------------------------------
-- EBAY ACCOUNT (20 Rows - Linked to AppUser IDs 1-20, which will be created next)
----------------------------------------------------------------------

INSERT INTO Ebay (user_id, client_id, client_secret, environment) VALUES
(1, 'ebay_client_01', 'secret_01', 'production'), (2, 'ebay_client_02', 'secret_02', 'sandbox'),
(3, 'ebay_client_03', 'secret_03', 'production'), (4, 'ebay_client_04', 'secret_04', 'sandbox'),
(5, 'ebay_client_05', 'secret_05', 'production'), (6, 'ebay_client_06', 'secret_06', 'sandbox'),
(7, 'ebay_client_07', 'secret_07', 'production'), (8, 'ebay_client_08', 'secret_08', 'sandbox'),
(9, 'ebay_client_09', 'secret_09', 'production'), (10, 'ebay_client_10', 'secret_10', 'sandbox'),
(11, 'ebay_client_11', 'secret_11', 'production'), (12, 'ebay_client_12', 'secret_12', 'sandbox'),
(13, 'ebay_client_13', 'secret_13', 'production'), (14, 'ebay_client_14', 'secret_14', 'sandbox'),
(15, 'ebay_client_15', 'secret_15', 'production'), (16, 'ebay_client_16', 'secret_16', 'sandbox'),
(17, 'ebay_client_17', 'secret_17', 'production'), (18, 'ebay_client_18', 'secret_18', 'sandbox'),
(19, 'ebay_client_19', 'secret_19', 'production'), (20, 'ebay_client_20', 'secret_20', 'sandbox');


----------------------------------------------------------------------
-- ETSY ACCOUNT (20 Rows - Linked to AppUser IDs 1-20, which will be created next)
----------------------------------------------------------------------

INSERT INTO Etsy (user_id, client_id, client_secret, environment) VALUES
(1, 'etsy_client_01', 'etsy_secret_01', 'active'), (2, 'etsy_client_02', 'etsy_secret_02', 'active'),
(3, 'etsy_client_03', 'etsy_secret_03', 'inactive'), (4, 'etsy_client_04', 'etsy_secret_04', 'active'),
(5, 'etsy_client_05', 'etsy_secret_05', 'active'), (6, 'etsy_client_06', 'etsy_secret_06', 'active'),
(7, 'etsy_client_07', 'etsy_secret_07', 'inactive'), (8, 'etsy_client_08', 'etsy_secret_08', 'active'),
(9, 'etsy_client_09', 'etsy_secret_09', 'active'), (10, 'etsy_client_10', 'etsy_secret_10', 'active'),
(11, 'etsy_client_11', 'etsy_secret_11', 'active'), (12, 'etsy_client_12', 'etsy_secret_12', 'inactive'),
(13, 'etsy_client_13', 'etsy_secret_13', 'active'), (14, 'etsy_client_14', 'etsy_secret_14', 'active'),
(15, 'etsy_client_15', 'etsy_secret_15', 'active'), (16, 'etsy_client_16', 'etsy_secret_16', 'active'),
(17, 'etsy_client_17', 'etsy_secret_17', 'inactive'), (18, 'etsy_client_18', 'etsy_secret_18', 'active'),
(19, 'etsy_client_19', 'etsy_secret_19', 'active'), (20, 'etsy_client_20', 'etsy_secret_20', 'active');

----------------------------------------------------------------------
-- APP USER (Phase 2: Linking Ebay/Etsy Accounts)
-- This runs after Ebay and Etsy tables are populated.
----------------------------------------------------------------------

UPDATE AppUser
SET
    ebay_account_id = user_id,
    etsy_account_id = user_id
WHERE
    user_id BETWEEN 1 AND 20;

----------------------------------------------------------------------
-- ITEM (20 Items - EXISTING DATA KEPT AS REQUESTED)
-- Creator IDs used: 1=alice_qsi, 2=bob_il, 3=carol_gd, 4=dave_evg, 5=eve_ss
----------------------------------------------------------------------

INSERT INTO Item (title, price, description, category, list_date, creator_id) VALUES
('Wireless Mouse', 25.99, 'Ergonomic wireless mouse', 'Electronics', '2024-01-15', 1),
('Eco Bottle', 15.50, 'Reusable eco-friendly water bottle', 'Lifestyle', '2024-02-10', 2),
('AI Textbook', 49.99, 'Comprehensive guide to AI basics', 'Education', '2024-03-05', 3),
('Heart Monitor', 199.99, 'Wearable heart monitoring device', 'Health', '2024-04-01', 4),
('Drone Kit', 500.00, 'DIY drone assembly kit', 'Technology', '2024-05-12', 5),
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

----------------------------------------------------------------------
-- ITEM IMAGE (20 Rows - One primary image for each of the 20 Items)
----------------------------------------------------------------------

INSERT INTO ItemImage (item_id, image_url, is_primary) VALUES
(1, '/images/item_1.jpg', TRUE), (2, '/images/item_2.jpg', TRUE),
(3, '/images/item_3.jpg', TRUE), (4, '/images/item_4.jpg', TRUE),
(5, '/images/item_5.jpg', TRUE), (6, '/images/item_6.jpg', TRUE),
(7, '/images/item_7.jpg', TRUE), (8, '/images/item_8.jpg', TRUE),
(9, '/images/item_9.jpg', TRUE), (10, '/images/item_10.jpg', TRUE),
(11, '/images/item_11.jpg', TRUE), (12, '/images/item_12.jpg', TRUE),
(13, '/images/item_13.jpg', TRUE), (14, '/images/item_14.jpg', TRUE),
(15, '/images/item_15.jpg', TRUE), (16, '/images/item_16.jpg', TRUE),
(17, '/images/item_17.jpg', TRUE), (18, '/images/item_18.jpg', TRUE),
(19, '/images/item_19.jpg', TRUE), (20, '/images/item_20.jpg', TRUE);

----------------------------------------------------------------------
-- AppTransaction (20 Rows)
-- Seller IDs are distributed among AppUsers 1-5 (common creators)
----------------------------------------------------------------------

INSERT INTO AppTransaction (sale_date, total, tax, seller_comission, seller_id) VALUES
('2025-08-20', 395.99, 15.00, 19.80, 1),
('2025-08-21', 180.50, 7.22, 9.03, 2),
('2025-08-22', 400.00, 20.00, 20.00, 3),
('2025-08-23', 250.00, 12.50, 12.50, 4),
('2025-08-24', 550.00, 27.50, 27.50, 5),
('2025-08-25', 120.00, 6.00, 6.00, 1),
('2025-08-26', 300.00, 15.00, 15.00, 2),
('2025-08-27', 45.00, 2.25, 2.25, 3),
('2025-08-28', 99.99, 5.00, 5.00, 4),
('2025-08-29', 150.00, 7.50, 7.50, 5),
('2025-08-30', 210.00, 10.50, 10.50, 1),
('2025-09-01', 35.00, 1.75, 1.75, 2),
('2025-09-02', 85.00, 4.25, 4.25, 3),
('2025-09-03', 450.00, 22.50, 22.50, 4),
('2025-09-04', 199.00, 9.95, 9.95, 5),
('2025-09-05', 75.00, 3.75, 3.75, 1),
('2025-09-06', 40.00, 2.00, 2.00, 2),
('2025-09-07', 22.50, 1.13, 1.13, 3),
('2025-09-08', 55.99, 2.80, 2.80, 4),
('2025-09-09', 130.00, 6.50, 6.50, 5);


----------------------------------------------------------------------
-- AppTransaction_Item (20 Rows - Linking Transactions to Items)
-- Each of the 20 transactions is linked to one of the 20 items.
----------------------------------------------------------------------

INSERT INTO AppTransaction_Item (item_id, transaction_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
(6, 6), (7, 7), (8, 8), (9, 9), (10, 10),
(11, 11), (12, 12), (13, 13), (14, 14), (15, 15),
(16, 16), (17, 17), (18, 18), (19, 19), (20, 20);


----------------------------------------------------------------------
-- EBAY ITEM (20 Rows - Linking all 20 Items to Ebay Account 1)
----------------------------------------------------------------------

INSERT INTO EbayItem (sku, item_id, quantity, ebay_item_id, ebay_offer_id, ebay_listing_id, ebay_status, last_synced_at, source_of_truth, ebay_account_id) VALUES
('sku-eb-001', 1, 10, 'ebay1001', 'offer1001', 'list1001', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 1),
('sku-eb-002', 2, 5, 'ebay1002', 'offer1002', 'list1002', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 1),
('sku-eb-003', 3, 20, 'ebay1003', 'offer1003', 'list1003', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 1),
('sku-eb-004', 4, 2, 'ebay1004', 'offer1004', 'list1004', 'ACTIVE', CURRENT_TIMESTAMP, 'EBAY', 2),
('sku-eb-005', 5, 1, 'ebay1005', 'offer1005', 'list1005', 'INACTIVE', CURRENT_TIMESTAMP, 'APP', 2),
('sku-eb-006', 6, 15, 'ebay1006', 'offer1006', 'list1006', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 3),
('sku-eb-007', 7, 8, 'ebay1007', 'offer1007', 'list1007', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 3),
('sku-eb-008', 8, 30, 'ebay1008', 'offer1008', 'list1008', 'ACTIVE', CURRENT_TIMESTAMP, 'EBAY', 4),
('sku-eb-009', 9, 7, 'ebay1009', 'offer1009', 'list1009', 'INACTIVE', CURRENT_TIMESTAMP, 'APP', 4),
('sku-eb-010', 10, 3, 'ebay1010', 'offer1010', 'list1010', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 5),
('sku-eb-011', 11, 25, 'ebay1011', 'offer1011', 'list1011', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 5),
('sku-eb-012', 12, 12, 'ebay1012', 'offer1012', 'list1012', 'ACTIVE', CURRENT_TIMESTAMP, 'EBAY', 6),
('sku-eb-013', 13, 9, 'ebay1013', 'offer1013', 'list1013', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 6),
('sku-eb-014', 14, 4, 'ebay1014', 'offer1014', 'list1014', 'INACTIVE', CURRENT_TIMESTAMP, 'APP', 7),
('sku-eb-015', 15, 6, 'ebay1015', 'offer1015', 'list1015', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 7),
('sku-eb-016', 16, 18, 'ebay1016', 'offer1016', 'list1016', 'ACTIVE', CURRENT_TIMESTAMP, 'EBAY', 8),
('sku-eb-017', 17, 11, 'ebay1017', 'offer1017', 'list1017', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 8),
('sku-eb-018', 18, 14, 'ebay1018', 'offer1018', 'list1018', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 9),
('sku-eb-019', 19, 17, 'ebay1019', 'offer1019', 'list1019', 'INACTIVE', CURRENT_TIMESTAMP, 'EBAY', 9),
('sku-eb-020', 20, 13, 'ebay1020', 'offer1020', 'list1020', 'ACTIVE', CURRENT_TIMESTAMP, 'APP', 10);


----------------------------------------------------------------------
-- ETSY ITEM (20 Rows - Linking all 20 Items to Etsy Account 1)
----------------------------------------------------------------------

INSERT INTO EtsyItem (sku, item_id, quantity, etsy_account_id) VALUES
('sku-et-001', 1, 10, 1), ('sku-et-002', 2, 5, 1),
('sku-et-003', 3, 20, 2), ('sku-et-004', 4, 2, 2),
('sku-et-005', 5, 1, 3), ('sku-et-006', 6, 15, 3),
('sku-et-007', 7, 8, 4), ('sku-et-008', 8, 30, 4),
('sku-et-009', 9, 7, 5), ('sku-et-010', 10, 3, 5),
('sku-et-011', 11, 25, 6), ('sku-et-012', 12, 12, 6),
('sku-et-013', 13, 9, 7), ('sku-et-014', 14, 4, 7),
('sku-et-015', 15, 6, 8), ('sku-et-016', 16, 18, 8),
('sku-et-017', 17, 11, 9), ('sku-et-018', 18, 14, 9),
('sku-et-019', 19, 17, 10), ('sku-et-020', 20, 13, 10);