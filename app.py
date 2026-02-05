import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Silver Price Calculator & Silver Sales Dashboard",
    page_icon="🥈",
    layout="wide"
)

st.title("🥈 Silver Price Calculator & Silver Sales Analysis")

st.markdown("""
This application analyzes **historical silver prices in India** and  
**state-wise silver purchases** using interactive charts, maps, and 3D visualization.
""")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
price_df = pd.read_csv("historical_silver_price.csv")
sales_df = pd.read_csv("state_wise_silver_purchased_kg.csv")

st.success("Datasets Loaded Successfully!")

# ---------------------------------------------------------
# SIDEBAR (Currency Conversion)
# ---------------------------------------------------------
st.sidebar.header("Currency Converter")

currency = st.sidebar.selectbox("Choose Currency", ["INR", "USD", "EUR"])

rates = {
    "INR": 1,
    "USD": 0.012,
    "EUR": 0.011
}

# =========================================================
# 1) SILVER PRICE CALCULATOR
# =========================================================
st.header("🔢 Silver Price Calculator")

c1, c2, c3 = st.columns(3)

with c1:
    weight = st.number_input("Enter Weight", min_value=0.0, value=10.0)

with c2:
    unit = st.radio("Unit", ["Grams", "Kilograms"])

with c3:
    price_per_gram = st.number_input("Price per Gram (INR)", value=75.0)

if unit == "Kilograms":
    weight = weight * 1000

total_cost_inr = weight * price_per_gram
converted_cost = total_cost_inr * rates[currency]

st.success(f"💰 Total Cost: {converted_cost:,.2f} {currency}")

# =========================================================
# HISTORICAL SILVER PRICE ANALYSIS
# =========================================================
st.header("📈 Historical Silver Price Analysis")

price_filter = st.selectbox(
    "Filter Price (INR per kg)",
    ["All", "≤ 20,000", "20,000 - 30,000", "≥ 30,000"]
)

filtered_df = price_df.copy()

if price_filter == "≤ 20,000":
    filtered_df = filtered_df[
        filtered_df["Silver_Price_INR_per_kg"] <= 20000
    ]

elif price_filter == "20,000 - 30,000":
    filtered_df = filtered_df[
        (filtered_df["Silver_Price_INR_per_kg"] > 20000) &
        (filtered_df["Silver_Price_INR_per_kg"] < 30000)
    ]

elif price_filter == "≥ 30,000":
    filtered_df = filtered_df[
        filtered_df["Silver_Price_INR_per_kg"] >= 30000
    ]

# ----------- 2D LINE CHART -------------
fig_price = px.line(
    filtered_df,
    x=filtered_df.index,
    y="Silver_Price_INR_per_kg",
    markers=True,
    title="Historical Silver Price Trend (INR/kg)"
)

st.plotly_chart(fig_price, use_container_width=True)

# ----------- 3D BAR CHART -------------
st.subheader("🧊 3D Silver Price Visualization")

fig3d = plt.figure(figsize=(8, 5))
ax = fig3d.add_subplot(111, projection='3d')

x = np.arange(len(filtered_df))
y = filtered_df["Silver_Price_INR_per_kg"]
z = np.zeros(len(filtered_df))

ax.bar(x, y, z)
ax.set_xlabel("Time Index")
ax.set_ylabel("Price (INR/kg)")
ax.set_zlabel("Depth")

st.pyplot(fig3d)

# =========================================================
# 2) SILVER SALES DASHBOARD
# =========================================================
st.header("📊 Silver Sales Dashboard")

# ---------------------------------------------------------
# INDIA MAP
# ---------------------------------------------------------
india_geojson = "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"
india_map = gpd.read_file(india_geojson)

india_map["NAME_1"] = india_map["NAME_1"].str.lower()
sales_df["State"] = sales_df["State"].str.lower()

merged_df = india_map.merge(
    sales_df,
    left_on="NAME_1",
    right_on="State"
)

st.subheader("🗺 State-wise Silver Purchases (kg)")

fig_map, ax = plt.subplots(figsize=(7, 8))
merged_df.plot(
    column="Silver_Purchased_kg",
    cmap="Greys",
    legend=True,
    ax=ax
)
ax.axis("off")
st.pyplot(fig_map)

# ---------------------------------------------------------
# TOP 5 STATES BAR CHART
# ---------------------------------------------------------
st.subheader("🏆 Top 5 States by Silver Purchase")

top5 = sales_df.sort_values(
    by="Silver_Purchased_kg",
    ascending=False
).head(5)

fig_top5 = px.bar(
    top5,
    x="State",
    y="Silver_Purchased_kg",
    color="State",
    title="Top 5 Silver Purchasing States"
)

st.plotly_chart(fig_top5, use_container_width=True)

# ---------------------------------------------------------
# KARNATAKA MONTHLY TREND
# ---------------------------------------------------------
st.subheader("📅 Karnataka Monthly Silver Purchases")

monthly_df = sales_df.melt(
    id_vars=["State"],
    var_name="Month",
    value_name="Monthly_Silver_kg"
)

karnataka_df = monthly_df[
    monthly_df["State"] == "karnataka"
]

fig_kar = px.line(
    karnataka_df,
    x="Month",
    y="Monthly_Silver_kg",
    markers=True,
    title="Karnataka Monthly Silver Purchase Trend"
)

st.plotly_chart(fig_kar, use_container_width=True)

# ---------------------------------------------------------
# RAW DATA
# ---------------------------------------------------------
with st.expander("📂 View Raw Datasets"):
    st.dataframe(price_df)
    st.dataframe(sales_df)

st.markdown("---")
st.markdown("Built using **Streamlit, GeoPandas, Plotly, Matplotlib & NumPy**")
