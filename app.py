import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import io
from fpdf import FPDF
import tempfile
import os

# Set page config
st.set_page_config(
    page_title="HealthKart Influencer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data with caching
@st.cache_data
def load_data():
    influencers = pd.read_csv('influencers.csv')
    posts = pd.read_csv('posts.csv')
    tracking_data = pd.read_csv('tracking_data.csv')
    payouts = pd.read_csv('payouts.csv')
    
    # Convert date columns to datetime
    for df in [posts, tracking_data, payouts]:
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
    if 'payout_date' in payouts.columns:
        payouts['payout_date'] = pd.to_datetime(payouts['payout_date'])
    
    return influencers, posts, tracking_data, payouts

influencers, posts, tracking_data, payouts = load_data()

# Merge data for analysis
@st.cache_data
def create_merged_data(influencers, posts, tracking_data, payouts):
    # Merge tracking data with influencers
    campaign_performance = tracking_data.merge(
        influencers,
        on='influencer_id',
        how='left'
    )
    
    # Merge with payouts
    campaign_performance = campaign_performance.merge(
        payouts.groupby(['influencer_id', 'campaign']).agg({'total_payout': 'sum'}).reset_index(),
        on=['influencer_id', 'campaign'],
        how='left'
    )
    
    # Calculate metrics
    campaign_performance['ROAS'] = campaign_performance['revenue'] / campaign_performance['total_payout']
    campaign_performance['CPO'] = campaign_performance['total_payout'] / campaign_performance['orders']
    campaign_performance['incremental_ROAS'] = (campaign_performance['revenue'] - (campaign_performance['clicks'] * campaign_performance['cost_per_click'])) / campaign_performance['total_payout']
    
    # Merge posts data for engagement metrics
    post_metrics = posts.groupby('influencer_id').agg({
        'reach': 'mean',
        'likes': 'mean',
        'comments': 'mean',
        'shares': 'mean',
        'saves': 'mean'
    }).reset_index()
    
    campaign_performance = campaign_performance.merge(
        post_metrics,
        on='influencer_id',
        how='left'
    )
    
    # Calculate engagement rate from posts
    if 'likes' in campaign_performance.columns and 'reach' in campaign_performance.columns:
        campaign_performance['calculated_engagement_rate'] = (
            (campaign_performance['likes'] + 
             campaign_performance['comments'] + 
             campaign_performance['shares'] + 
             campaign_performance['saves']) / 
            campaign_performance['reach']
        ) * 100
    
    return campaign_performance

campaign_performance = create_merged_data(influencers, posts, tracking_data, payouts)

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
min_date = min(posts['date'].min(), tracking_data['date'].min(), payouts['payout_date'].min())
max_date = max(posts['date'].max(), tracking_data['date'].max(), payouts['payout_date'].max())

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Convert to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date) + timedelta(days=1)  # Include end date

# Other filters
selected_brands = st.sidebar.multiselect(
    "Brands",
    options=tracking_data['brand'].unique(),
    default=tracking_data['brand'].unique()
)

selected_platforms = st.sidebar.multiselect(
    "Platforms",
    options=influencers['platform'].unique(),
    default=influencers['platform'].unique()
)

selected_categories = st.sidebar.multiselect(
    "Influencer Categories",
    options=influencers['category'].unique(),
    default=influencers['category'].unique()
)

selected_genders = st.sidebar.multiselect(
    "Genders",
    options=influencers['gender'].unique(),
    default=influencers['gender'].unique()
)

# Apply filters
def filter_data(df):
    filtered = df.copy()
    
    if 'date' in filtered.columns:
        filtered = filtered[(filtered['date'] >= start_date) & (filtered['date'] <= end_date)]
    elif 'payout_date' in filtered.columns:
        filtered = filtered[(filtered['payout_date'] >= start_date) & (filtered['payout_date'] <= end_date)]
    
    if 'brand' in filtered.columns and selected_brands:
        filtered = filtered[filtered['brand'].isin(selected_brands)]
    
    if 'platform' in filtered.columns and selected_platforms:
        filtered = filtered[filtered['platform'].isin(selected_platforms)]
    
    if 'category' in filtered.columns and selected_categories:
        filtered = filtered[filtered['category'].isin(selected_categories)]
    
    if 'gender' in filtered.columns and selected_genders:
        filtered = filtered[filtered['gender'].isin(selected_genders)]
    
    return filtered

