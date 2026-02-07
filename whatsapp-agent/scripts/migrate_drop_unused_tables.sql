-- Migration: drop FK constraint on conversations and remove unused tables
-- This preserves all conversation history while removing product/order/customer tables

-- 1. Drop the foreign key constraint so conversations can use phone-derived UUIDs
ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_customer_id_fkey;

-- 2. Drop unused tables (order matters due to FKs)
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS customers;

-- 3. Drop orphaned indexes
DROP INDEX IF EXISTS idx_customers_phone;
DROP INDEX IF EXISTS idx_products_category;
DROP INDEX IF EXISTS idx_orders_customer;
DROP INDEX IF EXISTS idx_orders_status;
