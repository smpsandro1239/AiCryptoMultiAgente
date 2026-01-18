import streamlit as st
import pandas as pd
import json
import os
import sys
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Adicionar raiz do projeto ao path
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
    st.title("🤖 Dashboard MATF - Negociação Multi-Agente")

    # API Connection
    st.sidebar.header("Ligação à API")
    api_url = st.sidebar.text_input("URL Base da API", "http://localhost:8000")
    if st.sidebar.button("Verificar Estado"):
        try:
            resp = requests.get(f"{api_url}/status")
            st.sidebar.success(f"Ligado: {resp.json()['status']}")
        except:
            st.sidebar.error("API Offline")

    # Strategy Marketplace
    sm = StrategyManager()
    st.sidebar.header("Mercado de Estratégias")
    selected_strategy = st.sidebar.selectbox("Carregar Estratégia", ["Nenhuma"] + sm.list_strategies())
    if selected_strategy != "Nenhuma":
        st.sidebar.json(sm.get_strategy(selected_strategy))

    st.sidebar.header("Fonte de Dados")
    results_file = st.sidebar.text_input("Caminho JSON de Resultados", "backtest_results.json")

    data = load_data(results_file)

    if data:
        pnl_df = pd.DataFrame(data["pnl"])
        memory_df = pd.DataFrame([m for m in data["memory"]])
        metrics = data.get("metrics", {})

        tabs = ["Performance", "Execuções", "Auditoria IA", "HFT & Scalping", "Mercado & DeFi", "Stress Testing", "Painel Controlo"]
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tabs)

        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                final_val = pnl_df['value'].iloc[-1]
                initial_val = pnl_df['value'].iloc[0]
                st.metric("Valor Portfólio", f"${final_val:,.2f}", delta=f"{((final_val/initial_val)-1)*100:.2f}%")
            with col2:
                st.metric("Rácio Sharpe", f"{metrics.get('sharpe_ratio', 0):.2f}")
            with col3:
                st.metric("Drawdown Máximo", f"{metrics.get('max_drawdown', 0)*100:.2f}%")
            with col4:
                st.metric("Total de Trocas", len(memory_df[memory_df['key'] == 'execution']))

            st.subheader("Curva de Equity")
            st.line_chart(pnl_df.set_index('timestamp')['value'])

            st.subheader("Visualização de Ordens")
            trades = [m['value'] for m in data['memory'] if m['key'] == 'execution']
            if trades:
                mock_prices = pd.DataFrame({"timestamp": pnl_df["timestamp"], "close": [40000 + i*100 for i in range(len(pnl_df))]})
                fig = create_trade_plot(mock_prices, trades)
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("Registo de Execuções")
            executions = []
            for m in data["memory"]:
                if m["key"] == "execution":
                    val = m["value"]
                    executions.append({
                        "Tempo": val.get("timestamp"),
                        "Símbolo": val.get("symbol"),
                        "Lado": val.get("side"),
                        "Preço": val.get("price"),
                        "PnL": val.get("pnl", 0)
                    })
            if executions: st.dataframe(pd.DataFrame(executions))

        with tab3:
            st.subheader("Auditoria de Raciocínio IA")
            audit_log = [m['value'] for m in data["memory"] if m["key"] == "execution"]
            if audit_log:
                for entry in audit_log:
                    side = entry.get('side', entry.get('Side', 'N/A'))
                    symbol = entry.get('symbol', entry.get('Symbol', 'N/A'))
                    with st.expander(f"{side} {symbol} - {entry.get('timestamp')}"):
                        st.write(entry.get('rationale'))

        with tab4:
            st.subheader("Análise HFT & Scalping")
            st.info("Monitorização de micro-tendências e sinais de alta frequência.")
            scalps = [m['value'] for m in data['memory'] if m.get('key') == 'opportunity_found' and 'Scalping' in str(m['value'].get('reason'))]
            if scalps:
                st.write("Sinais de Scalping Detetados")
                st.dataframe(pd.DataFrame(scalps))
            else:
                st.write("Sem sinais HFT recentes.")

        with tab5:
            st.subheader("Arbitragem & DeFi")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("Sinais de Arbitragem")
                arbs = [m['value'] for m in data['memory'] if m['key'] == 'arbitrage_signal']
                if arbs: st.dataframe(pd.DataFrame(arbs))
            with col_b:
                st.write("Oportunidades DeFi Yield")
                yields = [m['value'] for m in data['memory'] if m['key'] == 'defi_opportunity']
                if yields: st.dataframe(pd.DataFrame(yields))

        with tab6:
            st.subheader("Modelação de Risco")
            risk_logs = [m['value'] for m in data['memory'] if m['key'] == 'risk_analysis']
            if risk_logs:
                latest_risk = risk_logs[-1]
                st.write(f"Símbolo: {latest_risk['symbol']} | VaR Histórico: {latest_risk['var_historical']:.2%}")
                fig_sim = px.histogram(latest_risk['sim_final_prices'], nbins=50, title="Distribuição Monte Carlo")
                st.plotly_chart(fig_sim)

        with tab7:
            st.subheader("Painel de Controlo Remoto")
            with st.form("ordem_manual"):
                symbol = st.selectbox("Símbolo", ["BTC/USDT", "ETH/USDT"])
                side = st.selectbox("Lado", ["BUY", "SELL"])
                amount = st.number_input("Montante (USD)", min_value=10.0, value=100.0)
                submit = st.form_submit_button("Enviar Ordem")
                if submit:
                    try:
                        api_url = "http://localhost:8000"
                        r = requests.post(f"{api_url}/trade/manual", params={"symbol": symbol, "side": side, "amount": amount})
                        st.success(f"Ordem submetida: {r.json()}")
                    except:
                        st.error("Não foi possível contactar a API")

    else:
        st.warning(f"Ficheiro {results_file} não encontrado.")

if __name__ == "__main__":
    main()
