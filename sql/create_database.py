"""
CHI LIMITED - SQL DATABASE CREATION SCRIPT
Creates SQLite database with star schema
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

print("="*80)
print("CHI LIMITED - DATABASE CREATION STARTING...")
print("="*80)
print()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Database file location
DB_PATH = 'chi_limited.db'

# CSV files location
DATA_DIR = 'data/raw/'

# ============================================================================
# STEP 1: CREATE DATABASE CONNECTION
# ============================================================================

print("📂 Creating database connection...")

# Delete existing database if it exists (fresh start)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"   ✓ Removed old database file")

# Create new connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"   ✓ Connected to: {DB_PATH}")
print()

# ============================================================================
# STEP 2: CREATE TABLES (Star Schema)
# ============================================================================

print("🏗️  Creating database tables...")

# --- DIM_PRODUCT ---
cursor.execute("""
    CREATE TABLE dim_product (
        product_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        brand TEXT NOT NULL,
        category TEXT NOT NULL,
        pack_size_ml INTEGER,
        pack_format TEXT,
        target_segment TEXT,
        unit_price_ngn_2024 REAL NOT NULL,
        cogs_percentage REAL
    )
""")
print("   ✓ Created table: dim_product")

# --- DIM_GEOGRAPHY ---
cursor.execute("""
    CREATE TABLE dim_geography (
        region_id TEXT PRIMARY KEY,
        region_name TEXT NOT NULL,
        urbanization_index REAL,
        population_millions REAL,
        wealth_index REAL
    )
""")
print("   ✓ Created table: dim_geography")

# --- DIM_TIME ---
cursor.execute("""
    CREATE TABLE dim_time (
        week_id TEXT PRIMARY KEY,
        week_start_date TEXT NOT NULL,
        week_end_date TEXT NOT NULL,
        month_name TEXT NOT NULL,
        month_number INTEGER,
        quarter TEXT NOT NULL,
        year INTEGER NOT NULL,
        week_of_year INTEGER NOT NULL,
        is_holiday_week INTEGER DEFAULT 0,
        season TEXT NOT NULL,
        festive_period TEXT DEFAULT 'Regular'
    )
""")
print("   ✓ Created table: dim_time")

# --- FACT_SALES ---
cursor.execute("""
    CREATE TABLE fact_sales (
        transaction_id TEXT PRIMARY KEY,
        week_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        region_id TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        units_sold INTEGER NOT NULL DEFAULT 0,
        revenue_ngn REAL NOT NULL DEFAULT 0,
        cost_of_goods_sold REAL NOT NULL DEFAULT 0,
        promo_discount_ngn REAL DEFAULT 0,
        baseline_demand INTEGER,
        FOREIGN KEY (week_id) REFERENCES dim_time(week_id),
        FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
        FOREIGN KEY (region_id) REFERENCES dim_geography(region_id)
    )
""")
print("   ✓ Created table: fact_sales")

# --- FACT_PROMOTIONS ---
cursor.execute("""
    CREATE TABLE fact_promotions (
        promo_id TEXT PRIMARY KEY,
        product_id TEXT NOT NULL,
        region_id TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        promo_type TEXT NOT NULL,
        discount_percentage REAL NOT NULL,
        promo_start_week TEXT NOT NULL,
        promo_end_week TEXT NOT NULL,
        promo_cost_ngn REAL NOT NULL DEFAULT 0,
        incremental_volume_target INTEGER,
        FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
        FOREIGN KEY (region_id) REFERENCES dim_geography(region_id)
    )
""")
print("   ✓ Created table: fact_promotions")

# --- FACT_INVENTORY ---
cursor.execute("""
    CREATE TABLE fact_inventory (
        inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
        week_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        region_id TEXT NOT NULL,
        opening_stock_units INTEGER NOT NULL DEFAULT 0,
        closing_stock_units INTEGER NOT NULL DEFAULT 0,
        stockout_days INTEGER DEFAULT 0,
        inventory_holding_cost_ngn REAL DEFAULT 0,
        FOREIGN KEY (week_id) REFERENCES dim_time(week_id),
        FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
        FOREIGN KEY (region_id) REFERENCES dim_geography(region_id)
    )
