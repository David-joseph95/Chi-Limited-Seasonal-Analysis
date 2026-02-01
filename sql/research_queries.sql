-- ===============================
-- RESEARCH ANALYSIS
-- “what patterns exist?”--
-- ===============================

-- Revenue concentration by product
SELECT
    p.product_name,
    SUM(TRY_CAST(s.revenue_ngn AS DECIMAL(18,2))) AS product_revenue
FROM fact_sales s
JOIN dim_product p ON s.product_id = p.product_id
GROUP BY p.product_name
ORDER BY product_revenue DESC;


-- Revenue share (Pareto analysis)
SELECT
    p.product_name,
    SUM(TRY_CAST(s.revenue_ngn AS DECIMAL(18,2))) AS revenue,
    SUM(TRY_CAST(s.revenue_ngn AS DECIMAL(18,2)))
      / SUM(SUM(TRY_CAST(s.revenue_ngn AS DECIMAL(18,2)))) OVER () AS revenue_ratio
FROM fact_sales s
JOIN dim_product p ON s.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC;


-- Seasonal Revenue Patterns
SELECT 
    season,
    festive_period,
    category,
    total_revenue,
    avg_weekly_revenue
FROM v_seasonal_performance
WHERE category = 'Juice'
ORDER BY total_revenue DESC;


-- Month-over-Month Growth
WITH monthly_revenue AS (
    SELECT 
        t.year,
        t.month_name,
        t.month_number,
        SUM(TRY_CAST(s.revenue_ngn AS decimal(18,2))) AS revenue
    FROM fact_sales s
    JOIN dim_time t 
        ON s.week_id = t.week_id
    GROUP BY 
        t.year, 
        t.month_name, 
        t.month_number
)
SELECT 
    year,
    month_name,
    revenue,

    LAG(revenue) OVER (
        ORDER BY year, month_number
    ) AS prev_month_revenue,

    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY year, month_number)) /
        NULLIF(LAG(revenue) OVER (ORDER BY year, month_number), 0),
        2
    ) AS growth_pct
FROM monthly_revenue
ORDER BY 
    year, 
    month_number;
