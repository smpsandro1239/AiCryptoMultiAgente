import streamlit as st
import pandas as pd
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from multiagent_trading.core.strategy import StrategyManager

def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)

def main():
    st.set_page_config(page_title="MATF Dashboard", layout="wide")
    st.title("🤖 MATF Dashboard - Multi-Agent Trading")

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

        tab1, tab2, tab3, tab4 = st.tabs(["Performance", "Executions", "Microstructure", "Notifications"])

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

            st.subheader("Trade Replay")
            tick_index = st.slider("Select Tick", 0, len(pnl_df)-1, 0)
            st.write(f"State at Tick {tick_index}:")
            st.json(pnl_df.iloc[tick_index].to_dict())

        with tab2:
            st.subheader("Agent Execution Log")
            executions = []
            for m in data["memory"]:
                if m["key"] == "execution":
                    val = m["value"]
                    executions.append({
                        "Symbol": val.get("symbol"),
                        "Side": val.get("side"),
                        "Type": val.get("type"),
                        "Price": val.get("price"),
                        "Qty": val.get("qty", val.get("usd_size", "N/A"))
                    })
            if executions:
                st.dataframe(pd.DataFrame(executions))
            else:
                st.info("No executions found in memory.")

        with tab3:
            st.subheader("Microstructure Analysis")
            st.info("Microstructure analysis tracks order book imbalance and bid-ask spreads.")
            mock_ms = pd.DataFrame({
                "Symbol": ["BTC/USDT", "ETH/USDT"],
                "Spread": [0.0001, 0.00015],
                "Imbalance": [0.15, -0.05],
                "Liquidity": ["High", "High"]
            })
            st.table(mock_ms)

        with tab4:
            st.subheader("System Notifications")
            notifications = []
            for m in data["memory"]:
                if m["key"] == "notification":
                    notifications.append(m["value"])
            if notifications:
                for n in reversed(notifications):
                    st.info(n)
            else:
                st.write("No notifications logged.")

    else:
        st.warning(f"File {results_file} not found. Run a backtest first.")
        st.info("Example: `python examples/backtest_example.py` (ensure it saves to backtest_results.json)")

if __name__ == "__main__":
    main()