""")
print("   ✓ Created table: fact_inventory")

# Commit table creation
conn.commit()
print()

# ============================================================================
# STEP 3: CREATE INDEXES (For faster queries)
# ============================================================================

print("⚡ Creating indexes for performance...")

indexes = [
    "CREATE INDEX idx_product_category ON dim_product(category)",
    "CREATE INDEX idx_time_year ON dim_time(year)",
    "CREATE INDEX idx_time_festive ON dim_time(festive_period)",
    "CREATE INDEX idx_sales_week ON fact_sales(week_id)",
    "CREATE INDEX idx_sales_product ON fact_sales(product_id)",
    "CREATE INDEX idx_sales_region ON fact_sales(region_id)",
    "CREATE INDEX idx_promo_product ON fact_promotions(product_id)",
    "CREATE INDEX idx_inventory_week ON fact_inventory(week_id)",
]

for idx_sql in indexes:
    cursor.execute(idx_sql)
    
conn.commit()
print(f"   ✓ Created {len(indexes)} indexes")
print()

# ============================================================================
# STEP 4: LOAD DATA FROM CSV FILES
# ============================================================================

print("📥 Loading data from CSV files...")

# Helper function to load CSV
def load_csv_to_table(csv_file, table_name):
    """Load CSV file into SQL table"""
    csv_path = os.path.join(DATA_DIR, csv_file)
    
    if not os.path.exists(csv_path):
        print(f"   ❌ File not found: {csv_path}")
        return 0
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Load to SQL
    df.to_sql(table_name, conn, if_exists='append', index=False)
    
    row_count = len(df)
    print(f"   ✓ Loaded {row_count:,} rows into {table_name}")
    return row_count

# Load all tables
total_rows = 0
total_rows += load_csv_to_table('dim_product.csv', 'dim_product')
total_rows += load_csv_to_table('dim_geography.csv', 'dim_geography')
total_rows += load_csv_to_table('dim_time.csv', 'dim_time')
total_rows += load_csv_to_table('fact_promotions.csv', 'fact_promotions')
total_rows += load_csv_to_table('fact_sales.csv', 'fact_sales')
total_rows += load_csv_to_table('fact_inventory.csv', 'fact_inventory')

print()
print(f"   📊 Total rows loaded: {total_rows:,}")
print()

# ============================================================================
# STEP 5: CREATE ANALYTICAL VIEWS
# ============================================================================

print("👁️  Creating analytical views...")

# --- View 1: Weekly Revenue by Category ---
cursor.execute("""
    CREATE VIEW v_weekly_revenue_by_category AS
    SELECT 
        t.week_id,
        t.week_start_date,
        t.year,
        t.quarter,
        p.category,
        SUM(s.revenue_ngn) AS total_revenue,
        SUM(s.units_sold) AS total_units,
        SUM(s.cost_of_goods_sold) AS total_cogs,
        SUM(s.revenue_ngn - s.cost_of_goods_sold) AS gross_profit,
        ROUND(100.0 * SUM(s.revenue_ngn - s.cost_of_goods_sold) / 
              NULLIF(SUM(s.revenue_ngn), 0), 2) AS gross_margin_pct
    FROM fact_sales s
    JOIN dim_product p ON s.product_id = p.product_id
    JOIN dim_time t ON s.week_id = t.week_id
    GROUP BY t.week_id, t.week_start_date, t.year, t.quarter, p.category
    ORDER BY t.week_start_date, p.category
""")
print("   ✓ Created view: v_weekly_revenue_by_category")

# --- View 2: Regional Performance ---
cursor.execute("""
    CREATE VIEW v_regional_performance AS
    SELECT 
        g.region_name,
        COUNT(DISTINCT s.week_id) AS weeks_of_data,
        SUM(s.revenue_ngn) AS total_revenue,
        SUM(s.units_sold) AS total_units,
        ROUND(AVG(s.revenue_ngn), 2) AS avg_transaction_revenue
    FROM fact_sales s
    JOIN dim_geography g ON s.region_id = g.region_id
    GROUP BY g.region_id, g.region_name
    ORDER BY total_revenue DESC
