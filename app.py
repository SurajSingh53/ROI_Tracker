import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="✨ Influencer ROI Campaign Dashboard", layout="wide", page_icon="🌟")

@st.cache_data

def load_data():
    tracking_data = pd.read_csv("tracking_data.csv", parse_dates=['date'])
    posts = pd.read_csv("posts.csv")
    payouts = pd.read_csv("payouts.csv")
    influencers = pd.read_csv("influencers.csv")
    return tracking_data, posts, payouts, influencers

tracking_data, posts, payouts, influencers = load_data()

st.markdown("""
<style>
.big-metric {
    font-size: 30px !important;
    font-weight: bold;
    color: #00BFFF;
}
</style>
""", unsafe_allow_html=True)

st.title("🌟 Influencer Campaign ROI Dashboard")

if tracking_data.empty:
    st.warning("Tracking data is empty. Please check your CSV files.")
else:
    min_date = tracking_data['date'].min()
    max_date = tracking_data['date'].max()

    if pd.isnull(min_date) or pd.isnull(max_date):
        st.error("Date values in tracking_data.csv are missing or invalid.")
    else:
        selected_range = st.slider(
            "🗓️ Select Campaign Date Range",
            min_value=min_date.to_pydatetime(),
            max_value=max_date.to_pydatetime(),
            value=(min_date.to_pydatetime(), max_date.to_pydatetime())
        )

        start_date, end_date = selected_range
        tracking_data = tracking_data[(tracking_data['date'] >= start_date) & (tracking_data['date'] <= end_date)]

        required_columns = {'campaign_id', 'influencer_id'}
        if not required_columns.issubset(tracking_data.columns):
            st.error("Missing required columns in tracking_data.csv")
        elif not {'campaign_id'}.issubset(payouts.columns):
            st.error("Missing 'campaign_id' in payouts.csv")
        elif not {'influencer_id'}.issubset(influencers.columns):
            st.error("Missing 'influencer_id' in influencers.csv")
        else:
            merged = tracking_data.merge(payouts, on='campaign_id', how='inner')
            merged = merged.merge(influencers, on='influencer_id', how='inner')

            if merged.empty:
                st.warning("No matching records found after merging datasets.")
            else:
                merged['roi'] = merged['revenue'] / merged['payout']
                merged['roas'] = merged['revenue'] / merged['spend']

                st.subheader("📊 Overall Campaign Performance")
                total_spend = merged['spend'].sum()
                total_revenue = merged['revenue'].sum()
                total_payout = merged['payout'].sum()
                total_roi = total_revenue / total_payout if total_payout else 0
                total_roas = total_revenue / total_spend if total_spend else 0

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("💸 Total Spend", f"₹{total_spend:,.0f}")
                col2.metric("📈 Total Revenue", f"₹{total_revenue:,.0f}")
                col3.metric("🚀 ROI", f"{total_roi:.2f}x")
                col4.metric("📊 ROAS", f"{total_roas:.2f}x")

                st.divider()

                st.subheader("🧑‍🤝‍🧑 Influencer Performance")
                roi_df = merged.groupby(['influencer_id', 'name']).agg({
                    'revenue': 'sum',
                    'payout': 'sum',
                    'spend': 'sum'
                }).reset_index()
                roi_df['roi'] = roi_df['revenue'] / roi_df['payout']
                roi_df['roas'] = roi_df['revenue'] / roi_df['spend']

                fig_roi = px.bar(
                    roi_df.sort_values('roi', ascending=False),
                    x='name',
                    y='roi',
                    title='Top Influencers by ROI',
                    color='roi',
                    color_continuous_scale='aggrnyl',
                    labels={'roi': 'ROI'},
                    template='plotly_white'
                )
                fig_roi.update_layout(xaxis_title="Influencer", yaxis_title="ROI")
                st.plotly_chart(fig_roi, use_container_width=True)

                fig_roas = px.bar(
                    roi_df.sort_values('roas', ascending=False),
                    x='name',
                    y='roas',
                    title='Top Influencers by ROAS',
                    color='roas',
                    color_continuous_scale='sunsetdark',
                    labels={'roas': 'ROAS'},
                    template='plotly_white'
                )
                fig_roas.update_layout(xaxis_title="Influencer", yaxis_title="ROAS")
                st.plotly_chart(fig_roas, use_container_width=True)

                st.divider()

                st.subheader("📅 Daily Campaign Metrics")
                daily_summary = tracking_data.groupby('date').agg({
                    'spend': 'sum',
                    'revenue': 'sum'
                }).reset_index()
                daily_summary['roi'] = daily_summary['revenue'] / daily_summary['spend']

                fig_time = px.line(
                    daily_summary,
                    x='date',
                    y=['spend', 'revenue'],
                    title='📆 Daily Spend vs Revenue',
                    markers=True,
                    template='plotly_white'
                )
                fig_time.update_traces(mode='lines+markers')
                st.plotly_chart(fig_time, use_container_width=True)

                st.divider()

                st.subheader("🎯 ROI vs ROAS Correlation")
                scatter_fig = px.scatter(
                    roi_df,
                    x='roi',
                    y='roas',
                    size='revenue',
                    color='name',
                    hover_name='name',
                    title='Influencer ROI vs ROAS Scatter',
                    template='plotly_white'
                )
                st.plotly_chart(scatter_fig, use_container_width=True)

                st.divider()

                st.subheader("📜 Data Snapshot")
                with st.expander("🔍 View Merged Data Table"):
                    st.dataframe(merged.head(100), use_container_width=True)

                st.caption("Dashboard built with 💙 using Streamlit and Plotly")
