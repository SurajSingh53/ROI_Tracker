import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Influencer ROI Tracker", layout="wide")

st.title("📈 Influencer Campaign ROI Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = ["brand", "product", "revenue", "clicks", "cost_per_click", "total_payout"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing one or more required columns: {required_cols}")
        st.stop()

    df["ROI"] = df["revenue"] / df["total_payout"]
    df["ROAS"] = df["revenue"] / (df["clicks"] * df["cost_per_click"])
    df["incremental_ROAS"] = df["ROAS"] - df["ROI"]

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    else:
        st.warning("No 'date' column found in the uploaded file. Time series charts will be disabled.")

    brands = df["brand"].dropna().unique()
    products = df["product"].dropna().unique()

    st.sidebar.header("Filters")
    selected_brand = st.sidebar.selectbox("Brand", options=["All"] + list(brands))
    selected_product = st.sidebar.selectbox("Product", options=["All"] + list(products))

    if selected_brand != "All":
        df = df[df["brand"] == selected_brand]
    if selected_product != "All":
        df = df[df["product"] == selected_product]

    st.subheader("📊 ROI & ROAS Overview")
    st.dataframe(df[["brand", "product", "revenue", "total_payout", "ROI", "ROAS", "incremental_ROAS"]].sort_values("ROI", ascending=False))

    col1, col2, col3 = st.columns(3)
    col1.metric("Average ROI", f"{df['ROI'].mean():.2f}")
    col2.metric("Average ROAS", f"{df['ROAS'].mean():.2f}")
    col3.metric("Avg Incremental ROAS", f"{df['incremental_ROAS'].mean():.2f}")

    st.subheader("📉 ROI Distribution")
    fig1 = px.histogram(df, x="ROI", nbins=30, title="ROI Distribution")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📊 Top Influencer Performance")
    if "influencer" in df.columns:
        top_df = df.groupby("influencer")[["ROI", "ROAS", "incremental_ROAS"]].mean().sort_values("ROI", ascending=False).head(10)
        st.dataframe(top_df)
    else:
        st.info("No 'influencer' column found to display performance.")

    if "date" in df.columns:
        st.subheader("🗓️ ROI Over Time")
        time_fig = px.line(df.sort_values("date"), x="date", y="ROI", title="ROI Trend")
        st.plotly_chart(time_fig, use_container_width=True)
