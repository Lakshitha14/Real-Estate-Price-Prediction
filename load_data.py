"""
load_data.py
Cleans the Bengaluru House Price dataset and loads it into MySQL (real_estate_db.properties)
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# ---- 1. CONFIG ----
from urllib.parse import quote_plus

DB_USER = "root"
DB_PASSWORD = quote_plus("your_password_here")   # encodes special characters safely
DB_HOST = "localhost"
DB_NAME = "real_estate_db"

# ---- 2. Load raw CSV ----
df = pd.read_csv("data/Bengaluru_House_Data.csv")
print(f"Loaded {len(df)} rows")

# ---- 3. Clean 'size' column -> numeric BHK ----
df["bhk"] = df["size"].str.extract(r"(\d+)").astype(float)

# ---- 4. Clean 'total_sqft' column -> numeric ----
def clean_sqft(x):
    try:
        if "-" in str(x):
            parts = str(x).split("-")
            return (float(parts[0]) + float(parts[1])) / 2
        return float(x)
    except:
        return np.nan

df["total_sqft_clean"] = df["total_sqft"].apply(clean_sqft)

# ---- 5. Drop rows with missing critical values ----
df = df.dropna(subset=["total_sqft_clean", "bhk", "price", "bath", "location"])

# ---- 6. Remove obvious outliers ----
df = df[df["total_sqft_clean"] > 100]
df = df[df["price"] > 0]
df = df[(df["total_sqft_clean"] / df["bhk"]) > 200]

# ---- 7. Select final clean columns ----
final_df = df[[
    "location", "area_type", "availability",
    "total_sqft_clean", "bhk", "bath", "balcony", "price"
]].rename(columns={"total_sqft_clean": "total_sqft"})

final_df["balcony"] = final_df["balcony"].fillna(0)

print(f"Cleaned dataset: {len(final_df)} rows remain")
print(final_df.head())

# ---- 8. Load into MySQL ----
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

final_df.to_sql("properties", con=engine, if_exists="replace", index=False)
print("Data loaded into MySQL table 'properties' successfully.")