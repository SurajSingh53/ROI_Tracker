import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Influencer Campaign ROI Tracker", layout="wide")

@st.cache_data
def load_data():
    tracking_data = pd.read_csv("tracking_data.csv", parse_dates=['date'])
    posts = pd.read_csv("posts.csv")
    payouts = pd.read_csv("payouts.csv")
    influencers = pd.read_csv("influencers.csv")
    return tracking_data, posts, payouts, influencers

tracking_data, posts, payouts, influencers = load_data()

st.title("💫 Influencer Campaign ROI Dashboard")

# Date slider range check
min_date = tracking_data['date'].min()
max_date = tracking_data['date'].max()

if pd.isnull(min_date) or pd.isnull(max_date):
    st.error("Date values in tracking_data.csv are missing or invalid.")
else:
    selected_range = st.slider(
        "Select Campaign Date Range",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime())
    )

    start_date, end_date = selected_range
    tracking_data = tracking_data[(tracking_data['date'] >= start_date) & (tracking_data['date'] <= end_date)]

# Merge and compute metrics
merged = tracking_data.merge(payouts, on='campaign_id').merge(influencers, on='influencer_id')
merged['roi'] = merged['revenue'] / merged['payout']
merged['roas'] = merged['revenue'] / merged['spend']

st.subheader("📊 Key Metrics")
total_spend = merged['spend'].sum()
total_revenue = merged['revenue'].sum()
total_payout = merged['payout'].sum()
total_roi = total_revenue / total_payout if total_payout else 0
total_roas = total_revenue / total_spend if total_spend else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Spend", f"₹{total_spend:,.0f}")
col2.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col3.metric("ROI", f"{total_roi:.2f}x")
col4.metric("ROAS", f"{total_roas:.2f}x")

st.divider()

# ROI by Influencer
st.subheader("🧑‍🤝‍🧑 Influencer ROI")
roi_df = merged.groupby(['influencer_id', 'name']).agg({
    'revenue': 'sum',
    'payout': 'sum',
    'spend': 'sum'
}).reset_index()
roi_df['roi'] = roi_df['revenue'] / roi_df['payout']
roi_df['roas'] = roi_df['revenue'] / roi_df['spend']

fig_roi = px.bar(
    roi_df,
    x='name',
    y='roi',
    title='Influencer ROI',
    color='roi',
    color_continuous_scale='Tealgrn',
    labels={'roi': 'ROI'}
)
st.plotly_chart(fig_roi, use_container_width=True)

st.divider()

# Campaign Timeline
st.subheader("📅 Campaign Timeline")
campaign_summary = tracking_data.groupby('date').agg({
    'spend': 'sum',
    'revenue': 'sum'
}).reset_index()

fig_time = px.line(
    campaign_summary,
    x='date',
    y=['spend', 'revenue'],
    title='Daily Spend vs Revenue',
    markers=True
)
st.plotly_chart(fig_time, use_container_width=True)

st.divider()

# Optional: Add 3D visual hook later here
