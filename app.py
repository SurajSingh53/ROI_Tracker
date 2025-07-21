import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="HealthKart Influencer ROI Dashboard", layout="wide")
st.title("🏋️ HealthKart Influencer Campaign ROI Dashboard")

st.sidebar.header("📤 Upload Your Data")
influencer_file = st.sidebar.file_uploader("Upload Influencers CSV", type="csv")
posts_file = st.sidebar.file_uploader("Upload Posts CSV", type="csv")
tracking_file = st.sidebar.file_uploader("Upload Tracking Data CSV", type="csv")
payouts_file = st.sidebar.file_uploader("Upload Payouts CSV", type="csv")

@st.cache_data
def load_uploaded_data():
    if influencer_file and posts_file and tracking_file and payouts_file:
        influencers = pd.read_csv(influencer_file)
        posts = pd.read_csv(posts_file)
        tracking = pd.read_csv(tracking_file)
        payouts = pd.read_csv(payouts_file)
        return influencers, posts, tracking, payouts
    return None, None, None, None

influencers, posts, tracking, payouts = load_uploaded_data()

if influencers is None:
    st.warning("⬅️ Please upload all required CSV files from the sidebar to continue.")
    st.stop()

st.sidebar.header("Filter Options")
selected_platform = st.sidebar.multiselect("Platform", influencers["platform"].unique(), default=influencers["platform"].unique())
selected_gender = st.sidebar.multiselect("Gender", influencers["gender"].unique(), default=influencers["gender"].unique())
selected_category = st.sidebar.multiselect("Category", influencers["category"].unique(), default=influencers["category"].unique())

filtered_influencers = influencers[
    (influencers["platform"].isin(selected_platform)) &
    (influencers["gender"].isin(selected_gender)) &
    (influencers["category"].isin(selected_category))
]
filtered_posts = posts[posts["platform"].isin(selected_platform)]
filtered_tracking = tracking[tracking["source"].isin(selected_platform)]

perf_df = filtered_tracking.merge(payouts, on="influencer_id", how="left")
perf_df = perf_df.merge(influencers, on="influencer_id", how="left")
perf_df = perf_df.merge(posts, on="influencer_id", how="left")

perf_df["ROAS"] = perf_df["revenue"] / perf_df["total_payout"]
perf_df["ROI"] = (perf_df["revenue"] - perf_df["total_payout"]) / perf_df["total_payout"]
perf_df["engagement"] = (perf_df["likes"] + perf_df["comments"]) / perf_df["reach"]
perf_df["conversion_rate"] = perf_df["orders"] / perf_df["reach"]
perf_df["revenue_per_post"] = perf_df["revenue"] / perf_df["rate"]
perf_df["cost_per_order"] = perf_df["total_payout"] / perf_df["orders"]
perf_df["cost_per_reach"] = perf_df["total_payout"] / perf_df["reach"]
perf_df["likes_per_post"] = perf_df["likes"]
perf_df["comments_per_post"] = perf_df["comments"]

total_revenue = perf_df["revenue"].sum()
total_spend = perf_df["total_payout"].sum()
overall_roas = round(total_revenue / total_spend, 2)
total_orders = perf_df["orders"].sum()
total_reach = perf_df["reach"].sum()

st.markdown("### 📈 Overall Campaign Metrics")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Revenue (₹)", f"{total_revenue:,.0f}")
kpi2.metric("Total Spend (₹)", f"{total_spend:,.0f}")
kpi3.metric("Overall ROAS", f"{overall_roas}x")
kpi4, kpi5, kpi6 = st.columns(3)
kpi4.metric("Total Orders", f"{total_orders:,.0f}")
kpi5.metric("Total Reach", f"{total_reach:,.0f}")
kpi6.metric("Avg Engagement Rate", f"{perf_df['engagement'].mean():.2%}")

st.markdown("### 👥 Influencer Performance")
st.dataframe(perf_df[["name", "platform", "category", "gender", "follower_count", "revenue", "orders", "reach", "likes", "comments", "engagement", "conversion_rate", "total_payout", "ROAS", "ROI", "cost_per_order", "cost_per_reach"]].round(2))

st.markdown("### 📊 ROAS by Influencer")
fig = px.bar(perf_df, x="name", y="ROAS", color="platform", text="ROAS", height=400)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 💬 Engagement Rate by Platform")
fig2 = px.box(perf_df, x="platform", y="engagement", color="platform")
st.plotly_chart(fig2, use_container_width=True)

if "date" in perf_df.columns:
    perf_df["date"] = pd.to_datetime(perf_df["date"])
    trend = perf_df.groupby(perf_df["date"].dt.to_period("M")).agg({"revenue": "sum", "orders": "sum"}).reset_index()
    trend["date"] = trend["date"].astype(str)
    st.markdown("### 📅 Monthly Revenue and Orders Trend")
    fig3 = px.line(trend, x="date", y=["revenue", "orders"], markers=True)
    st.plotly_chart(fig3, use_container_width=True)

st.download_button("Export ROI Data to CSV", data=perf_df.to_csv(index=False), file_name="influencer_roi.csv", mime="text/csv")


with st.expander("💡 Auto Insights Summary"):
    best_influencer = perf_df.sort_values(by="ROAS", ascending=False).iloc[0]
    worst_influencer = perf_df.sort_values(by="ROAS").iloc[0]
    st.markdown(f"- **Top ROAS:** {best_influencer['name']} ({best_influencer['ROAS']:.2f}x)")
    st.markdown(f"- **Lowest ROAS:** {worst_influencer['name']} ({worst_influencer['ROAS']:.2f}x)")
    st.markdown(f"- **Top Engagement:** {perf_df.sort_values(by='engagement', ascending=False).iloc[0]['name']} ({perf_df['engagement'].max():.2%})")
    st.markdown(f"- **Top Conversion:** {perf_df.sort_values(by='conversion_rate', ascending=False).iloc[0]['name']} ({perf_df['conversion_rate'].max():.2%})")
    st.markdown("- Influencers paid per order are generally more cost-effective based on ROI comparison.")
