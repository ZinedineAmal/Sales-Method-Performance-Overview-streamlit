import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(layout="wide", page_title="Sales Method Analysis")

# ==============================
# HEADER DENGAN GAMBAR
# ==============================
try:
    banner = Image.open("images/sales_banner.png")
    st.image(banner, use_column_width=True)
except:
    st.markdown("<h1 style='text-align:center; color:#FFD43B; background-color:#1E3A5F; padding:10px;'>SALES METHOD ANALYSIS</h1>", unsafe_allow_html=True)

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("data_clean.csv")
    df["Invoice Date"] = pd.to_datetime(df["Invoice Date"])
    df["Month"] = df["Invoice Date"].dt.to_period("M").dt.to_timestamp()
    return df

df = load_data()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.title("Filters")

# State filter
states = ["All"] + sorted(df["State"].unique().tolist())
selected_state = st.sidebar.selectbox("STATE", states)

# Retailer filter
retailers = sorted(df["Retailer"].unique().tolist())
selected_retailers = st.sidebar.multiselect("Retailer", retailers, default=retailers)

# Sales Method filter
methods = sorted(df["Sales Method"].unique().tolist())
selected_methods = st.sidebar.multiselect("Sales Method", methods, default=methods)

# Date range filter
min_date, max_date = df["Invoice Date"].min(), df["Invoice Date"].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

# Apply filters
filtered = df.copy()
if selected_state != "All":
    filtered = filtered[filtered["State"] == selected_state]
filtered = filtered[filtered["Retailer"].isin(selected_retailers)]
filtered = filtered[filtered["Sales Method"].isin(selected_methods)]
filtered = filtered[
    (filtered["Invoice Date"] >= pd.to_datetime(date_range[0]))
    & (filtered["Invoice Date"] <= pd.to_datetime(date_range[1]))
]

# ==============================
# KPI METRICS
# ==============================
kpi1, kpi2, kpi3 = st.columns(3)

total_sales = filtered["Total Sales"].sum()
total_profit = filtered["Operating Profit"].sum()
avg_margin = filtered["Operating Margin"].mean() * 100

with kpi1:
    try:
        st.image("images/instore_icon.png", width=50)
    except:
        st.write("🏬")
    st.metric("Total Sales", f"${total_sales/1e6:.0f}M")

with kpi2:
    try:
        st.image("images/online_icon.png", width=50)
    except:
        st.write("💻")
    st.metric("Total Profit", f"${total_profit/1e6:.0f}M")

with kpi3:
    try:
        st.image("images/outlet_icon.png", width=50)
    except:
        st.write("🏷️")
    st.metric("Average Operating Margin", f"{avg_margin:.2f}%")

# ==============================
# VISUALS
# ==============================
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Total Sales by Sales Method")
    sales_method = filtered.groupby("Sales Method")["Total Sales"].sum().reset_index()
    fig_pie = px.pie(
        sales_method,
        values="Total Sales",
        names="Sales Method",
        color_discrete_sequence=px.colors.sequential.YlOrRd,
        hole=0.3,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Total Sales by Month and Sales Method")
    monthly_sales = filtered.groupby(["Month", "Sales Method"])["Total Sales"].sum().reset_index()
    fig_line = px.line(monthly_sales, x="Month", y="Total Sales", color="Sales Method", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

col3, col4 = st.columns([1, 1.2])

with col3:
    st.subheader("Operating Margin by Sales Method")
    margin = filtered.groupby("Sales Method")["Operating Margin"].mean().reset_index()
    fig_margin = px.bar(
        margin,
        x="Operating Margin",
        y="Sales Method",
        orientation="h",
        text=margin["Operating Margin"].apply(lambda x: f"{x:.2%}"),
        color="Sales Method"
    )
    st.plotly_chart(fig_margin, use_container_width=True)

with col4:
    st.subheader("Product by Total Order and Sales Method")
    product_sales = filtered.groupby(["Product", "Sales Method"])["Total Sales"].sum().reset_index()
    fig_grouped = px.bar(
        product_sales,
        x="Product",
        y="Total Sales",
        color="Sales Method",
        barmode="group"
    )
    st.plotly_chart(fig_grouped, use_container_width=True)

# ==============================
# INSIGHTS
# ==============================
st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("Objective")
    st.write("""
    Evaluate the effectiveness of sales methods (In-store, Online, Outlet) 
    to determine which method increases sales and profitability the most.
    """)

    st.subheader("Business Questions")
    st.markdown("""
    1. Which sales method generates the highest sales?  
    2. Which sales method provides the best operating margin?  
    3. How do monthly sales trends evolve for each method?  
    4. Which sales method is most frequently used for each product type?  
    """)

with right:
    st.subheader("Recommendations")
    try:
        st.image("images/strategy.png", use_container_width=True)
    except:
        st.write("📊")
    st.markdown("""
    - **Focus on Online**: Highest margin (46.3%) → Invest more in online marketing & channels.  
    - **Leverage In-store seasonality**: In-store peaks mid-year → run seasonal promotions.  
    - **Stabilize Outlet**: Fluctuating → optimize costs & localized promotions.  
    - **Product optimization**: Channel-specific pricing & targeted offers.  
    """)

st.markdown("---")
st.caption("Created by Zinedine Amalia — Sales Method Performance Overview")
