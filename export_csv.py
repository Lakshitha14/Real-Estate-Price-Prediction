import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

DB_PASSWORD = quote_plus("your_password_here")
engine = create_engine(f"mysql+pymysql://root:{DB_PASSWORD}@localhost/real_estate_db")

df = pd.read_sql("SELECT * FROM properties", con=engine)
df.to_csv("data/properties_clean.csv", index=False)

print(f"Exported {len(df)} rows to data/properties_clean.csv")