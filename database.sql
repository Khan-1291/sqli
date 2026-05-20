-- ============================================
-- SQL Injection Lab - Database Schema & Sample Data
-- Intentionally vulnerable for educational purposes ONLY
-- ============================================

-- Drop tables if they exist
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample users (intentionally weak passwords for demo)
INSERT INTO users (username, password, email, role) VALUES
('admin', 'admin123', 'admin@sqli-lab.local', 'admin'),
('alice', 'password1', 'alice@example.com', 'user'),
('bob', 'password2', 'bob@example.com', 'user'),
('charlie', 'password3', 'charlie@example.com', 'user'),
('dave', 'password4', 'dave@example.com', 'user'),
('eve', 'password5', 'eve@example.com', 'user'),
('frank', 'password6', 'frank@example.com', 'user'),
('grace', 'password7', 'grace@example.com', 'user'),
('hank', 'password8', 'hank@example.com', 'user'),
('irene', 'password9', 'irene@example.com', 'user');

-- ============================================
-- PRODUCTS TABLE
-- ============================================
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL,
    category TEXT,
    stock INTEGER DEFAULT 0
);

INSERT INTO products (name, description, price, category, stock) VALUES
('Laptop Pro X1', 'High-performance business laptop with 16GB RAM', 1299.99, 'Electronics', 15),
('Wireless Mouse', 'Ergonomic wireless mouse with USB receiver', 29.99, 'Accessories', 200),
('USB-C Hub', '7-in-1 USB-C hub with HDMI and card reader', 49.99, 'Accessories', 80),
('Mechanical Keyboard', 'RGB mechanical keyboard with Cherry MX switches', 89.99, 'Accessories', 45),
('Webcam HD 1080p', 'Full HD webcam with built-in microphone', 59.99, 'Electronics', 60),
('Monitor 27" 4K', '27-inch 4K UHD monitor with IPS panel', 349.99, 'Electronics', 25),
('SSD 1TB', '1TB NVMe M.2 SSD with read speeds up to 3500MB/s', 119.99, 'Storage', 100),
('RAM 32GB DDR4', '32GB DDR4 3200MHz memory kit (2x16GB)', 89.99, 'Components', 50),
('Graphics Card RTX 4060', 'NVIDIA GeForce RTX 4060 8GB GDDR6', 299.99, 'Components', 10),
('Power Supply 750W', '750W 80+ Gold fully modular power supply', 109.99, 'Components', 30),
('CPU Cooler', 'AIO liquid cooler 240mm with RGB fans', 79.99, 'Components', 40),
('Gaming Chair', 'Ergonomic gaming chair with lumbar support', 199.99, 'Furniture', 20),
('Desk Mat XXL', 'Extra large desk mat 900x400mm', 24.99, 'Accessories', 150),
('Cable Management Kit', 'Cable ties, clips, and sleeves organizer', 14.99, 'Accessories', 300),
('Monitor Arm', 'Single monitor arm desk mount up to 32"', 44.99, 'Furniture', 35);

-- ============================================
-- ORDERS TABLE
-- ============================================
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    total_price REAL,
    status TEXT DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
(2, 1, 1, 1299.99, 'completed'),
(2, 3, 2, 99.98, 'completed'),
(3, 2, 1, 29.99, 'completed'),
(3, 5, 1, 59.99, 'pending'),
(4, 7, 2, 239.98, 'completed'),
(5, 12, 1, 199.99, 'shipped'),
(6, 1, 1, 1299.99, 'pending'),
(7, 9, 1, 299.99, 'completed'),
(8, 4, 1, 89.99, 'shipped'),
(9, 6, 1, 349.99, 'pending'),
(10, 13, 3, 74.97, 'completed'),
(2, 8, 1, 89.99, 'pending'),
(3, 11, 1, 79.99, 'completed'),
(4, 14, 2, 29.98, 'shipped'),
(5, 15, 1, 44.99, 'pending');

-- ============================================
-- FEEDBACK TABLE (for Second-Order SQLi demo)
-- ============================================
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    message TEXT NOT NULL,
    is_approved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initial feedback entries
INSERT INTO feedback (name, email, message, is_approved) VALUES
('John Doe', 'john@example.com', 'Great products! Fast shipping.', 1),
('Jane Smith', 'jane@example.com', 'The laptop is amazing, highly recommend.', 1),
('Mike Johnson', 'mike@example.com', 'Customer service was helpful.', 1);

-- ============================================
-- SECRETS TABLE (for Out-of-Band SQLi simulation)
-- ============================================
CREATE TABLE secrets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    secret_key TEXT NOT NULL,
    secret_value TEXT NOT NULL,
    description TEXT
);

INSERT INTO secrets (secret_key, secret_value, description) VALUES
('API_KEY_PROD', 'sk-prod-abc123xyz789', 'Production API key'),
('DB_PASSWORD', 'SuperSecretDBPass2024!', 'Database admin password'),
('JWT_SECRET', 'jwt-secret-token-lab-env', 'JWT signing secret'),
('ADMIN_BACKDOOR', 'backdoor-access-granted', 'Admin backdoor token'),
('FLAG', 'FLAG{SQL_INJECTION_MASTER_2024}', 'CTF Flag - Congratulations!');

-- ============================================
-- LOGS TABLE (for stacked queries demo)
-- ============================================
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,
    details TEXT,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO logs (action, details) VALUES
('INIT', 'Database initialized for SQLi Lab'),
('ADMIN_LOGIN', 'Admin logged in from 127.0.0.1'),
('USER_REGISTER', 'New user alice registered');