""")
print("   ✓ Created view: v_regional_performance")

# --- View 3: Promotional Effectiveness ---
cursor.execute("""
    CREATE VIEW v_promotional_effectiveness AS
    SELECT 
        p.promo_id,
        p.promo_type,
        p.discount_percentage,
        pr.category,
        SUM(s.revenue_ngn) AS promo_revenue,
        SUM(s.units_sold) AS promo_units,
        SUM(s.units_sold - s.baseline_demand) AS incremental_units,
        p.promo_cost_ngn,
        ROUND(SUM(s.revenue_ngn) / NULLIF(p.promo_cost_ngn, 0), 2) AS roi
    FROM fact_promotions p
    JOIN fact_sales s ON s.product_id = p.product_id 
        AND s.region_id = p.region_id 
        AND s.week_id BETWEEN p.promo_start_week AND p.promo_end_week
    JOIN dim_product pr ON p.product_id = pr.product_id
    GROUP BY p.promo_id, p.promo_type, p.discount_percentage, pr.category, p.promo_cost_ngn
    HAVING incremental_units > 0
    ORDER BY roi DESC
""")
print("   ✓ Created view: v_promotional_effectiveness")

# --- View 4: Inventory Health ---
cursor.execute("""
    CREATE VIEW v_inventory_health AS
    SELECT 
        p.product_name,
        p.category,
        g.region_name,
        SUM(i.stockout_days) AS total_stockout_days,
        ROUND(AVG(i.closing_stock_units), 0) AS avg_closing_stock,
        SUM(i.inventory_holding_cost_ngn) AS total_holding_cost
    FROM fact_inventory i
    JOIN dim_product p ON i.product_id = p.product_id
    JOIN dim_geography g ON i.region_id = g.region_id
    GROUP BY p.product_id, p.product_name, p.category, g.region_id, g.region_name
    ORDER BY total_stockout_days DESC
""")
print("   ✓ Created view: v_inventory_health")

# --- View 5: Seasonal Performance ---
cursor.execute("""
    CREATE VIEW v_seasonal_performance AS
    SELECT 
        t.season,
        t.festive_period,
        p.category,
        COUNT(DISTINCT s.week_id) AS weeks,
        SUM(s.revenue_ngn) AS total_revenue,
        ROUND(AVG(s.revenue_ngn), 2) AS avg_weekly_revenue,
        SUM(s.units_sold) AS total_units
    FROM fact_sales s
    JOIN dim_time t ON s.week_id = t.week_id
    JOIN dim_product p ON s.product_id = p.product_id
    GROUP BY t.season, t.festive_period, p.category
    ORDER BY t.season, p.category, total_revenue DESC
""")
print("   ✓ Created view: v_seasonal_performance")

conn.commit()
print()

# ============================================================================
# STEP 6: VERIFY DATABASE
# ============================================================================

print("✅ Verifying database...")

# Check table row counts
tables = ['dim_product', 'dim_geography', 'dim_time', 'fact_sales', 'fact_promotions', 'fact_inventory']

print()
print("📊 Table Row Counts:")
print("-" * 50)
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"   {table:<25} {count:>10,} rows")

print()

# Test a sample query
cursor.execute("""
    SELECT category, SUM(revenue_ngn) as total_revenue 
    FROM fact_sales s
    JOIN dim_product p ON s.product_id = p.product_id
    GROUP BY category
    ORDER BY total_revenue DESC
""")

results = cursor.fetchall()
print("💰 Revenue by Category:")
print("-" * 50)
for category, revenue in results:
    print(f"   {category:<15} ₦{revenue:>15,.2f}")

print()

# ============================================================================
# STEP 7: CLOSE CONNECTION
# ============================================================================

conn.close()

print("="*80)
print("✅ DATABASE CREATION COMPLETE!")
print("="*80)
print()
print(f"📁 Database saved as: {DB_PATH}")
print(f"📊 Total tables: 6 (3 dimensions + 3 facts)")
print(f"👁️  Total views: 5 (analytical views)")
print(f"⚡ Total indexes: {len(indexes)}")
print()
print("🎉 Ready for Day 3: Exploratory Data Analysis!")
print("="*80)
