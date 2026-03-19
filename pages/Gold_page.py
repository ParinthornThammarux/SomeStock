import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ================================
# Load Data
# ================================
@st.cache_data
def load_data():
    df = pd.read_csv("./TrainMLModel/predictions.csv", index_col=0, parse_dates=True)
    return df

# ================================
# Plot Function
# ================================
def plot_chart(df):
    fig, ax = plt.subplots(figsize=(12,6))

    ax.plot(df.index, df["Actual"], label="Actual")
    ax.plot(df.index, df["Linear Regression"], label="Linear Regression")

    ax.set_title("Gold Price vs Linear Regression (Last 1 Year)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()

    return fig

# ================================
# Main Render Function
# ================================
def render():
    st.title("Gold Price Prediction Dashboard")

    df = load_data()

    # ================================
    # 📊 Metrics (ใช้ Linear Regression)
    # ================================
    latest_actual = df["Actual"].iloc[-1]
    latest_pred = df["Linear Regression"].iloc[-1]

    col1, col2 = st.columns(2)

    col1.metric(
        "Gold Price (Latest)",
        f"{latest_actual:,.2f}"
    )

    col2.metric(
        "Predicted Price (7 Days Ahead)",
        f"{latest_pred:,.2f}",
        delta=f"{latest_pred - latest_actual:,.2f}"
    )

    st.markdown("---")

    # ================================
    # 📈 Chart
    # ================================
    st.subheader("Prediction vs Actual (Last 1 Year)")
    fig = plot_chart(df)
    st.pyplot(fig)