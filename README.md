# Bengaluru Real Estate Price Prediction
🔗 **Live Demo:** [Open the app](https://real-estate-price-prediction-ag3iefaklunth6perklhvc.streamlit.app/)

## Overview
An end-to-end data analysis and machine learning project predicting residential property prices in Bengaluru, using SQL for data storage/analysis and Python for modeling. Built as a Bengaluru-based student, using local market knowledge to guide analysis choices.

## Tech Stack
- **Database:** MySQL
- **Language:** Python (pandas, scikit-learn, seaborn, matplotlib)
- **ORM/Connection:** SQLAlchemy + PyMySQL

## Dataset
Bengaluru House Price Data (Kaggle, by amitabhajoy) — 13,320 property listings across Bengaluru with features including location, area type, size (BHK), total square footage, bathrooms, balconies, and price (in lakhs INR).

**Note on dataset vintage:** this dataset reflects historical Bengaluru listings. The cleaning pipeline, SQL analysis, and modeling methodology are directly reusable with more recent data (e.g., via live scraping or updated listings) — the goal here was to demonstrate the analytical approach end-to-end.

## Project Pipeline

### 1. Data Cleaning (`load_data.py`)
- Extracted numeric BHK from text ("2 BHK" → 2)
- Parsed `total_sqft` ranges into averaged numeric values
- Removed rows with missing critical fields and unrealistic sqft-per-bedroom ratios
- Loaded cleaned data (12,754 rows) into MySQL

### 2. SQL Analysis (`sql/queries.sql`)
Wrote 6 analytical queries including:
- Average price and price-per-sqft by locality
- Top 10 most expensive localities (min. 5 listings)
- Locality ranking using window functions (`RANK() OVER`)
- BHK distribution across the market

**Key finding:** Sadashiva Nagar, Cunningham Road, and Defence Colony are the highest-priced localities, consistent with their status as established premium central Bengaluru neighborhoods. 2-BHK and 3-BHK properties dominate the market (5,514 and 4,768 listings respectively).

### 3. EDA & Visualization (`notebooks/eda_and_model.ipynb`)
- Price distribution analysis
- Price vs. square footage relationship
- Average price by BHK category
- Outlier removal (extreme BHK values, bath-to-bedroom ratio checks)

### 4. Modeling
Trained a **Random Forest Regressor** to predict property price.

| Version | RMSE (lakhs) | R² Score |
|---|---|---|
| Initial model | 95.40 | 0.6123 |
| After capping top 1% price outliers | **50.44** | **0.7111** |

**Why the improvement mattered:** the top 1% of listings (ultra-luxury properties) were disproportionately hard to predict and skewed error metrics. Capping them improved model reliability for the typical market segment, at the cost of not modeling ultra-luxury properties well — a reasonable trade-off for most practical use cases (e.g., mass-market valuation tools).

### 5. Feature Importance
| Feature | Importance |
|---|---|
| Total Sqft | 67.7% |
| Bathrooms | 8.3% |
| BHK | 5.1% |
| Balcony | 3.9% |
| Specific localities (Malleshwaram, Sadashiva Nagar, etc.) | ~1-2% each |

**Business insight:** property size is by far the dominant price driver, but specific premium localities add a measurable price premium beyond size alone — useful for identifying under/over-valued listings relative to their locality's typical pricing.

## How to Run
```bash
# 1. Set up environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install pandas numpy matplotlib seaborn scikit-learn sqlalchemy pymysql jupyter

# 2. Set up MySQL database
mysql -u root -p
CREATE DATABASE real_estate_db;

# 3. Load and clean data
python load_data.py

# 4. Run SQL analysis
mysql -u root -p real_estate_db
SOURCE sql/queries.sql;

# 5. Run EDA + modeling notebook
# Open notebooks/eda_and_model.ipynb in VS Code/Jupyter and run all cells
```

## Future Improvements
- Incorporate more recent listing data via API/scraping
- Add geographic distance-to-city-center as a feature
- Try gradient boosting models (XGBoost, LightGBM) for comparison
- Deploy as a simple web app for interactive price prediction

## Deployment Note
The deployed demo reads a pre-exported CSV snapshot of the cleaned data, since cloud hosting can't reach a local MySQL database. The full pipeline (MySQL storage + SQL analysis) is in `load_data.py` and `sql/queries.sql`.