"""
CHI LIMITED - SAMPLE ANALYTICAL QUERIES
Practice SQL queries for business insights
"""

import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('chi_limited.db')

print("="*80)
print("CHI LIMITED - ANALYTICAL QUERIES")
print("="*80)
print()

# ============================================================================
# QUERY 1: Top 10 Products by Revenue
# ============================================================================

print("📊 QUERY 1: Top 10 Products by Revenue")
print("-" * 80)

query1 = """
    SELECT 
        p.product_name,
        p.category,
        SUM(s.revenue_ngn) AS total_revenue,
        SUM(s.units_sold) AS total_units
    FROM fact_sales s
    JOIN dim_product p ON s.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
    ORDER BY total_revenue DESC
    LIMIT 10
"""

df1 = pd.read_sql_query(query1, conn)
print(df1.to_string(index=False))
print()

# ============================================================================
# QUERY 2: Revenue by Region and Year
# ============================================================================

print("📊 QUERY 2: Revenue by Region and Year")
print("-" * 80)

query2 = """
    SELECT 
        g.region_name,
        t.year,
        SUM(s.revenue_ngn) AS total_revenue,
        ROUND(AVG(s.revenue_ngn), 2) AS avg_revenue_per_transaction
    FROM fact_sales s
    JOIN dim_geography g ON s.region_id = g.region_id
    JOIN dim_time t ON s.week_id = t.week_id
    GROUP BY g.region_name, t.year
    ORDER BY g.region_name, t.year
"""

df2 = pd.read_sql_query(query2, conn)
print(df2.to_string(index=False))
print()

# ============================================================================
# QUERY 3: Promotional ROI by Type
# ============================================================================

print("📊 QUERY 3: Promotional ROI by Type")
print("-" * 80)

query3 = """
    SELECT 
        promo_type,
        COUNT(*) AS num_campaigns,
        ROUND(AVG(roi), 2) AS avg_roi,
        ROUND(MIN(roi), 2) AS min_roi,
        ROUND(MAX(roi), 2) AS max_roi
    FROM v_promotional_effectiveness
    GROUP BY promo_type
    ORDER BY avg_roi DESC
"""

df3 = pd.read_sql_query(query3, conn)
print(df3.to_string(index=False))
print()

# ============================================================================
# QUERY 4: Seasonal Revenue Patterns
# ============================================================================

print("📊 QUERY 4: Seasonal Revenue Patterns")
print("-" * 80)

query4 = """
    SELECT 
        season,
        festive_period,
        category,
        total_revenue,
        avg_weekly_revenue
    FROM v_seasonal_performance
    WHERE category = 'Juice'
    ORDER BY total_revenue DESC
    LIMIT 10
"""

df4 = pd.read_sql_query(query4, conn)
print(df4.to_string(index=False))
print()

# ============================================================================
# QUERY 5: Products with High Stockout Frequency
# ============================================================================

print("📊 QUERY 5: Products with High Stockout Frequency")
print("-" * 80)

query5 = """
    SELECT 
        product_name,
        region_name,
        total_stockout_days,
        avg_closing_stock,
        total_holding_cost
    FROM v_inventory_health
    WHERE total_stockout_days > 10
    ORDER BY total_stockout_days DESC
    LIMIT 15
"""

df5 = pd.read_sql_query(query5, conn)
print(df5.to_string(index=False))
print()

# ============================================================================
# QUERY 6: Month-over-Month Growth
# ============================================================================

print("📊 QUERY 6: Month-over-Month Growth Rate")
print("-" * 80)

query6 = """
    WITH monthly_revenue AS (
        SELECT 
            t.year,
            t.month_name,
            SUM(s.revenue_ngn) AS revenue
        FROM fact_sales s
        JOIN dim_time t ON s.week_id = t.week_id
        GROUP BY t.year, t.month_name, t.month_number
        ORDER BY t.year, t.month_number
    )
    SELECT 
        year,
        month_name,
        revenue,
        LAG(revenue) OVER (ORDER BY year, month_name) AS prev_month_revenue,
        ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year, month_name)) / 
              NULLIF(LAG(revenue) OVER (ORDER BY year, month_name), 0), 2) AS growth_pct
    FROM monthly_revenue
    ORDER BY year, month_name
"""

df6 = pd.read_sql_query(query6, conn)
print(df6.head(15).to_string(index=False))
print()

# ============================================================================
# QUERY 7: Channel Performance Comparison
# ============================================================================

print("📊 QUERY 7: Modern Trade vs Traditional Trade")
print("-" * 80)

query7 = """
    SELECT 
        channel_id,
        COUNT(DISTINCT product_id) AS num_products,
        SUM(revenue_ngn) AS total_revenue,
        SUM(units_sold) AS total_units,
        ROUND(AVG(revenue_ngn / NULLIF(units_sold, 0)), 2) AS avg_price_per_unit
    FROM fact_sales
    GROUP BY channel_id
"""

df7 = pd.read_sql_query(query7, conn)
print(df7.to_string(index=False))
print()

# Close connection
conn.close()

print("="*80)
print("✅ All queries executed successfully!")
print("="*80)