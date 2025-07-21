import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.graph_objects as go
from matplotlib.animation import FuncAnimation

st.set_page_config(layout="wide")

st.title("📊 Influencer Campaign ROI Dashboard")

# Load data
posts = pd.read_csv("posts.csv")
payouts = pd.read_csv("payouts.csv")
influencers = pd.read_csv("influencers.csv")
tracking = pd.read_csv("tracking_data.csv")

# Merge data
merged = tracking.merge(posts, on=["Influencer Name", "Campaign Name"], how="left")
merged = merged.merge(payouts, on=["Influencer Name", "Campaign Name"], how="left")
merged = merged.merge(influencers, on="Influencer Name", how="left")

# Fill NaNs
merged.fillna(0, inplace=True)

# Calculations
merged["ROI"] = (merged["Sales Value"] - merged["Payout Amount"]) / merged["Payout Amount"]
merged["ROAS"] = merged["Sales Value"] / merged["Payout Amount"]

# Sidebar filters
brands = merged["Brand"].unique()
products = merged["Product"].unique()
types = merged["Influencer Type"].unique()
platforms = merged["Platform"].unique()

brand_filter = st.sidebar.multiselect("Filter by Brand", brands, default=brands)
product_filter = st.sidebar.multiselect("Filter by Product", products, default=products)
type_filter = st.sidebar.multiselect("Filter by Influencer Type", types, default=types)
platform_filter = st.sidebar.multiselect("Filter by Platform", platforms, default=platforms)

filtered = merged[
    (merged["Brand"].isin(brand_filter)) &
    (merged["Product"].isin(product_filter)) &
    (merged["Influencer Type"].isin(type_filter)) &
    (merged["Platform"].isin(platform_filter))
]

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Campaigns", filtered["Campaign Name"].nunique())
col2.metric("Total Influencers", filtered["Influencer Name"].nunique())
col3.metric("Total Sales", f"₹{int(filtered['Sales Value'].sum()):,}")
col4.metric("Avg. ROAS", f"{filtered['ROAS'].mean():.2f}x")

# Layout
st.markdown("---")
col5, col6 = st.columns(2)

# ROI Distribution
with col5:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(filtered["ROI"], kde=True, ax=ax, color="skyblue")
    ax.set_title("ROI Distribution")
    ax.set_xlabel("ROI (Return on Investment)")
    ax.xaxis.set_major_formatter(ticker.PercentFormatter(1.0))
    st.pyplot(fig)

# ROAS vs Sales
with col6:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(data=filtered, x="ROAS", y="Sales Value", hue="Platform", ax=ax)
    ax.set_title("ROAS vs Sales Value")
    ax.set_ylabel("Sales (₹)")
    ax.set_xlabel("ROAS (x)")
    st.pyplot(fig)

st.markdown("---")
col7, col8 = st.columns(2)

# Top Influencers by Sales
top_influencers = filtered.groupby("Influencer Name")["Sales Value"].sum().sort_values(ascending=False).head(10)
with col7:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=top_influencers.values, y=top_influencers.index, palette="viridis", ax=ax)
    ax.set_title("Top 10 Influencers by Sales")
    ax.set_xlabel("Sales (₹)")
    st.pyplot(fig)

# Best performing personas
best_personas = filtered.groupby("Influencer Type")["ROAS"].mean().sort_values(ascending=False)
with col8:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=best_personas.values, y=best_personas.index, palette="magma", ax=ax)
    ax.set_title("Best Performing Influencer Types (Avg. ROAS)")
    ax.set_xlabel("ROAS (x)")
    st.pyplot(fig)

st.markdown("---")

# Animated post tracking over time
filtered["Date"] = pd.to_datetime(filtered["Date"], errors='coerce')
filtered = filtered.dropna(subset=["Date"])

time_group = filtered.groupby(filtered["Date"].dt.to_period("M")).agg({"Sales Value": "sum"})
time_group.index = time_group.index.to_timestamp()

fig, ax = plt.subplots(figsize=(10, 4))
bar = ax.bar([], [])

frames = []
x = time_group.index

for i in range(len(x)):
    ax.clear()
    ax.plot(x[:i+1], time_group["Sales Value"].values[:i+1], color="dodgerblue")
    ax.set_title("Sales Value Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Sales (₹)")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# Last: Influencer-level ROAS
roas_chart = filtered.groupby("Influencer Name")["ROAS"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=roas_chart.index, y=roas_chart.values, ax=ax, palette="cubehelix")
ax.set_title("Influencer-wise ROAS")
ax.set_ylabel("ROAS (x)")
ax.set_xlabel("Influencer")
ax.set_xticklabels(roas_chart.index, rotation=90, fontsize=7)
st.pyplot(fig)

st.markdown("---")
st.markdown("Made with 💚 by SurajSingh")
