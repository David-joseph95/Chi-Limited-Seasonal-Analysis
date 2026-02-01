-- ====================================================================
-- 1?? Seasonal Revenue Patterns (Top Juice Category)
-- ====================================================================
SELECT TOP 10
    season,
    festive_period,
    category,
    SUM(TRY_CAST(total_revenue AS decimal(18,2))) AS total_revenue,
    ROUND(AVG(TRY_CAST(avg_weekly_revenue AS decimal(18,2))), 2) AS avg_weekly_revenue
FROM v_seasonal_performance
WHERE category = 'Juice'
GROUP BY season, festive_period, category
ORDER BY total_revenue DESC;


-- ====================================================================
-- 2?? Products with High Stockout Frequency
-- ====================================================================
SELECT TOP 10
    product_name,
    region_name,
    SUM(TRY_CAST(total_stockout_days AS int)) AS total_stockout_days,
    ROUND(AVG(TRY_CAST(avg_closing_stock AS int)), 0) AS avg_closing_stock,
    SUM(TRY_CAST(total_holding_cost AS decimal(18,2))) AS total_holding_cost
FROM v_inventory_health
WHERE total_stockout_days > 10
GROUP BY product_name, region_name
ORDER BY total_stockout_days DESC;

