import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Page config ----------
st.set_page_config(page_title="Bengaluru Real Estate Explorer", layout="wide")

# ---------- Custom CSS for better UI ----------
st.markdown("""
<style>
    /* Overall background */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Headings */
    h1 {
        color: #1e293b;
        font-weight: 700;
    }
    h2, h3 {
        color: #334155;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    
    /* Success box */
    .stSuccess {
        border-radius: 10px;
    }
    
    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Load model + data (cached so it's fast) ----------
@st.cache_resource
def load_model():
    model = joblib.load("model.pkl")
    columns = joblib.load("model_columns.pkl")
    return model, columns

@st.cache_data
def load_data():
    df = pd.read_csv("data/properties_clean.csv")
    df = df[df['bhk'] <= 10]
    df = df[df['bath'] <= df['bhk'] + 2]
    return df

model, model_columns = load_model()
df = load_data()

# ---------- Simple session-based "login" (demo only, not real auth) ----------
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if st.session_state.user_name is None:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2563eb 0%, #1e293b 100%);
        padding: 60px 40px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 30px;
    ">
        <h1 style="color: white; font-size: 42px; margin-bottom: 10px;">🏠 Bengaluru Real Estate Explorer</h1>
        <p style="color: #cbd5e1; font-size: 18px;">Find your next home, understand fair pricing, and explore the market — powered by real data and machine learning.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("Enter your name to get started", placeholder="e.g. Lakshitha")
        if st.button("Continue →", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                st.rerun()
            else:
                st.warning("Please enter your name")
    st.stop()

# ---------- Sidebar navigation ----------
st.sidebar.title(f"👋 Hi, {st.session_state.user_name}")
st.sidebar.title("🏠 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Search Properties", "Price Predictor", "Market Insights"])

# =========================================================
# PAGE 1: Home
# =========================================================
if page == "Home":
    st.markdown(f"<h1>Welcome back, {st.session_state.user_name} 👋</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 16px;'>Explore Bengaluru's real estate market using real data and machine learning.</p>", unsafe_allow_html=True)
    
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏘️ Listings in Database", f"{len(df):,}")
    col2.metric("📍 Areas Covered", df['location'].nunique())
    col3.metric("💰 Typical Price", f"₹{df['price'].median():.0f} L")
    col4.metric("📐 Avg Price/Sqft", f"₹{(df['price']*100000/df['total_sqft']).mean():.0f}")

    st.write("---")
    st.markdown("### What you can do here")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**🔍 Search Properties**\n\nFilter real listings by locality, BHK, and budget")
    with col2:
        st.info("**🔮 Price Predictor**\n\nGet an ML-based price estimate for any property")
    with col3:
        st.info("**📊 Market Insights**\n\nExplore pricing trends across localities")

if page == "Search Properties":
    st.title("🔍 Search Bengaluru Properties")
    st.write("Filter listings by locality, budget, and BHK to find matching properties.")

    col1, col2, col3 = st.columns(3)
    with col1:
        locations = sorted(df['location'].unique())
        selected_location = st.selectbox("Locality", ["All"] + locations)
    with col2:
        bhk_options = sorted(df['bhk'].unique())
        selected_bhk = st.selectbox("BHK", ["All"] + [int(b) for b in bhk_options])
    with col3:
        budget = st.slider("Max Budget (Lakhs)", 
                            int(df['price'].min()), int(df['price'].max()), 
                            int(df['price'].median()))

    filtered = df.copy()
    if selected_location != "All":
        filtered = filtered[filtered['location'] == selected_location]
    if selected_bhk != "All":
        filtered = filtered[filtered['bhk'] == selected_bhk]
    filtered = filtered[filtered['price'] <= budget]

    filtered = filtered.copy()
    filtered['price_per_sqft'] = (filtered['price'] * 100000 / filtered['total_sqft']).round(0)

    st.write(f"**{len(filtered)} properties found**")
    st.dataframe(filtered[['location', 'bhk', 'total_sqft', 'bath', 'balcony', 'price', 'price_per_sqft']]
                 .sort_values('price').reset_index(drop=True))

# =========================================================
# PAGE 2: Price Predictor
# =========================================================
elif page == "Price Predictor":
    st.title("🔮 Property Price Predictor")
    st.write("Enter property details to get an estimated price.")
    

    col1, col2 = st.columns(2)
    with col1:
        location = st.selectbox("Locality", sorted(df['location'].unique()))
        sqft = st.number_input("Total Sqft", min_value=200, max_value=10000, value=1200)
        bhk = st.number_input("BHK", min_value=1, max_value=10, value=2)
    with col2:
        bath = st.number_input("Bathrooms", min_value=1, max_value=10, value=2)
        balcony = st.number_input("Balconies", min_value=0, max_value=5, value=1)

    if st.button("Predict Price"):
        input_dict = {col: 0 for col in model_columns}
        input_dict['total_sqft'] = sqft
        input_dict['bhk'] = bhk
        input_dict['bath'] = bath
        input_dict['balcony'] = balcony

        location_col = f"location_grouped_{location}"
        if location_col in input_dict:
            input_dict[location_col] = 1
        else:
            other_col = "location_grouped_other"
            if other_col in input_dict:
                input_dict[other_col] = 1

        input_df = pd.DataFrame([input_dict])[model_columns]
        prediction = model.predict(input_df)[0]
        locality_avg = df[df['location'] == location]['price'].mean()
        diff_pct = ((prediction - locality_avg) / locality_avg) * 100 if locality_avg > 0 else 0

        st.success(f"### Estimated Price: ₹{prediction:.2f} Lakhs (₹{prediction*100000:,.0f})")
        price_per_sqft = (prediction * 100000) / sqft
        st.caption(f"📐 That's approximately ₹{price_per_sqft:,.0f} per sqft")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"Avg price in {location}", f"₹{locality_avg:.2f} Lakhs")
        with col2:
            st.metric("Difference from locality avg", f"{diff_pct:+.1f}%")

        st.caption(f"💡 Estimated monthly rent (based on 3.5% annual yield): ₹{(prediction*100000*0.035/12):,.0f}/month")

        with st.expander("How is this price calculated?"):
            st.write("""
            This estimate comes from a Random Forest model trained on 12,700+ real Bengaluru property listings.
            It considers your property's square footage, number of bedrooms/bathrooms/balconies, and locality —
            square footage is the single biggest driver of price, followed by 
            bathroom count and locality premium.
            """)
# =========================================================
# PAGE 3: Market Insights
# =========================================================
elif page == "Market Insights":
    st.title("📊 Bengaluru Real Estate Market Insights")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average Price by Locality (Top 15)")
        top_locations = df.groupby('location')['price'].agg(['mean', 'count'])
        top_locations = top_locations[top_locations['count'] >= 10].sort_values('mean', ascending=False).head(15)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(x=top_locations['mean'], y=top_locations.index, ax=ax)
        ax.set_xlabel("Average Price (Lakhs)")
        st.pyplot(fig)

    with col2:
        st.subheader("BHK Distribution")
        bhk_counts = df['bhk'].value_counts().sort_index()
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        sns.barplot(x=bhk_counts.index, y=bhk_counts.values, ax=ax2)
        ax2.set_xlabel("BHK")
        ax2.set_ylabel("Count")
        st.pyplot(fig2)

    st.subheader("Price vs Square Footage")
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    sns.scatterplot(data=df[df['total_sqft'] < 6000], x='total_sqft', y='price', alpha=0.4, ax=ax3)
    st.pyplot(fig3)