import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import os

st.set_page_config(layout="wide")
st.title("📊 Influencer ROI Tracker Dashboard")

uploaded_file = st.file_uploader("Upload your influencer CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Raw Data Preview")
    st.dataframe(df.head(20), use_container_width=True)

    with st.expander("Show Summary Statistics"):
        st.write(df.describe())

    st.subheader("Campaign Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Campaigns", df["Campaign Name"].nunique())
    with col2:
        st.metric("Total Influencers", df["Influencer Name"].nunique())
    with col3:
        st.metric("Total Spent", f"₹{df['Amount Spent'].sum():,.0f}")
    with col4:
        st.metric("Total Revenue", f"₹{df['Revenue Generated'].sum():,.0f}")

    df["ROAS"] = df["Revenue Generated"] / df["Amount Spent"]
    df["ROI (%)"] = ((df["Revenue Generated"] - df["Amount Spent"]) / df["Amount Spent"]) * 100

    st.subheader("📈 ROAS by Campaign")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.barplot(data=df, x="Campaign Name", y="ROAS", hue="Platform", ax=ax1)
    ax1.set_title("ROAS by Campaign")
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)

    st.subheader("📈 ROI (%) by Influencer")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.barplot(data=df.sort_values("ROI (%)", ascending=False), x="Influencer Name", y="ROI (%)", ax=ax2)
    ax2.set_title("ROI (%) by Influencer")
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)

    st.subheader("📈 Revenue vs Spend")
    fig3, ax3 = plt.subplots(figsize=(6, 6))
    sns.scatterplot(data=df, x="Amount Spent", y="Revenue Generated", hue="Platform", ax=ax3)
    ax3.plot([df['Amount Spent'].min(), df['Amount Spent'].max()], [df['Amount Spent'].min(), df['Amount Spent'].max()], 'r--')
    ax3.set_title("Revenue vs Spend")
    st.pyplot(fig3)

    st.subheader("💡 Predict Revenue from Spend")
    if st.checkbox("Enable Revenue Predictor"):
        X = df[["Amount Spent"]]
        y = df["Revenue Generated"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        st.markdown(f"**Model R² Score:** {r2:.2f}")
        st.markdown(f"**Mean Squared Error:** {mse:.2f}")

        input_spend = st.number_input("Enter Spend to Predict Revenue", min_value=0.0, step=100.0)
        if input_spend:
            predicted = model.predict([[input_spend]])[0]
            st.success(f"Estimated Revenue: ₹{predicted:,.0f}")

else:
    st.info("👆 Upload a CSV file to begin tracking ROI!")
