import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Silver Price Calculator & Silver Sales Analysis",
    page_icon=":tada:",
    layout="wide"
)

st.title("Silver Price Calculator & Silver Sales Analysis")

st.markdown("""
This application analyzes **historical silver price trends in India**
and **state-wise silver purchases** using **Streamlit UI widgets**
and **2D & 3D visualizations**.
""")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
def load_price_data():
    return pd.read_csv("historical_silver_price.csv")

def load_sales_data():
    return pd.read_csv("state_wise_silver_purchased_kg.csv")

price_df = load_price_data()
sales_df = load_sales_data()

st.success("Data loaded successfully. Ready for analysis.")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("User Controls")

currency = st.sidebar.selectbox(
    "Select Currency",
    ["INR", "USD", "EUR"]
)

exchange_rate = {
    "INR": 1,
    "USD": 0.012,
    "EUR": 0.011
}


# 1. SILVER PRICE CALCULATOR
st.header("Silver Price Calculator")

c1, c2, c3 = st.columns(3)

with c1:
    weight = st.number_input("Enter Weight", min_value=0.0, value=10.0)

with c2:
    unit = st.radio("Unit", ["Grams", "Kilograms"])

with c3:
    price_per_gram = st.number_input(
        "Current Price per Gram (INR)",
        min_value=0.0,
        value=75.0
    )

if unit == "Kilograms":
    weight_in_grams = weight * 1000
else:
    weight_in_grams = weight

total_cost_inr = weight_in_grams * price_per_gram
converted_cost = total_cost_inr * exchange_rate[currency]

st.success(f"💰 Total Cost: **{converted_cost:,.2f} {currency}**")

# HISTORICAL SILVER PRICE ANALYSIS
st.header("Historical Silver Price Analysis")

year_range = st.slider(
    "Select Year Range",
    min_value=int(price_df["Year"].min()),
    max_value=int(price_df["Year"].max()),
    value=(int(price_df["Year"].min()), int(price_df["Year"].max()))
)

price_filter = st.selectbox(
    "Filter Price Range (INR per kg)",
    ["≤ 20,000", "20,000 – 30,000", "≥ 30,000", "All"]
)

filtered_df = price_df[
    (price_df["Year"] >= year_range[0]) &
    (price_df["Year"] <= year_range[1])
].copy()

if price_filter == "≤ 20,000":
    filtered_df = filtered_df[filtered_df["Silver_Price_INR_per_kg"] <= 20000]
elif price_filter == "20,000 – 30,000":
    filtered_df = filtered_df[
        (filtered_df["Silver_Price_INR_per_kg"] > 20000) &
        (filtered_df["Silver_Price_INR_per_kg"] < 30000)
    ]
elif price_filter == "≥ 30,000":
    filtered_df = filtered_df[filtered_df["Silver_Price_INR_per_kg"] >= 30000]

filtered_df["Time_Index"] = range(len(filtered_df))

fig_line = px.line(
    filtered_df,
    x="Time_Index",
    y="Silver_Price_INR_per_kg",
    markers=True,
    title="Historical Silver Price Trend (INR per kg)"
)

st.plotly_chart(fig_line, use_container_width=True)

# 3D SILVER PRICE VISUALIZATION
st.subheader("3D Silver Price Visualization")

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection="3d")

x = filtered_df["Time_Index"]
y = filtered_df["Silver_Price_INR_per_kg"]
z = np.zeros(len(filtered_df))

ax.bar(x, y, z)
ax.set_xlabel("Time Index")
ax.set_ylabel("Price (INR per kg)")
ax.set_zlabel("Depth")

st.pyplot(fig)

# 2. SILVER SALES DASHBOARD
st.header("Silver Sales Dashboard")

# TOP 5 STATES
st.subheader("Top 5 States by Silver Purchases")

top5 = sales_df.sort_values(
    by="Silver_Purchased_kg",
    ascending=False
).head(5)

fig_bar = px.bar(
    top5,
    x="State",
    y="Silver_Purchased_kg",
    color="State",
    title="Top 5 Silver Purchasing States"
)

st.plotly_chart(fig_bar, use_container_width=True)

# STATE-WISE COMPARISON
st.subheader("State-wise Silver Purchase Comparison")

fig_state_line = px.line(
    sales_df.sort_values("Silver_Purchased_kg"),
    x="State",
    y="Silver_Purchased_kg",
    markers=True,
    title="State-wise Silver Purchases (kg)"
)

st.plotly_chart(fig_state_line, use_container_width=True)

# RAW DATA
with st.expander("View Raw Datasets"):
    st.dataframe(price_df)
    st.dataframe(sales_df)

st.markdown("---")