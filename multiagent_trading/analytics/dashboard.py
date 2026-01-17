import streamlit as st
import pandas as pd
import json
import os
import sys
import requests
import plotly.express as px

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from multiagent_trading.core.strategy import StrategyManager
from multiagent_trading.analytics.plots import create_trade_plot

def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)

def main():
    st.set_page_config(page_title="MATF Dashboard", layout="wide")
    st.title("🤖 MATF Dashboard - Multi-Agent Trading")

    # API Connection
    st.sidebar.header("API Connection")
    api_url = st.sidebar.text_input("API Base URL", "http://localhost:8000")
    if st.sidebar.button("Check API Status"):
        try:
            resp = requests.get(f"{api_url}/status")
            st.sidebar.success(f"Connected: {resp.json()['status']}")
        except:
            st.sidebar.error("API Offline")

    # Strategy Marketplace
    sm = StrategyManager()
    st.sidebar.header("Strategy Marketplace")
    selected_strategy = st.sidebar.selectbox("Load Strategy", ["None"] + sm.list_strategies())
    if selected_strategy != "None":
        st.sidebar.json(sm.get_strategy(selected_strategy))

    st.sidebar.header("Data Source")
    results_file = st.sidebar.text_input("Results JSON Path", "backtest_results.json")

    data = load_data(results_file)

    if data:
        pnl_df = pd.DataFrame(data["pnl"])
        memory_df = pd.DataFrame([m for m in data["memory"]])
        metrics = data.get("metrics", {})

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Performance", "Executions", "AI Reasoning", "Market Insights", "DeFi & Yield", "Control Panel"])

        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                final_val = pnl_df['value'].iloc[-1]
                initial_val = pnl_df['value'].iloc[0]
                st.metric("Portfolio Value", f"${final_val:,.2f}", delta=f"{((final_val/initial_val)-1)*100:.2f}%")
            with col2:
                st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}")
            with col3:
                st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0)*100:.2f}%")
            with col4:
                st.metric("Total Trades", len(memory_df[memory_df['key'] == 'execution']))

            st.subheader("Equity Curve")
            st.line_chart(pnl_df.set_index('timestamp')['value'])

            st.subheader("Trade Visualization")
            trades = [m['value'] for m in data['memory'] if m['key'] == 'execution']
            if trades:
                mock_prices = pd.DataFrame({"timestamp": pnl_df["timestamp"], "close": [40000 + i*100 for i in range(len(pnl_df))]})
                fig = create_trade_plot(mock_prices, trades)
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("PnL Attribution")
            attr = [m['value'] for m in data['memory'] if m['key'] == 'pnl_attribution']
            if attr:
                st.bar_chart(pd.Series(attr[-1]))
            else:
                st.info("No PnL attribution data found.")

        with tab2:
            st.subheader("Agent Execution Log")
            executions = []
            for m in data["memory"]:
                if m["key"] == "execution":
                    val = m["value"]
                    executions.append({
                        "Time": val.get("timestamp"),
                        "Symbol": val.get("symbol"),
                        "Side": val.get("side"),
                        "Price": val.get("price"),
                        "PnL": val.get("pnl", 0)
                    })
            if executions:
                st.dataframe(pd.DataFrame(executions))

        with tab3:
            st.subheader("AI Reasoning Audit")
            audit_log = [m['value'] for m in data["memory"] if m["key"] == "execution"]
            if audit_log:
                for entry in audit_log:
                    with st.expander(f"{entry['Side']} {entry['Symbol']} - {entry.get('timestamp')}"):
                        st.write(entry.get('rationale'))

        with tab4:
            st.subheader("Arbitrage & Microstructure")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("Arbitrage Signals")
                arbs = [m['value'] for m in data['memory'] if m['key'] == 'arbitrage_signal']
                if arbs: st.dataframe(pd.DataFrame(arbs))
                else: st.info("No arbitrage signals.")
            with col_b:
                st.write("Microstructure Logs")
                st.info("Tracks order book imbalance and bid-ask spreads.")

        with tab5:
            st.subheader("DeFi Yield Farming & Staking")
            yields = [m['value'] for m in data['memory'] if m['key'] == 'defi_opportunity']
            if yields:
                st.write("Active Yield Opportunities")
                st.dataframe(pd.DataFrame(yields))
            else:
                st.info("No DeFi opportunities logged.")

        with tab6:
            st.subheader("Remote Control Panel")
            with st.form("manual_order"):
                symbol = st.selectbox("Symbol", ["BTC/USDT", "ETH/USDT"])
                side = st.selectbox("Side", ["BUY", "SELL"])
                amount = st.number_input("Amount (USD)", min_value=10.0, value=100.0)
                submit = st.form_submit_button("Send Order")
                if submit:
                    try:
                        api_url = "http://localhost:8000"
                        r = requests.post(f"{api_url}/trade/manual", params={"symbol": symbol, "side": side, "amount": amount})
                        st.success(f"Order submitted: {r.json()}")
                    except:
                        st.error("Could not reach API")

    else:
        st.warning(f"File {results_file} not found.")

if __name__ == "__main__":
    main()