filtered_performance = filter_data(campaign_performance)
filtered_posts = filter_data(posts)
filtered_payouts = filter_data(payouts)
filtered_influencers = filter_data(influencers)

# Dashboard title
st.title("HealthKart Influencer Campaign Dashboard")

# KPI cards
st.subheader("Campaign Performance Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_performance['revenue'].sum()
    st.metric("Total Revenue", f"₹{total_revenue:,.0f}")

with col2:
    total_payout = filtered_payouts['total_payout'].sum()
    st.metric("Total Payout", f"₹{total_payout:,.0f}")

with col3:
    avg_roas = filtered_performance['ROAS'].mean() if not filtered_performance.empty else 0
    st.metric("Average ROAS", f"{avg_roas:.2f}")

with col4:
    total_orders = filtered_performance['orders'].sum()
    st.metric("Total Orders", f"{total_orders:,.0f}")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Campaign Performance", 
    "Influencer Insights", 
    "ROAS Analysis", 
    "Payout Tracking"
])

with tab1:
    st.subheader("Campaign Performance Metrics")
    
    # Group by campaign and calculate metrics
    campaign_metrics = filtered_performance.groupby(['campaign', 'brand']).agg({
        'revenue': 'sum',
        'orders': 'sum',
        'total_payout': 'sum',
        'clicks': 'sum',
        'ROAS': 'mean',
        'incremental_ROAS': 'mean',
        'CPO': 'mean'
    }).reset_index()
    
    # Display metrics table
    st.dataframe(
        campaign_metrics.sort_values('revenue', ascending=False),
        column_config={
            'revenue': st.column_config.NumberColumn("Revenue", format="₹%.0f"),
            'total_payout': st.column_config.NumberColumn("Payout", format="₹%.0f"),
            'ROAS': st.column_config.NumberColumn("ROAS", format="%.2f"),
            'incremental_ROAS': st.column_config.NumberColumn("Incremental ROAS", format="%.2f"),
            'CPO': st.column_config.NumberColumn("Cost Per Order", format="₹%.2f")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Revenue by campaign chart
    fig = px.bar(
        campaign_metrics.sort_values('revenue', ascending=False),
        x='campaign',
        y='revenue',
        color='brand',
        title="Revenue by Campaign",
        labels={'revenue': 'Revenue (₹)', 'campaign': 'Campaign'},
        text_auto='.2s'
    )
    fig.update_layout(barmode='stack')
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance over time
    st.subheader("Performance Over Time")
    
    time_period = st.selectbox(
        "Time Period",
        ["Daily", "Weekly", "Monthly"],
        key="performance_time_period"
    )
    
    time_group = filtered_performance.copy()
    if time_period == "Daily":
        time_group['period'] = time_group['date'].dt.date
    elif time_period == "Weekly":
        time_group['period'] = time_group['date'].dt.to_period('W').dt.start_time
    else:  # Monthly
        time_group['period'] = time_group['date'].dt.to_period('M').dt.start_time
    
    time_metrics = time_group.groupby(['period', 'brand']).agg({
        'revenue': 'sum',
        'orders': 'sum',
        'total_payout': 'sum'
    }).reset_index()
    
    # Line chart for revenue and payout over time
    fig = px.line(
        time_metrics,
        x='period',
        y=['revenue', 'total_payout'],
        color='brand',
        title="Revenue vs Payout Over Time",
        labels={'value': 'Amount (₹)', 'period': 'Date', 'variable': 'Metric'},
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Influencer Insights")
    
    # Top influencers by revenue
    top_influencers = filtered_performance.groupby(['influencer_id', 'name', 'platform', 'category', 'gender']).agg({
        'revenue': 'sum',
        'orders': 'sum',
        'total_payout': 'sum',
        'ROAS': 'mean',
        'reach': 'mean',
        'calculated_engagement_rate': 'mean'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top Influencers by Revenue**")
        st.dataframe(
            top_influencers.sort_values('revenue', ascending=False).head(10),
            column_config={
                'revenue': st.column_config.NumberColumn("Revenue", format="₹%.0f"),
                'total_payout': st.column_config.NumberColumn("Payout", format="₹%.0f"),
                'ROAS': st.column_config.NumberColumn("ROAS", format="%.2f"),
                'calculated_engagement_rate': st.column_config.NumberColumn("Engagement Rate", format="%.2f%%")
            },
            hide_index=True,
            use_container_width=True
        )
    
    with col2:
        st.markdown("**Top Influencers by ROAS**")
        st.dataframe(
            top_influencers[top_influencers['orders'] > 0].sort_values('ROAS', ascending=False).head(10),
            column_config={
                'revenue': st.column_config.NumberColumn("Revenue", format="₹%.0f"),
                'total_payout': st.column_config.NumberColumn("Payout", format="₹%.0f"),
                'ROAS': st.column_config.NumberColumn("ROAS", format="%.2f"),
                'calculated_engagement_rate': st.column_config.NumberColumn("Engagement Rate", format="%.2f%%")
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Influencer personas analysis
    st.subheader("Persona Performance Analysis")
    
    persona_metrics = filtered_performance.groupby(['category', 'gender', 'platform']).agg({
        'revenue': 'sum',
        'orders': 'sum',
        'total_payout': 'sum',
        'ROAS': 'mean',
        'influencer_id': 'nunique'
    }).reset_index()
    
    # Best performing personas
    fig = px.treemap(
        persona_metrics,
        path=['platform', 'category', 'gender'],
        values='revenue',
        color='ROAS',
        color_continuous_scale='RdYlGn',
        title="Revenue by Influencer Persona (Size=Revenue, Color=ROAS)",
        hover_data=['orders', 'total_payout', 'influencer_id']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Engagement vs Performance
    st.subheader("Engagement vs Performance")
    
    if not filtered_performance.empty:
        fig = px.scatter(
            top_influencers,
            x='calculated_engagement_rate',
            y='ROAS',
            size='revenue',
            color='platform',
            hover_name='name',
            title="Engagement Rate vs ROAS",
            labels={
                'calculated_engagement_rate': 'Engagement Rate (%)',
                'ROAS': 'ROAS',
                'revenue': 'Revenue'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("ROAS Analysis")
    
    # ROAS distribution
    fig = px.box(
        filtered_performance[filtered_performance['orders'] > 0],
        y='ROAS',
        x='platform',
        color='brand',
        title="ROAS Distribution by Platform and Brand",
        points="all"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Incremental ROAS analysis
    st.subheader("Incremental ROAS Analysis")
    
    if not filtered_performance.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=filtered_performance['campaign'],
            y=filtered_performance['ROAS'],
            name='ROAS',
            marker_color='#636EFA'
        ))
        
        fig.add_trace(go.Bar(
            x=filtered_performance['campaign'],
            y=filtered_performance['incremental_ROAS'],
            name='Incremental ROAS',
            marker_color='#EF553B'
        ))
        
        fig.update_layout(
            barmode='group',
            title="ROAS vs Incremental ROAS by Campaign",
            xaxis_title="Campaign",
            yaxis_title="Value"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ROAS drivers analysis
    st.subheader("ROAS Drivers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # By platform
        platform_roas = filtered_performance.groupby('platform')['ROAS'].mean().reset_index()
        fig = px.bar(
            platform_roas.sort_values('ROAS', ascending=False),
            x='platform',
            y='ROAS',
            title="Average ROAS by Platform"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # By influencer category
        category_roas = filtered_performance.groupby('category')['ROAS'].mean().reset_index()
        fig = px.bar(
            category_roas.sort_values('ROAS', ascending=False),
            x='category',
            y='ROAS',
            title="Average ROAS by Influencer Category"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Payout Tracking")
    
    # Payout summary
    payout_summary = filtered_payouts.groupby(['campaign', 'basis']).agg({
        'total_payout': 'sum',
        'posts_count': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    st.dataframe(
        payout_summary,
        column_config={
            'total_payout': st.column_config.NumberColumn("Total Payout", format="₹%.0f"),
            'posts_count': st.column_config.NumberColumn("Posts Count"),
            'orders': st.column_config.NumberColumn("Orders")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Payout by influencer
    influencer_payouts = filtered_payouts.groupby(['influencer_id', 'campaign', 'basis']).agg({
        'total_payout': 'sum',
        'posts_count': 'sum',
        'orders': 'sum'
    }).reset_index().merge(
        influencers[['influencer_id', 'name', 'platform']],
        on='influencer_id',
        how='left'
    )
    
    st.dataframe(
        influencer_payouts.sort_values('total_payout', ascending=False),
        column_config={
            'total_payout': st.column_config.NumberColumn("Total Payout", format="₹%.0f"),
            'posts_count': st.column_config.NumberColumn("Posts Count"),
            'orders': st.column_config.NumberColumn("Orders")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Payout over time
    st.subheader("Payouts Over Time")
    
    payout_time = filtered_payouts.groupby(['payout_date', 'basis']).agg({
        'total_payout': 'sum'
    }).reset_index()
    
    fig = px.line(
        payout_time,
        x='payout_date',
        y='total_payout',
        color='basis',
        title="Payouts Over Time by Payment Basis",
        labels={'total_payout': 'Total Payout (₹)', 'payout_date': 'Date'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Data export functionality
st.sidebar.header("Data Export")

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

def create_pdf_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.cell(200, 10, txt="HealthKart Influencer Campaign Report", ln=1, align='C')
    
    # Add date range
    pdf.cell(200, 10, txt=f"Date Range: {start_date.date()} to {end_date.date()}", ln=1, align='C')
    
    # Add KPIs
    pdf.cell(200, 10, txt="Key Performance Indicators", ln=1, align='L')
    pdf.cell(200, 10, txt=f"Total Revenue: ₹{total_revenue:,.0f}", ln=1)
    pdf.cell(200, 10, txt=f"Total Payout: ₹{total_payout:,.0f}", ln=1)
    pdf.cell(200, 10, txt=f"Average ROAS: {avg_roas:.2f}", ln=1)
    pdf.cell(200, 10, txt=f"Total Orders: {total_orders:,.0f}", ln=1)
    
    # Add top influencers
    pdf.cell(200, 10, txt="Top 5 Influencers by Revenue", ln=1, align='L')
    top_influencers_list = top_influencers.sort_values('revenue', ascending=False).head(5)
    for idx, row in top_influencers_list.iterrows():
        pdf.cell(200, 10, txt=f"{row['name']} - 'Rs '{row['revenue']:,.0f} (ROAS: {row['ROAS']:.2f})", ln=1)
    
    return pdf

# Export buttons
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("Export Data to Excel"):
        excel_data = to_excel(filtered_performance)
        st.sidebar.download_button(
            label="Download Excel",
            data=excel_data,
            file_name="influencer_performance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with col2:
    if st.button("Generate PDF Report"):
        pdf = create_pdf_report()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.close()
            pdf.output(tmp.name)
            
            with open(tmp.name, "rb") as f:
                pdf_bytes = f.read()
            
            os.unlink(tmp.name)
        
        st.sidebar.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name="influencer_report.pdf",
            mime="application/pdf"
        )

# Assumptions and notes
st.sidebar.header("Assumptions")
st.sidebar.markdown("""
1. **Incremental ROAS Calculation**:  
   Calculated as `(Revenue - (Clicks * CPC)) / Payout` to estimate incremental value.
   
2. **Engagement Rate**:  
   Calculated as `(Likes + Comments + Shares + Saves) / Reach * 100`.

3. **Data Merging**:  
   Campaign data is merged at influencer level for analysis.

4. **Date Filtering**:  
   Applies to all relevant date columns in each dataset.
""")
