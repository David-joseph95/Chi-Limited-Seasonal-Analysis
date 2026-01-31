"""
CHI LIMITED - DATA GENERATION SCRIPT
Generates 156 weeks of realistic sales, inventory, and promotional data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

print("="*80)
print("CHI LIMITED - DATA GENERATION STARTING...")
print("="*80)
print()

# ============================================================================
# CONFIGURATION
# ============================================================================

START_DATE = datetime(2022, 1, 3)  # First Monday of 2022
NUM_WEEKS = 156  # 3 years

# Product catalog (42 SKUs)
PRODUCTS = [
    # Juice Category (22 SKUs)
    ('JC-CV100-OR-200', 'Chivita 100% Orange 200ml', 'Chivita', 'Juice', 200, 'Tetra', 'Family', 400, 0.58),
    ('JC-CV100-OR-500', 'Chivita 100% Orange 500ml', 'Chivita', 'Juice', 500, 'Tetra', 'Family', 850, 0.56),
    ('JC-CV100-OR-1L', 'Chivita 100% Orange 1L', 'Chivita', 'Juice', 1000, 'Tetra', 'Family', 1500, 0.55),
    ('JC-CV100-AP-500', 'Chivita 100% Apple 500ml', 'Chivita', 'Juice', 500, 'Tetra', 'Premium', 900, 0.57),
    ('JC-CV100-PI-500', 'Chivita 100% Pineapple 500ml', 'Chivita', 'Juice', 500, 'Tetra', 'Family', 880, 0.56),
    ('JC-CV100-MX-1L', 'Chivita 100% Mixed Fruit 1L', 'Chivita', 'Juice', 1000, 'Tetra', 'Family', 1550, 0.55),
    ('JC-CVACT-MN-500', 'Chivita Active Mango 500ml', 'Chivita', 'Juice', 500, 'Tetra', 'Health', 800, 0.58),
    ('JC-CVEXO-GU-330', 'Chivita Exotic Guava 330ml Can', 'Chivita', 'Juice', 330, 'Can', 'Premium', 650, 0.60),
    ('JC-HAPPY-OR-200', 'Happy Hour Orange 200ml', 'Chivita', 'Juice', 200, 'Tetra', 'Kids', 280, 0.60),
    ('JC-CAPRI-OR-200', 'Capri-Sun Orange 200ml Pouch', 'Chivita', 'Juice', 200, 'Pouch', 'Kids', 350, 0.62),
    
    # Dairy Category (20 SKUs)
    ('DR-HOLYO-ST-90', 'Hollandia Yoghurt Strawberry 90ml Cup', 'Hollandia', 'Dairy', 90, 'Cup', 'Kids', 200, 0.62),
    ('DR-HOLYO-ST-500', 'Hollandia Yoghurt Strawberry 500ml Bottle', 'Hollandia', 'Dairy', 500, 'Bottle', 'Family', 750, 0.58),
    ('DR-HOLYO-ST-1L', 'Hollandia Yoghurt Strawberry 1L Carton', 'Hollandia', 'Dairy', 1000, 'Carton', 'Family', 1350, 0.56),
    ('DR-HOLMK-FC-500', 'Hollandia UHT Milk Full Cream 500ml', 'Hollandia', 'Dairy', 500, 'Tetra', 'Family', 750, 0.60),
    ('DR-HOLMK-FC-1L', 'Hollandia UHT Milk Full Cream 1L', 'Hollandia', 'Dairy', 1000, 'Tetra', 'Family', 1400, 0.58),
    ('DR-HOLEVP-400', 'Hollandia Evaporated Milk 400ml Can', 'Hollandia', 'Dairy', 400, 'Can', 'Family', 850, 0.59),
    ('DR-HOLSOY-OR-500', 'Hollandia Soya Milk Original 500ml', 'Hollandia', 'Dairy', 500, 'Tetra', 'Health', 700, 0.57),
    ('DR-CHIMLT-330', 'Chivita Smart Malt 330ml Bottle', 'CHI', 'Dairy', 330, 'Bottle', 'Kids', 500, 0.61),
    
    # Snacks Category (6 SKUs) - Add more to reach 42 total
    ('SN-SUPBT-BF', 'SuperBite Premium Beef Sausage Roll', 'CHI', 'Snacks', 0, 'Pack', 'Family', 450, 0.65),
    ('SN-BEEFE-MP', 'Beefie Meat Pie', 'CHI', 'Snacks', 0, 'Pack', 'Family', 380, 0.66),
]

# Add more products to reach 42 (filling gaps)
PRODUCTS.extend([
    ('JC-CV100-OR-315', 'Chivita 100% Orange 315ml', 'Chivita', 'Juice', 315, 'Tetra', 'Family', 600, 0.57),
    ('JC-CVACT-OC-500', 'Chivita Active Orange-Carrot-Mango 500ml', 'Chivita', 'Juice', 500, 'Tetra', 'Health', 820, 0.58),
    ('JC-CVEXO-LY-330', 'Chivita Exotic Lychee 330ml Can', 'Chivita', 'Juice', 330, 'Can', 'Premium', 680, 0.60),
    ('JC-CVEXO-PA-330', 'Chivita Exotic Passion Fruit 330ml Can', 'Chivita', 'Juice', 330, 'Can', 'Premium', 670, 0.60),
    ('JC-HAPPY-AP-200', 'Happy Hour Apple 200ml', 'Chivita', 'Juice', 200, 'Tetra', 'Kids', 280, 0.60),
    ('JC-HAPPY-TR-315', 'Happy Hour Tropical 315ml', 'Chivita', 'Juice', 315, 'Tetra', 'Kids', 400, 0.59),
    ('JC-CVTEA-LE-330', 'Chivita Ice Tea Lemon 330ml Can', 'Chivita', 'Juice', 330, 'Can', 'Youth', 450, 0.61),
    ('JC-CVTEA-PE-330', 'Chivita Ice Tea Peach 330ml Can', 'Chivita', 'Juice', 330, 'Can', 'Youth', 450, 0.61),
    ('JC-CAPRI-SA-200', 'Capri-Sun Safari 200ml Pouch', 'Chivita', 'Juice', 200, 'Pouch', 'Kids', 350, 0.62),
    ('JC-CAPRI-CH-200', 'Capri-Sun Cherry 200ml Pouch', 'Chivita', 'Juice', 200, 'Pouch', 'Kids', 350, 0.62),
    ('JC-CAPRI-MV-200', 'Capri-Sun Multivitamin 200ml Pouch', 'Chivita', 'Juice', 200, 'Pouch', 'Kids', 370, 0.62),
    ('JC-CVACT-MN-315', 'Chivita Active Mango 315ml', 'Chivita', 'Juice', 315, 'Tetra', 'Health', 550, 0.58),
    
    ('DR-HOLYO-VA-315', 'Hollandia Yoghurt Vanilla 315ml Bottle', 'Hollandia', 'Dairy', 315, 'Bottle', 'Family', 500, 0.60),
    ('DR-HOLYO-VA-1L', 'Hollandia Yoghurt Vanilla 1L Carton', 'Hollandia', 'Dairy', 1000, 'Carton', 'Family', 1300, 0.56),
    ('DR-HOLYO-NA-500', 'Hollandia Yoghurt Natural 500ml Bottle', 'Hollandia', 'Dairy', 500, 'Bottle', 'Health', 780, 0.58),
    ('DR-HOLYO-PI-1L', 'Hollandia Yoghurt Pineapple 1L Carton', 'Hollandia', 'Dairy', 1000, 'Carton', 'Family', 1380, 0.56),
    ('DR-HOLMK-FC-190', 'Hollandia UHT Milk Full Cream 190ml', 'Hollandia', 'Dairy', 190, 'Tetra', 'Kids', 320, 0.61),
    ('DR-HOLMK-LF-500', 'Hollandia UHT Milk Low Fat 500ml', 'Hollandia', 'Dairy', 500, 'Tetra', 'Health', 800, 0.59),
    ('DR-HOLMK-SK-500', 'Hollandia UHT Milk Skimmed 500ml', 'Hollandia', 'Dairy', 500, 'Tetra', 'Health', 820, 0.59),
    ('DR-HOLMK-LT-500', 'Hollandia UHT Milk Lactose-Free 500ml', 'Hollandia', 'Dairy', 500, 'Tetra', 'Health', 950, 0.58),
    ('DR-HOLEVP-160', 'Hollandia Evaporated Milk 160ml Can', 'Hollandia', 'Dairy', 160, 'Can', 'Family', 380, 0.60),
    ('DR-HOLSOY-VA-500', 'Hollandia Soya Milk Vanilla 500ml', 'Hollandia', 'Dairy', 500, 'Tetra', 'Health', 700, 0.57),
    ('DR-HOLSOY-OR-1L', 'Hollandia Soya Milk Original 1L', 'Hollandia', 'Dairy', 1000, 'Tetra', 'Health', 1250, 0.56),
    ('DR-HOLSOY-OR-200', 'Hollandia Soya Milk Original 200ml', 'Hollandia', 'Dairy', 200, 'Tetra', 'Health', 350, 0.59),
    
    ('SN-BEEFE-RL', 'Beefie Beef Roll', 'CHI', 'Snacks', 0, 'Pack', 'Family', 380, 0.66),
    ('SN-CHICK-VN', 'CHI Classic Cake Vanilla', 'CHI', 'Snacks', 0, 'Pack', 'Family', 650, 0.64),
    ('SN-CHICK-CH', 'CHI Classic Cake Chocolate', 'CHI', 'Snacks', 0, 'Pack', 'Family', 680, 0.64),
    ('SN-CHICK-BN', 'CHI Classic Cake Banana', 'CHI', 'Snacks', 0, 'Pack', 'Family', 630, 0.65),
])

# Regions (6)
REGIONS = [
    ('RG-LAG', 'Lagos', 4.5, 21.0, 1.0),
    ('RG-SWE', 'South-West', 3.8, 28.5, 0.85),
    ('RG-SEA', 'South-East', 3.2, 18.2, 0.75),
    ('RG-SSO', 'South-South', 3.0, 27.8, 0.80),
    ('RG-NCE', 'North-Central', 2.8, 22.1, 0.70),
    ('RG-NOR', 'North', 2.3, 35.4, 0.60),
]

CHANNELS = ['Modern_Trade', 'Traditional_Trade']

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_season(month):
    """Determine Nigerian season"""
    if month in [11, 12, 1, 2]:
        return 'Harmattan'
    elif month in [3, 4, 5, 6, 7]:
        return 'Hot_Dry'
    else:
        return 'Rainy'

def get_festive_period(date_obj):
    """Determine festive period"""
    year = date_obj.year
    month = date_obj.month
    
    # Simplified festive periods
    if year == 2022:
        if month == 4:
            return 'Ramadan'
        elif month == 5 and date_obj.day <= 10:
            return 'Eid'
        elif month == 9:
            return 'Back_to_School'
        elif month == 12 and date_obj.day >= 18:
            return 'Christmas'
    elif year == 2023:
        if month == 3 and date_obj.day >= 23:
            return 'Ramadan'
        elif month == 4 and date_obj.day <= 21:
            return 'Ramadan'
        elif month == 4 and 21 < date_obj.day <= 28:
            return 'Eid'
        elif month == 9:
            return 'Back_to_School'
        elif month == 12 and date_obj.day >= 18:
            return 'Christmas'
    elif year == 2024:
        if month == 3 and date_obj.day >= 11:
            return 'Ramadan'
        elif month == 4 and date_obj.day <= 9:
            return 'Ramadan'
        elif month == 4 and 10 <= date_obj.day <= 17:
            return 'Eid'
        elif month == 9:
            return 'Back_to_School'
        elif month == 12 and date_obj.day >= 18:
            return 'Christmas'
    
    return 'Regular'

def apply_inflation(base_price, year):
    """Apply Nigerian inflation"""
    rates = {2022: 1.00, 2023: 1.18, 2024: 1.40}
    return round(base_price * rates.get(year, 1.0), 2)

def add_noise(value, level='medium'):
    """Add realistic market noise"""
    ranges = {
        'low': (0.90, 1.10),
        'medium': (0.80, 1.20),
        'high': (0.65, 1.35)
    }
    low, high = ranges[level]
    return int(value * random.uniform(low, high))

# ============================================================================
# TABLE 1: DIM_PRODUCT
# ============================================================================

print("📦 Generating DIM_PRODUCT...")
product_data = []
for p in PRODUCTS:
    product_data.append({
        'product_id': p[0],
        'product_name': p[1],
        'brand': p[2],
        'category': p[3],
        'pack_size_ml': p[4],
        'pack_format': p[5],
        'target_segment': p[6],
        'unit_price_ngn_2024': p[7],
        'cogs_percentage': p[8]
    })

df_product = pd.DataFrame(product_data)
print(f"   ✓ {len(df_product)} products created")

# ============================================================================
# TABLE 2: DIM_GEOGRAPHY
# ============================================================================

print("🗺️  Generating DIM_GEOGRAPHY...")
geography_data = []
for r in REGIONS:
    geography_data.append({
        'region_id': r[0],
        'region_name': r[1],
        'urbanization_index': r[2],
        'population_millions': r[3],
        'wealth_index': r[4]
    })

df_geography = pd.DataFrame(geography_data)
print(f"   ✓ {len(df_geography)} regions created")

# ============================================================================
# TABLE 3: DIM_TIME
# ============================================================================

print("📅 Generating DIM_TIME...")
time_data = []
for week_num in range(NUM_WEEKS):
    week_start = START_DATE + timedelta(weeks=week_num)
    week_end = week_start + timedelta(days=6)
    
    time_data.append({
        'week_id': f"{week_start.year}-W{week_start.isocalendar()[1]:02d}",
        'week_start_date': week_start.strftime('%Y-%m-%d'),
        'week_end_date': week_end.strftime('%Y-%m-%d'),
        'month_name': week_start.strftime('%B'),
        'month_number': week_start.month,
        'quarter': f"Q{(week_start.month-1)//3 + 1}",
        'year': week_start.year,
        'week_of_year': week_start.isocalendar()[1],
        'is_holiday_week': 1 if get_festive_period(week_start) != 'Regular' else 0,
        'season': get_season(week_start.month),
        'festive_period': get_festive_period(week_start)
    })

df_time = pd.DataFrame(time_data)
print(f"   ✓ {len(df_time)} weeks created")

# ============================================================================
# TABLE 4: FACT_PROMOTIONS
# ============================================================================

print("🎯 Generating FACT_PROMOTIONS...")
promotions = []
promo_id = 1

for year in [2022, 2023, 2024]:
    # Generate 80-120 promos per year
    for _ in range(random.randint(80, 120)):
        product = random.choice(PRODUCTS)
        region = random.choice(REGIONS)
        channel = random.choice(CHANNELS)
        
        # Random week in year
        start_week_idx = random.randint(0, 51)  # Week 0-51 of year
        year_weeks = df_time[df_time['year'] == year]
        if start_week_idx >= len(year_weeks):
            continue
            
        promo_start_week = year_weeks.iloc[start_week_idx]['week_id']
        duration = random.choice([1, 2, 2, 3, 4])  # Weighted toward shorter
        
        # Find end week
        end_idx = start_week_idx + duration - 1
        if end_idx >= len(year_weeks):
            end_idx = len(year_weeks) - 1
        promo_end_week = year_weeks.iloc[end_idx]['week_id']
        
        # Promo type
        promo_type = random.choice(['Price_Off', 'Price_Off', 'BOGOF', 'Bundle', 'Trade_Promo'])
        
        if promo_type == 'Price_Off':
            discount = random.choice([10, 15, 20, 25, 30])
        elif promo_type == 'BOGOF':
            discount = 50
        elif promo_type == 'Bundle':
            discount = random.choice([15, 20])
        else:
            discount = random.choice([5, 8, 10, 12])
        
        # Cost calculation
        expected_volume = random.randint(1000, 5000) * duration
        promo_cost = (product[7] * discount / 100) * expected_volume * random.uniform(0.8, 1.2)
        
        promotions.append({
            'promo_id': f"PROMO-{promo_id:04d}",
            'product_id': product[0],
            'region_id': region[0],
            'channel_id': channel,
            'promo_type': promo_type,
            'discount_percentage': discount,
            'promo_start_week': promo_start_week,
            'promo_end_week': promo_end_week,
            'promo_cost_ngn': round(promo_cost, 2),
            'incremental_volume_target': int(expected_volume * 0.4)
        })
        promo_id += 1

df_promotions = pd.DataFrame(promotions)
print(f"   ✓ {len(df_promotions)} promotional campaigns created")

# ============================================================================
# TABLE 5: FACT_SALES (Main transaction data)
# ============================================================================

print("💰 Generating FACT_SALES (this takes 2-3 minutes)...")
sales_data = []
transaction_id = 1

for week_idx, week_row in df_time.iterrows():
    week_id = week_row['week_id']
    year = week_row['year']
    season = week_row['season']
    festive = week_row['festive_period']
    
    # Seasonal multipliers
    season_mult = {'Hot_Dry': 1.35, 'Rainy': 0.85, 'Harmattan': 1.05}
    festive_mult = {'Ramadan': 1.25, 'Eid': 1.65, 'Christmas': 1.80, 
                    'Back_to_School': 1.40, 'Regular': 1.00}
    yoy_growth = {2022: 1.00, 2023: 1.12, 2024: 1.26}
    
    for product in PRODUCTS:
        for region in REGIONS:
            for channel in CHANNELS:
                # Base demand
                category_base = {'Juice': random.randint(800, 1500), 
                                'Dairy': random.randint(600, 1200), 
                                'Snacks': random.randint(400, 800)}
                base_demand = category_base[product[3]]
                
                # Adjustments
                base_demand *= region[4]  # Wealth index
                if region[0] == 'RG-LAG':
                    base_demand *= 1.6
                
                if channel == 'Modern_Trade':
                    base_demand *= 0.42
                else:
                    base_demand *= 0.98
                
                # Apply seasonality
                demand = base_demand * season_mult[season] * festive_mult[festive] * yoy_growth[year]
                
                # Category-specific boosts
                if product[3] == 'Juice' and season == 'Hot_Dry':
                    demand *= 1.25
                if product[6] == 'Kids' and festive == 'Back_to_School':
                    demand *= 1.50
                
                # Check for promotions
                active_promos = df_promotions[
                    (df_promotions['product_id'] == product[0]) &
                    (df_promotions['region_id'] == region[0]) &
                    (df_promotions['channel_id'] == channel) &
                    (df_promotions['promo_start_week'] <= week_id) &
                    (df_promotions['promo_end_week'] >= week_id)
                ]
                
                promo_discount = 0
                if len(active_promos) > 0:
                    promo = active_promos.iloc[0]
                    uplift = 1 + (promo['discount_percentage'] / 100) * random.uniform(1.5, 2.5)
                    demand *= uplift
                    unit_price = apply_inflation(product[7], year)
                    promo_discount = unit_price * (promo['discount_percentage'] / 100)
                
                # Add noise
                noise_level = 'high' if festive in ['Eid', 'Christmas'] else 'medium'
                units_sold = add_noise(demand, noise_level)
                units_sold = max(0, units_sold)
                
                # Financial calculations
                unit_price = apply_inflation(product[7], year)
                revenue = units_sold * unit_price
                cogs = revenue * product[8]
                
                sales_data.append({
                    'transaction_id': f"TXN-{transaction_id:06d}",
                    'week_id': week_id,
                    'product_id': product[0],
                    'region_id': region[0],
                    'channel_id': channel,
                    'units_sold': units_sold,
                    'revenue_ngn': round(revenue, 2),
                    'cost_of_goods_sold': round(cogs, 2),
                    'promo_discount_ngn': round(promo_discount * units_sold, 2),
                    'baseline_demand': int(base_demand)
                })
                transaction_id += 1
    
    if (week_idx + 1) % 20 == 0:
        print(f"   ⏳ {week_idx + 1}/{NUM_WEEKS} weeks processed...")

df_sales = pd.DataFrame(sales_data)
print(f"   ✓ {len(df_sales):,} sales transactions created")

# ============================================================================
# TABLE 6: FACT_INVENTORY
# ============================================================================

print("📦 Generating FACT_INVENTORY...")
inventory_data = []
inventory_tracker = {}

for week_idx, week_row in df_time.iterrows():
    week_id = week_row['week_id']
    
    for product in PRODUCTS:
        for region in REGIONS:
            # Get sales
            week_sales = df_sales[
                (df_sales['week_id'] == week_id) &
                (df_sales['product_id'] == product[0]) &
                (df_sales['region_id'] == region[0])
            ]['units_sold'].sum()
            
            # Opening stock
            if week_idx == 0:
                opening_stock = int(week_sales * random.uniform(3, 6))
            else:
                key = (product[0], region[0])
                opening_stock = inventory_tracker.get(key, int(week_sales * 4))
            
            # Replenishment
            if opening_stock < week_sales * 2.5:
                replenishment = int(week_sales * random.uniform(4, 6) - opening_stock)
            else:
                replenishment = 0
            
            closing_stock = max(0, opening_stock + replenishment - week_sales)
            
            # Stockouts
            if closing_stock <= 0:
                stockout_days = random.randint(1, 4)
            elif closing_stock < week_sales * 0.5:
                stockout_days = random.randint(1, 2) if random.random() < 0.3 else 0
            else:
                stockout_days = 0
            
            # Holding cost
            avg_inv = (opening_stock + closing_stock) / 2
            holding_cost = avg_inv * product[7] * product[8] * (0.18 / 52)
            
            inventory_data.append({
                'week_id': week_id,
                'product_id': product[0],
                'region_id': region[0],
                'opening_stock_units': int(opening_stock),
                'closing_stock_units': int(closing_stock),
                'stockout_days': stockout_days,
                'inventory_holding_cost_ngn': round(holding_cost, 2)
            })
            
            inventory_tracker[(product[0], region[0])] = closing_stock

df_inventory = pd.DataFrame(inventory_data)
print(f"   ✓ {len(df_inventory):,} inventory records created")

# ============================================================================
# SAVE TO CSV
# ============================================================================

print()
print("💾 Saving to CSV files...")

# Create data/raw directory if it doesn't exist
output_dir = 'data/raw/'
os.makedirs(output_dir, exist_ok=True)

df_product.to_csv(f'{output_dir}dim_product.csv', index=False)
df_geography.to_csv(f'{output_dir}dim_geography.csv', index=False)
df_time.to_csv(f'{output_dir}dim_time.csv', index=False)
df_promotions.to_csv(f'{output_dir}fact_promotions.csv', index=False)
df_sales.to_csv(f'{output_dir}fact_sales.csv', index=False)
df_inventory.to_csv(f'{output_dir}fact_inventory.csv', index=False)

print("   ✓ All files saved!")

# ============================================================================
# SUMMARY
# ============================================================================

print()
print("="*80)
print("✅ DATA GENERATION COMPLETE!")
print("="*80)
print()
print(f"📊 Summary:")
print(f"   • Products: {len(df_product)}")
print(f"   • Regions: {len(df_geography)}")
print(f"   • Weeks: {len(df_time)}")
print(f"   • Promotions: {len(df_promotions)}")
print(f"   • Sales Transactions: {len(df_sales):,}")
print(f"   • Inventory Records: {len(df_inventory):,}")
print()
print(f"💰 Total Revenue (3 years): ₦{df_sales['revenue_ngn'].sum():,.2f}")
print(f"📈 Avg Weekly Revenue: ₦{df_sales.groupby('week_id')['revenue_ngn'].sum().mean():,.2f}")
print()
print("📁 Files created in data/raw/:")
print("   1. dim_product.csv")
print("   2. dim_geography.csv")
print("   3. dim_time.csv")
print("   4. fact_promotions.csv")
print("   5. fact_sales.csv")
print("   6. fact_inventory.csv")
print()
print("🎉 Ready for Day 2: SQL Database Setup!")
print("="*80)