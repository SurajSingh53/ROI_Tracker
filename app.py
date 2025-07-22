import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import numpy as np

st.set_page_config(layout="wide")

st.title("📊 Influencer ROI & Campaign Performance Dashboard")

uploaded_tracking = st.file_uploader("Upload Tracking Data", type="csv")
uploaded_posts = st.file_uploader("Upload Posts Data", type="csv")
uploaded_payouts = st.file_uploader("Upload Payouts Data", type="csv")
uploaded_influencers = st.file_uploader("Upload Influencers Data", type="csv")

if uploaded_tracking and uploaded_posts and uploaded_payouts and uploaded_influencers:
    tracking_df = pd.read_csv(uploaded_tracking)
    posts_df = pd.read_csv(uploaded_posts)
    payouts_df = pd.read_csv(uploaded_payouts)
    influencers_df = pd.read_csv(uploaded_influencers)

    df = tracking_df.merge(posts_df, on="influencer_id", how="left")
    df = df.merge(payouts_df, on=["influencer_id", "campaign"], how="left")
    df = df.merge(influencers_df, on="influencer_id", how="left")

    df["ROI"] = df["revenue"] / df["total_payout"]
    df["ROAS"] = df["revenue"] / (df["clicks"] * df["cost_per_click"])
    df["incremental_ROAS"] = df["ROAS"] - df["ROI"]
    df["date"] = pd.to_datetime(df["date"])

    brands = df["brand"].dropna().unique()
    products = df["product"].dropna().unique()
    platforms = df["platform_x"].dropna().unique()
    genders = df["gender"].dropna().unique()

    selected_brand = st.selectbox("Filter by Brand", ["All"] + list(brands))
    selected_product = st.selectbox("Filter by Product", ["All"] + list(products))
    selected_platform = st.selectbox("Filter by Platform", ["All"] + list(platforms))
    selected_gender = st.selectbox("Filter by Influencer Gender", ["All"] + list(genders))

    filtered_df = df.copy()
    if selected_brand != "All":
        filtered_df = filtered_df[filtered_df["brand"] == selected_brand]
    if selected_product != "All":
        filtered_df = filtered_df[filtered_df["product"] == selected_product]
    if selected_platform != "All":
        filtered_df = filtered_df[filtered_df["platform_x"] == selected_platform]
    if selected_gender != "All":
        filtered_df = filtered_df[filtered_df["gender"] == selected_gender]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧮 Total Campaigns", df["campaign"].nunique())
    col2.metric("🎯 Total Orders", int(df["orders"].sum()))
    col3.metric("💸 Total Revenue", f"₹{int(df["revenue"].sum()):,}")
    col4.metric("🤑 Avg ROI", round(df["ROI"].mean(), 2))

    st.markdown("---")

    st.subheader("📈 Revenue Over Time")
    fig1 = alt.Chart(filtered_df).mark_line(point=True).encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("revenue:Q", title="Revenue (₹)"),
        color="campaign:N",
        tooltip=["date", "campaign", "revenue"]
    ).properties(width=900, height=300).interactive()
    st.altair_chart(fig1, use_container_width=True)

    st.subheader("🔥 Top Influencers by ROI")
    top_influencers = filtered_df.groupby("name")["ROI"].mean().nlargest(10).reset_index()
    fig2 = alt.Chart(top_influencers).mark_bar().encode(
        x=alt.X("ROI:Q", title="ROI"),
        y=alt.Y("name:N", sort="-x", title="Influencer Name"),
        color="ROI:Q",
        tooltip=["name", "ROI"]
    ).properties(width=800, height=300)
    st.altair_chart(fig2, use_container_width=True)

    st.subheader("📉 Influencer Engagement vs Payout")
    fig3 = alt.Chart(filtered_df).mark_circle(size=60).encode(
        x=alt.X("engagement_rate:Q", title="Engagement Rate (%)"),
        y=alt.Y("total_payout:Q", title="Total Payout (₹)"),
        color="platform_x:N",
        tooltip=["name", "engagement_rate", "total_payout"]
    ).properties(width=800, height=300).interactive()
    st.altair_chart(fig3, use_container_width=True)

    st.subheader("🧠 Incremental ROAS by Influencer")
    roas_by_influencer = filtered_df.groupby("name")["incremental_ROAS"].mean().reset_index()
    roas_by_influencer = roas_by_influencer.sort_values("incremental_ROAS", ascending=False).head(20)
    fig4 = alt.Chart(roas_by_influencer).mark_bar().encode(
        x=alt.X("name:N", sort="-y", title="Influencer Name", axis=alt.Axis(labelAngle=-90, labelFontSize=10)),
        y=alt.Y("incremental_ROAS:Q", title="Incremental ROAS"),
        color="incremental_ROAS:Q",
        tooltip=["name", "incremental_ROAS"]
    ).properties(width=1000, height=400)
    st.altair_chart(fig4, use_container_width=True)
st.markdown("---")
st.markdown("Made with 💚 by SurajSingh")
