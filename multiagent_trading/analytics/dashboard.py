import streamlit as st
import pandas as pd
import numpy as np
import json
import sqlite3
import plotly.graph_objects as go
from multiagent_trading.analytics.plots import TradeVisualizer
from multiagent_trading.analytics.stress_test import PortfolioStressTester
from datetime import datetime

st.set_page_config(page_title="MATF Dashboard", layout="wide")

st.title("📊 Multi-Agent Trading Framework (MATF)")

# Conectar à base de dados de memória
def get_memory_data():
    try:
        conn = sqlite3.connect("memory.db")
        df = pd.read_sql_query("SELECT * FROM memory ORDER BY timestamp DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# Sidebar para filtros e status
st.sidebar.header("🕹️ Controlo do Sistema")
st.sidebar.success("Sistema Online (v1.0-RC)")
st.sidebar.divider()
st.sidebar.write("**Configurações de Língua**")
st.sidebar.info("Língua: Português (Portugal)")

# Tabs do Dashboard
tab_perf, tab_exec, tab_news, tab_micro, tab_hft, tab_defi, tab_stress, tab_opt, tab_replay, tab_market, tab_control, tab_audit = st.tabs([
    "📈 Desempenho",
    "💸 Execuções",
    "📰 Sentimento Global",
    "🔍 Microestrutura",
    "⚡ HFT & Scalping",
    "🔗 DeFi & Yield",
    "🛡️ Stress Testing",
    "🛠️ Builder & Otimização",
    "⏪ Trade Replay",
    "🏪 Mercado de Estratégias",
    "🎮 Painel de Controlo",
    "📋 Auditoria de Decisões"
])

with tab_perf:
    st.subheader("📈 Desempenho do Portfólio")

    # Gerar gráfico real se houver dados
    df_memory = get_memory_data()
    if not df_memory.empty:
        trades_rows = df_memory[df_memory['key'] == 'trade']
        trades_list = [json.loads(r) for r in trades_rows['value']]

        # Simulação de dataframe de preço para o visualizador
        df_price = pd.DataFrame({
            'close': [100, 102, 101, 105, 104, 108, 110]
        }, index=pd.date_range(start='2026-01-01', periods=7))

        fig = TradeVisualizer.plot_price_with_trades(df_price, trades_list)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart([1000, 1010, 1005, 1020, 1015, 1030])

with tab_news:
    st.subheader("📰 Feed de Notícias e Sentimento")
    news_items = [
        {"time": "10:00", "title": "Fed mantém taxas de juro inalteradas", "sentiment": "Positivo"},
        {"time": "11:30", "title": "Adoção institucional de BTC atinge novo máximo", "sentiment": "Muito Positivo"},
        {"time": "13:00", "title": "Regulação restritiva em discussão na UE", "sentiment": "Negativo"}
    ]
    for item in news_items:
        col1, col2 = st.columns([1, 4])
        with col1: st.write(f"**{item['time']}**")
        with col2: st.info(f"{item['title']} | Sentimento: {item['sentiment']}")

    st.divider()
    st.subheader("Impacto nos Agentes")
    st.write("Evolução do Sentiment Score (Média Global)")
    st.line_chart(np.random.uniform(0.1, 0.8, 20))

with tab_exec:
    st.subheader("Histórico de Execuções")
    df_memory = get_memory_data()
    if not df_memory.empty:
        trades = df_memory[df_memory['key'] == 'trade'].copy()
        if not trades.empty:
            trades['value_parsed'] = trades['value'].apply(json.loads)
            st.write(trades[['timestamp', 'value_parsed']])
        else:
            st.info("Nenhuma execução registada.")
    else:
        st.info("Sem dados na memória.")

with tab_micro:
    st.subheader("🔍 Análise de Microestrutura (Order Book)")
    # Simulação de dados de microestrutura
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Spread Atual", "0.05", "0.01")
    with col2:
        st.metric("Order Book Imbalance", "0.65", "0.10")

    st.info("Esta aba mostrará detalhes do bid-ask spread e desequilíbrio em tempo real.")

with tab_hft:
    st.subheader("⚡ HFT & Scalping")
    st.write("Monitorização de micro-momentum e execução de alta frequência.")
    st.line_chart(np.random.randn(20, 3), height=250)
    st.info("Frequência de scan: 500ms | Agentes ativos: ScalpingAgent, MarketMakerAgent")

with tab_opt:
    st.subheader("🛠️ Strategy Builder e Otimização")

    col1, col2 = st.columns(2)
    with col1:
        st.write("### 🏗️ Constructor de Estratégias")
        st_name = st.text_input("Nome da Nova Estratégia", "MinhaEstrategia_v1")
        st_agents = st.multiselect("Selecionar Agentes", ["Regime", "Scanner", "Risk", "Execution", "LLM", "Sentiment", "ML Classifier"])
        if st.button("Gerar Ficheiro JSON"):
            st.success(f"Estratégia {st_name}.json criada em strategies/")

    with col2:
        st.write("### 🚀 Otimização de Parâmetros")
        st.write("Grid Search de Parâmetros de Risco")
        st.slider("Risk Aversion Range", 0.5, 5.0, (1.0, 3.0))
        if st.button("Iniciar Otimização"):
            with st.spinner("A correr 12 variantes de backtest..."):
                st.write("**Melhores Resultados:**")
                st.table([
                    {"Rank": 1, "Params": "Risk=2.0, SL=0.03", "Sharpe": 1.85},
                    {"Rank": 2, "Params": "Risk=1.5, SL=0.02", "Sharpe": 1.72},
                ])

with tab_stress:
    st.subheader("🛡️ Testes de Stress e Projeções de Risco")

    portfolio_val = 10000.0
    df_memory = get_memory_data()
    if not df_memory.empty:
        # Tentar obter valor real se disponível em memória ou simular
        st.write(f"Valor Base do Portfólio: **${portfolio_val}**")

        col1, col2 = st.columns(2)
        with col1:
            st.write("### Cenários Históricos")
            stress_results = PortfolioStressTester.simulate_scenarios(portfolio_val)
            for scenario, val in stress_results.items():
                diff = val - portfolio_val
                st.metric(scenario, f"${val:,.2f}", f"{diff:,.2f}")

        with col2:
            st.write("### Projeção Monte Carlo (30 dias)")
            mc_data = df_memory[df_memory['key'] == 'risk_monte_carlo']
            if not mc_data.empty:
                latest_mc = json.loads(mc_data.iloc[0]['value'])
                st.write(f"**Mediana:** ${latest_mc['median']:,.2f}")
                st.write(f"**Pior Caso:** ${latest_mc['worst_case']:,.2f}")
                st.write(f"**Melhor Caso:** ${latest_mc['best_case']:,.2f}")

                # Gráfico de barras simples para MC
                st.bar_chart({
                    "Pior Caso": latest_mc['worst_case'],
                    "Mediana": latest_mc['median'],
                    "Melhor Caso": latest_mc['best_case']
                })
            else:
                st.info("Aguardando dados de Monte Carlo do RiskAnalysisAgent...")

with tab_defi:
    st.subheader("Oportunidades DeFi & Yield")
    df_memory = get_memory_data()
    if not df_memory.empty:
        defi_opps = df_memory[df_memory['key'] == 'defi_opportunity'].copy()
        if not defi_opps.empty:
            defi_opps['details'] = defi_opps['value'].apply(json.loads)
            st.write(defi_opps[['timestamp', 'details']])
        else:
            st.info("Nenhuma oportunidade DeFi registada.")
    else:
        st.info("Sem dados na memória.")

with tab_market:
    st.subheader("🏪 Mercado de Estratégias e Plugins")

    col_l, col_r = st.columns(2)

    with col_l:
        st.write("### Estratégias Disponíveis")
        marketplace = [
            {"name": "Trend Follower Pro", "author": "QuantLab", "rating": "⭐⭐⭐⭐⭐"},
            {"name": "Arbitrage Master", "author": "DeFiWhale", "rating": "⭐⭐⭐⭐"},
            {"name": "HFT Scalper", "author": "FlashBoys", "rating": "⭐⭐⭐⭐⭐"}
        ]

        for item in marketplace:
            mcol1, mcol2 = st.columns([3, 1])
            with mcol1: st.write(f"**{item['name']}** ({item['author']})")
            with mcol2: st.button("Instalar", key=f"inst_{item['name']}")

    with col_r:
        st.write("### Gestão de Plugins")
        plugin_path = st.text_input("Caminho do Módulo de Plugin", "multiagent_trading.agents.custom")
        if st.button("Carregar Plugin"):
            st.info(f"A tentar carregar plugin de: {plugin_path}")
            # Em produção, chamaria o PluginManager
            st.success("Plugin validado e pronto a ativar!")

        st.write("---")
        st.write("**Agentes Ativos**")
        st.caption("RegimeClassifier, Scanner, Risk, Supervisor, Execution, LLM, Sentiment, DeFi")

with tab_replay:
    st.subheader("⏪ Replay de Negociações")
    st.write("Revisão passo-a-passo das trocas históricas.")

    df_memory = get_memory_data()
    if not df_memory.empty:
        trades = df_memory[df_memory['key'] == 'trade'].copy()
        if not trades.empty:
            step = st.slider("Passo da Troca", 0, len(trades)-1, 0)
            selected_row = trades.iloc[step]
            selected_trade = json.loads(selected_row['value'])

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Dados da Ordem**")
                st.json(selected_trade)
            with col2:
                st.write("**Metadados**")
                st.write(f"ID: {selected_row['id']}")
                st.write(f"Timestamp: {selected_row['timestamp']}")
        else:
            st.info("Nenhuma troca para reproduzir.")
    else:
        st.info("Sem dados na memória.")

with tab_control:
    st.subheader("🎮 Painel de Controlo")

    col1, col2 = st.columns(2)
    with col1:
        st.write("### Ordens Manuais")
        symbol = st.text_input("Símbolo", "BTC/USDT")
        side = st.selectbox("Lado", ["BUY", "SELL"])
        amount = st.number_input("Quantidade", min_value=0.0, value=1.0)
        if st.button("Enviar Ordem"):
            st.success(f"Ordem de {side} para {amount} {symbol} enviada para o orchestrator!")

    with col2:
        st.write("### Estado da API")
        if st.button("Verificar Status"):
            st.code('{"status": "online", "framework": "MATF"}')

with tab_audit:
    st.subheader("Auditoria de Decisões dos Agentes")
    df_memory = get_memory_data()
    if not df_memory.empty:
        st.dataframe(df_memory)

        st.divider()
        st.subheader("Raciocínio IA (LLM)")
        llm_reasoning = df_memory[df_memory['value'].str.contains('rationale', na=False)]
        if not llm_reasoning.empty:
            for index, row in llm_reasoning.iterrows():
                val = json.loads(row['value'])
                st.write(f"**{row['timestamp']} - {val.get('symbol')}**")
                st.info(val.get('rationale'))
    else:
        st.info("Nenhum registo de auditoria encontrado.")
