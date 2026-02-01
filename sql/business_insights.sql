SELECT TOP 10 * 
FROM fact_sales;

SELECT 
    COLUMN_NAME,
    DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'fact_sales';


-- Revenue Concentration Analysis--
-- Top 10 Products by Revenue (Product Performance)
SELECT TOP 10
       p.product_name,
       p.category,
       SUM(TRY_CAST(s.revenue_ngn AS DECIMAL(18,2))) AS total_revenue,
       SUM(TRY_CAST(s.units_sold AS INT)) AS total_units
FROM fact_sales s
JOIN dim_product p 
     ON s.product_id = p.product_id
GROUP BY p.product_name, p.category
ORDER BY total_revenue DESC;

-- Revenue by region
SELECT 
    g.region_name,
    SUM(TRY_CAST(s.revenue_ngn AS DECIMAL(18,2))) AS total_revenue
FROM fact_sales s
JOIN dim_geography g ON s.region_id = g.region_id
GROUP BY g.region_name
ORDER BY total_revenue DESC;

-- Revenue by Region and Year
SELECT 
    g.region_name,
    t.year,

    SUM(TRY_CAST(s.revenue_ngn AS decimal(18,2))) AS total_revenue,

    ROUND(
        AVG(TRY_CAST(s.revenue_ngn AS decimal(18,2))),
        2
    ) AS avg_revenue_per_transaction
FROM fact_sales s
JOIN dim_geography g 
    ON s.region_id = g.region_id
JOIN dim_time t 
    ON s.week_id = t.week_id
GROUP BY 
    g.region_name, 
    t.year
ORDER BY 
    total_revenue DESC;


-- Promotional ROI by Type
SELECT 
    promo_type,
    COUNT(*) AS num_campaigns,

    ROUND(AVG(roi), 2) AS avg_roi,
    ROUND(MIN(roi), 2) AS min_roi,
    ROUND(MAX(roi), 2) AS max_roi
FROM v_promotional_effectiveness
GROUP BY 
    promo_type
ORDER BY 
    avg_roi DESC;
