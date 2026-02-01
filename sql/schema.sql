-- =========================================================
-- ANALYTICAL VIEWS
-- =========================================================

SELECT 
    COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'fact_sales';


CREATE VIEW v_weekly_revenue_by_category AS
SELECT 
    t.week_id,
    t.week_start_date,
    t.year,
    t.quarter,
    p.category,

    SUM(TRY_CAST(s.revenue_ngn AS decimal(18,2))) AS total_revenue,
    SUM(TRY_CAST(s.units_sold AS int)) AS total_units,
    SUM(TRY_CAST(s.cost_of_goods_sold AS decimal(18,2))) AS total_cogs,

    SUM(
        TRY_CAST(s.revenue_ngn AS decimal(18,2)) -
        TRY_CAST(s.cost_of_goods_sold AS decimal(18,2))
    ) AS gross_profit,

    ROUND(
        100.0 *
        SUM(
            TRY_CAST(s.revenue_ngn AS decimal(18,2)) -
            TRY_CAST(s.cost_of_goods_sold AS decimal(18,2))
        ) /
        NULLIF(SUM(TRY_CAST(s.revenue_ngn AS decimal(18,2))), 0),
        2
    ) AS gross_margin_pct
FROM fact_sales s
JOIN dim_product p ON s.product_id = p.product_id
JOIN dim_time t ON s.week_id = t.week_id
GROUP BY 
    t.week_id, 
    t.week_start_date, 
    t.year, 
    t.quarter, 
    p.category;

CREATE OR ALTER VIEW v_regional_performance AS
SELECT 
    g.region_name,
    COUNT(DISTINCT s.week_id) AS weeks_of_data,

    SUM(TRY_CAST(s.revenue_ngn AS decimal(18,2))) AS total_revenue,
    SUM(TRY_CAST(s.units_sold AS int)) AS total_units,

    ROUND(
        AVG(TRY_CAST(s.revenue_ngn AS decimal(18,2))),
        2
    ) AS avg_transaction_revenue
FROM fact_sales s
JOIN dim_geography g 
    ON s.region_id = g.region_id
GROUP BY 
    g.region_id, 
    g.region_name;


CREATE OR ALTER VIEW v_promotional_effectiveness AS
SELECT 
    p.promo_id,
    p.promo_type,
    p.discount_percentage,
    pr.category,

    SUM(TRY_CAST(s.revenue_ngn AS decimal(18,2))) AS promo_revenue,
    SUM(TRY_CAST(s.units_sold AS int)) AS promo_units,

    SUM(
        TRY_CAST(s.units_sold AS int) -
        TRY_CAST(s.baseline_demand AS int)
    ) AS incremental_units,

    TRY_CAST(p.promo_cost_ngn AS decimal(18,2)) AS promo_cost_ngn,

    ROUND(
        SUM(TRY_CAST(s.revenue_ngn AS decimal(18,2))) /
        NULLIF(TRY_CAST(p.promo_cost_ngn AS decimal(18,2)), 0),
        2
    ) AS roi
FROM fact_promotions p
JOIN fact_sales s 
    ON s.product_id = p.product_id
   AND s.region_id = p.region_id
   AND s.week_id BETWEEN p.promo_start_week AND p.promo_end_week
JOIN dim_product pr 
    ON p.product_id = pr.product_id
GROUP BY 
    p.promo_id,
    p.promo_type,
    p.discount_percentage,
    pr.category,
    p.promo_cost_ngn
HAVING 
    SUM(
        TRY_CAST(s.units_sold AS int) -
        TRY_CAST(s.baseline_demand AS int)
    ) > 0;


CREATE OR ALTER VIEW v_inventory_health AS
SELECT 
    p.product_name,
    p.category,
    g.region_name,

    SUM(TRY_CAST(i.stockout_days AS int)) AS total_stockout_days,

    ROUND(
        AVG(TRY_CAST(i.closing_stock_units AS int)),
        0
    ) AS avg_closing_stock,

    SUM(
        TRY_CAST(i.inventory_holding_cost_ngn AS decimal(18,2))
    ) AS total_holding_cost
FROM fact_inventory i
JOIN dim_product p 
    ON i.product_id = p.product_id
JOIN dim_geography g 
    ON i.region_id = g.region_id
GROUP BY 
    p.product_id,
    p.product_name,
    p.category,
    g.region_id,
    g.region_name;


CREATE OR ALTER VIEW v_seasonal_performance AS
SELECT 
    t.season,
    t.festive_period,
    p.category,

    COUNT(DISTINCT s.week_id) AS weeks,

    SUM(TRY_CAST(s.revenue_ngn AS decimal(18,2))) AS total_revenue,

    ROUND(
        AVG(TRY_CAST(s.revenue_ngn AS decimal(18,2))),
        2
    ) AS avg_weekly_revenue,

    SUM(TRY_CAST(s.units_sold AS int)) AS total_units
FROM fact_sales s
JOIN dim_time t 
    ON s.week_id = t.week_id
JOIN dim_product p 
    ON s.product_id = p.product_id
GROUP BY 
    t.season,
    t.festive_period,
    p.category;
