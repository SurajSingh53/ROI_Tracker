# influencer_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(page_title="Influencer Campaign Dashboard", layout="wide", page_icon="📊")
st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #e0f7fa 0%, #f1f8e9 100%);
            color: #1a237e;
        }
        .stMetricLabel, .stMetricValue {
            color: #004d40 !important;
        }
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌟 HealthKart Influencer Campaign Dashboard")
st.markdown("##### Stunning 3D Visuals • Interactive Filters • Real-Time Insights")

# Upload CSV files
st.sidebar.header("📤 Upload Campaign Data")
influencers_file = st.sidebar.file_uploader("Upload influencers.csv", type="csv")
posts_file = st.sidebar.file_uploader("Upload posts.csv", type="csv")
tracking_file = st.sidebar.file_uploader("Upload tracking_data.csv", type="csv")
payouts_file = st.sidebar.file_uploader("Upload payouts.csv", type="csv")

if all([influencers_file, posts_file, tracking_file, payouts_file]):
    # Load data
    df_influencers = pd.read_csv(influencers_file)
    df_posts = pd.read_csv(posts_file)
    df_tracking = pd.read_csv(tracking_file)
    df_payouts = pd.read_csv(payouts_file)

    df_posts["date"] = pd.to_datetime(df_posts["date"])
    df_tracking["date"] = pd.to_datetime(df_tracking["date"])

    # Merge tracking with influencer details
    df_merged = df_tracking.merge(df_influencers, on="influencer_id")
    df_merged = df_merged.merge(df_payouts[["influencer_id", "campaign", "total_payout"]], on=["influencer_id", "campaign"], how="left")

    # ROAS Calculation
    df_merged["ROAS"] = df_merged["revenue"] / (df_merged["clicks"] * df_merged["cost_per_click"] + 1e-5)

    # Incremental ROAS (relative to platform average)
    avg_roas_by_platform = df_merged.groupby("platform")["ROAS"].mean().reset_index().rename(columns={"ROAS": "avg_platform_roas"})
    df_merged = df_merged.merge(avg_roas_by_platform, on="platform")
    df_merged["Incremental ROAS"] = df_merged["ROAS"] - df_merged["avg_platform_roas"]

    # Date Range Slider
    min_date = pd.to_datetime(df_tracking["date"].min())
    max_date = pd.to_datetime(df_tracking["date"].max())

    if pd.isnull(min_date) or pd.isnull(max_date):
        st.error("Date values in tracking_data.csv are missing or invalid.")
    else:
        selected_range = st.slider(
            "Select Campaign Date Range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )
        df_merged = df_merged[(df_merged["date"] >= selected_range[0]) & (df_merged["date"] <= selected_range[1])]

        st.subheader("📊 Campaign Overview")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Total Revenue", f"₹{df_merged['revenue'].sum():,.0f}")
        col2.metric("📦 Total Orders", f"{df_merged['orders'].sum():,.0f}")
        col3.metric("📈 Avg ROAS", f"{df_merged['ROAS'].mean():.2f}")
        col4.metric("✨ Incremental ROAS", f"{df_merged['Incremental ROAS'].mean():.2f}")

        st.subheader("🎯 Influencer Insights")
        platform = st.selectbox("Filter by Platform", df_merged["platform"].unique())
        df_filtered = df_merged[df_merged["platform"] == platform]
        influencer_summary = df_filtered.groupby("name").agg({
            "follower_count": "first",
            "engagement_rate": "first",
            "revenue": "sum",
            "orders": "sum",
            "total_payout": "mean",
            "ROAS": "mean"
        }).sort_values("ROAS", ascending=False).reset_index()

        fig_bar = px.bar_3d(
            influencer_summary,
            x="name", y="revenue", z="follower_count",
            color="ROAS",
            title="3D Revenue vs Followers by Influencer",
            height=600
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.dataframe(influencer_summary.style.format({
            "revenue": "₹{:.0f}",
            "total_payout": "₹{:.0f}",
            "ROAS": "{:.2f}"
        }), use_container_width=True)

        st.subheader("📸 Top Performing Posts")
        top_posts = df_posts[df_posts["date"].between(*selected_range)].sort_values(by="likes", ascending=False).head(10)
        st.dataframe(top_posts[["platform", "date", "url", "caption", "likes", "comments", "shares"]])

        st.subheader("💸 Payout Summary")
        payouts_summary = df_payouts.groupby("status")["total_payout"].sum().reset_index()
        fig = go.Figure(data=[go.Pie(labels=payouts_summary["status"], values=payouts_summary["total_payout"], hole=.4)])
        fig.update_layout(title_text="Payout Status Distribution", height=500)
        st.plotly_chart(fig, use_container_width=True)

        if st.button("📤 Export Insights to CSV"):
            influencer_summary.to_csv("influencer_summary.csv", index=False)
            st.success("Exported influencer_summary.csv")
else:
    st.info("Please upload all 4 required CSV files to proceed.")
