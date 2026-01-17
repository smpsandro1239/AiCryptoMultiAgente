import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Mocking a way to get data if not running within a live session
def get_mock_results():
    dates = pd.date_range(start="2026-01-01", periods=100, freq="H")
    pnl = np.cumsum(np.random.normal(0.5, 2, 100)) + 10000
    return pd.DataFrame({"Timestamp": dates, "PnL": pnl})

def main():
    st.set_page_config(page_title="MATF Dashboard", layout="wide")
    st.title("🤖 Multi-Agent Trading Framework (MATF) Dashboard")

    st.sidebar.header("Configuration")
    mode = st.sidebar.selectbox("Mode", ["Backtest", "Live Monitoring"])

    col1, col2, col3 = st.columns(3)

    # Mock data for demonstration
    df = get_mock_results()

    with col1:
        st.metric("Total PnL", f"${df['PnL'].iloc[-1] - 10000:.2f}", delta=f"{((df['PnL'].iloc[-1]/10000)-1)*100:.2f}%")
    with col2:
        st.metric("Active Agents", "5")
    with col3:
        st.metric("Trades Executed", "42")

    st.subheader("Performance Over Time")
    st.line_chart(df.set_index("Timestamp"))

    st.subheader("Agent Activity Log")
    activity_log = [
        {"Time": "2026-01-16 10:00", "Agent": "Scanner", "Action": "Opportunity Found BTC/USDT"},
        {"Time": "2026-01-16 10:01", "Agent": "Risk", "Action": "Risk Assessed: OK"},
        {"Time": "2026-01-16 10:01", "Agent": "Supervisor", "Action": "Trade Approved"},
        {"Time": "2026-01-16 10:02", "Agent": "Execution", "Action": "BUY Order Executed at $42,500"},
        {"Time": "2026-01-16 10:05", "Agent": "Regime", "Action": "Regime Change: BULL -> SIDEWAYS"},
    ]
    st.table(pd.DataFrame(activity_log))

    st.subheader("Portfolio Distribution")
    portfolio_data = pd.DataFrame({
        'Asset': ['BTC', 'ETH', 'USDT', 'SOL'],
        'Value': [4500, 2500, 2000, 1000]
    })
    st.bar_chart(portfolio_data.set_index('Asset'))

if __name__ == "__main__":
    main()
