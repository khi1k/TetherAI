-- Declarative Database Schema & Reporting Engine for Tether AI Technologies
-- File: prototype_declarative.sql

-- Drop existing tables if re-running script
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS customers;

-- 1. Create Customers Table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- 2. Create Sales Table
CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    sale_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- 3. Populate Sample Customers
INSERT INTO customers (id, name) VALUES (1, 'Alex Mercer');
INSERT INTO customers (id, name) VALUES (2, 'Brian Jones');
INSERT INTO customers (id, name) VALUES (3, 'Carlos Reed');
INSERT INTO customers (id, name) VALUES (4, 'David Miller');

-- 4. Populate Sample Sales Transactions (4+ sample sales)
INSERT INTO sales (customer_id, amount, sale_date) VALUES (1, 30.00, '2025-02-23');
INSERT INTO sales (customer_id, amount, sale_date) VALUES (2, 15.00, '2025-02-23');
INSERT INTO sales (customer_id, amount, sale_date) VALUES (1, 25.00, '2025-02-23');
INSERT INTO sales (customer_id, amount, sale_date) VALUES (3, 30.00, '2025-02-23');
INSERT INTO sales (customer_id, amount, sale_date) VALUES (2, 10.00, '2025-02-23');
INSERT INTO sales (customer_id, amount, sale_date) VALUES (1, 18.00, '2025-02-23');

-- 5. Declarative Query: Total amount spent by each customer (Highest to Lowest)
SELECT 
    c.id AS customer_id,
    c.name AS customer_name,
    SUM(s.amount) AS total_spent,
    COUNT(s.id) AS total_visits
FROM customers c
JOIN sales s ON c.id = s.customer_id
GROUP BY c.id, c.name
ORDER BY total_spent DESC;
