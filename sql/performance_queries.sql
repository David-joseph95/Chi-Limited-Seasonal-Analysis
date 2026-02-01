-- ===============================
-- PERFORMANCE
-- ===============================

-- Top 10 Products by Revenue
SELECT TOP 10
    p.product_name,
    p.category,
    SUM(TRY_CAST(s.revenue_ngn AS decimal(18,2))) AS total_revenue,
    SUM(TRY_CAST(s.units_sold AS int)) AS total_units
FROM fact_sales s
JOIN dim_product p 
    ON s.product_id = p.product_id
GROUP BY 
    p.product_name, 
    p.category
ORDER BY 
    total_revenue DESC;


-- Channel Performance Comparison
SELECT 
    channel_id,

    COUNT(DISTINCT product_id) AS num_products,

    SUM(TRY_CAST(revenue_ngn AS decimal(18,2))) AS total_revenue,
    SUM(TRY_CAST(units_sold AS int)) AS total_units,

    ROUND(
        AVG(
            TRY_CAST(revenue_ngn AS decimal(18,2)) /
            NULLIF(TRY_CAST(units_sold AS int), 0)
        ),
        2
    ) AS avg_price_per_unit
FROM fact_sales
GROUP BY 
    channel_id;


SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'fact_inventory';

-- Inventory Risk: Products below reorder level
SELECT
    p.product_name,
    TRY_CAST(i.stock_on_hand AS INT) AS stock_on_hand,
    TRY_CAST(i.reorder_level AS INT) AS reorder_level
FROM fact_inventory i
JOIN dim_product p 
    ON i.product_id = p.product_id
WHERE TRY_CAST(i.stock_on_hand AS INT) <
      TRY_CAST(i.reorder_level AS INT)
ORDER BY stock_on_hand ASC;

