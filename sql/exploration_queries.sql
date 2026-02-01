-- =========================================================
-- EXPLORATORY DATA ANALYSIS (EDA)
-- Purpose: Understand structure, quality, and coverage
-- =========================================================

-- -----------------------------
-- Row counts per table
-- -----------------------------
SELECT 'fact_sales' AS table_name, COUNT(*) AS row_count FROM fact_sales;
SELECT 'dim_product' AS table_name, COUNT(*) AS row_count FROM dim_product;
SELECT 'dim_time' AS table_name, COUNT(*) AS row_count FROM dim_time;
SELECT 'dim_geography' AS table_name, COUNT(*) AS row_count FROM dim_geography;
SELECT 'fact_inventory' AS table_name, COUNT(*) AS row_count FROM fact_inventory;

-- Row counts
SELECT COUNT(*) AS sales_rows FROM fact_sales;
SELECT COUNT(*) AS product_rows FROM dim_product;
SELECT COUNT(*) AS geography_rows FROM dim_geography;

-- -----------------------------
-- Sample records
-- -----------------------------
SELECT TOP 10 * FROM fact_sales;
SELECT TOP 10 * FROM dim_product;
SELECT TOP 10 * FROM dim_time;

-- -----------------------------
-- Missing values check
-- -----------------------------
SELECT
    SUM(CASE WHEN revenue_ngn IS NULL THEN 1 ELSE 0 END) AS missing_revenue,
    SUM(CASE WHEN units_sold IS NULL THEN 1 ELSE 0 END) AS missing_units,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) AS missing_product
FROM fact_sales;

-- -----------------------------
-- Numeric sanity checks
-- -----------------------------
SELECT
    MIN(revenue_ngn) AS min_revenue,
    MAX(revenue_ngn) AS max_revenue,
    MIN(units_sold) AS min_units,
    MAX(units_sold) AS max_units
FROM fact_sales;

-- -----------------------------
-- Time coverage
-- -----------------------------
SELECT
    MIN(week_start_date) AS earliest_week,
    MAX(week_start_date) AS latest_week,
    COUNT(DISTINCT year) AS num_years
FROM dim_time;

-- -----------------------------
-- Orphan record checks
-- -----------------------------
SELECT COUNT(*) AS orphan_sales_products
FROM fact_sales s
LEFT JOIN dim_product p ON s.product_id = p.product_id
WHERE p.product_id IS NULL;

-- ===============================

