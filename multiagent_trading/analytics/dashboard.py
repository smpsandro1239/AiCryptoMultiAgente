import streamlit as st
import pandas as pd
import json
import sqlite3
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
st.sidebar.header("Estado do Sistema")
st.sidebar.success("Sistema Ativo")

# Tabs do Dashboard
tab_perf, tab_exec, tab_micro, tab_defi, tab_replay, tab_audit = st.tabs([
    "Desempenho",
    "Execuções",
    "Microestrutura",
    "DeFi & Yield",
    "Trade Replay",
    "Auditoria de Decisões"
])

with tab_perf:
    st.subheader("Evolução do Portfólio")
    # Placeholder para dados de performance
    st.line_chart([1000, 1010, 1005, 1020, 1015, 1030])

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
    st.subheader("Análise de Microestrutura (Order Book)")
    # Simulação de dados de microestrutura
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Spread Atual", "0.05", "0.01")
    with col2:
        st.metric("Order Book Imbalance", "0.65", "0.10")

    st.info("Esta aba mostrará detalhes do bid-ask spread e desequilíbrio em tempo real.")

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

with tab_replay:
    st.subheader("Trade Replay")
    st.write("Revisão passo-a-passo das trocas históricas.")

    df_memory = get_memory_data()
    if not df_memory.empty:
        trades = df_memory[df_memory['key'] == 'trade'].copy()
        if not trades.empty:
            step = st.slider("Passo da Troca", 0, len(trades)-1, 0)
            selected_trade = json.loads(trades.iloc[step]['value'])
            st.json(selected_trade)
            st.write(f"Timestamp: {trades.iloc[step]['timestamp']}")
        else:
            st.info("Nenhuma troca para reproduzir.")
    else:
        st.info("Sem dados na memória.")

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
