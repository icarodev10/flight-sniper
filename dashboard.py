"""
DASHBOARD FRONTEND V2.0 - Flight Sniper Pro
-------------------------------------------
Interface gráfica desenvolvida em Streamlit responsável por:
1. Coletar inputs do usuário (Rota, Datas, Preço Alvo).
2. Orquestrar a execução do robô de backend (robo_voos.py).
3. Exibir KPIs, Gráficos de Tendência e Tabelas Detalhadas.
4. Gerenciar o Banco de Dados (Limpeza e Reset).
"""

import time
import sqlite3
import pandas as pd
import streamlit as st
from datetime import date
import robo_voos  # Módulo de Backend

# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(
    page_title="Flight Sniper Pro ✈️",
    page_icon="✈️",
    layout="wide"
)

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    /* Ajuste de espaçamento do container principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Estilização dos Cards de Métricas (KPIs) com efeito de sombra/hover */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Estilização do Botão Primário */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✈️ Flight Sniper Command Center")

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================
def carregar_dados() -> pd.DataFrame:
    """
    Conecta ao banco SQLite e retorna os dados da tabela 'precos'.
    Trata erros caso a tabela ainda não exista (primeira execução).
    """
    conn = sqlite3.connect("meus_voos.db")
    try:
        df = pd.read_sql_query("SELECT * FROM precos", conn)
    except Exception:
        # Retorna DataFrame vazio estruturado para evitar quebra de UI
        df = pd.DataFrame(columns=[
            'id', 'data_voo', 'origem', 'destino', 'valor', 
            'companhia', 'horario', 'status', 'data_coleta', 'link'
        ])
    finally:
        conn.close()
    return df

def highlight_status(val: str) -> str:
    """
    Define a cor de fundo da célula na tabela baseado no status do voo.
    """
    color = 'transparent'
    val_str = str(val)
    if 'META' in val_str:
        color = '#d4edda' # Verde 
    elif 'PROMO' in val_str:
        color = '#cce5ff' # Azul 
    elif 'Caro' in val_str:
        color = '#f8d7da' # Vermelho 
    return f'background-color: {color}'

# ==============================================================================
# BARRA LATERAL (CONTROLES)
# ==============================================================================
with st.sidebar:
    st.header("📍 Configuração da Rota")
    origem = st.text_input("Origem (IATA)", "CGH", max_chars=3).upper() 
    destino = st.text_input("Destino (IATA)", "SDU", max_chars=3).upper()
    
    st.divider()
    
    st.header("🤖 Parâmetros do Robô")
    data_selecionada = st.date_input("Data Inicial", date(2026, 2, 19))
    dias_analise = st.slider("Janela de Análise (Dias)", 1, 3, 7)
    preco_alvo = st.number_input("Preço Alvo (R$)", value=600.00, step=50.0)
    
    st.divider()
    botao_busca = st.button("🚀 INICIAR VARREDURA", type="primary")

# ==============================================================================
# ÁREA PRINCIPAL (TABS)
# ==============================================================================
aba1, aba2, aba3 = st.tabs(["📊 Monitoramento", "📂 Dados Detalhados", "⚙️ Gestão"])

# --- ABA 1: DASHBOARD ANALÍTICO ---
with aba1:
    st.markdown(f"### Análise de Rota: **{origem} ➡️ {destino}**")
    
    df_geral = carregar_dados()
    
    # Filtro de Contexto (Mostra apenas dados da rota selecionada na sidebar)
    if not df_geral.empty:
        df_rota = df_geral[
            (df_geral['origem'] == origem) & 
            (df_geral['destino'] == destino)
        ].copy()
        
        if not df_rota.empty:
            # Ordenação: Mais recente primeiro
            df_rota = df_rota.sort_values(by='id', ascending=False)
            ultimo_registro = df_rota.iloc[0]

            # Cálculos de KPIs
            valor_atual = ultimo_registro['valor']
            media_valor = df_rota["valor"].mean()
            menor_valor = df_rota["valor"].min()
            delta = valor_atual - media_valor # Diferença para a média histórica

            # Grid de 4 Colunas para Métricas
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Último Preço", f"R$ {valor_atual:.2f}", f"{delta:.2f}", delta_color="inverse")
            col2.metric("Média Histórica", f"R$ {media_valor:.2f}")
            col3.metric("Melhor Registro", f"R$ {menor_valor:.2f}")
            col4.metric("Meta Definida", f"R$ {preco_alvo:.2f}")
            
            st.divider()
            
            st.subheader("📈 Tendência de Preços")
            st.line_chart(df_rota, x="data_coleta", y="valor")
            st.caption("Eixo X: Data/Hora da coleta do robô | Eixo Y: Valor da passagem")
            
        else:
            st.info(f"Nenhum histórico encontrado para {origem}-{destino}. Inicie o robô para coletar dados.")
    else:
        st.warning("Banco de dados vazio. Realize a primeira varredura.")

# --- LÓGICA DE EXECUÇÃO DO ROBÔ ---
if botao_busca:
    # Elementos de UI para Feedback em Tempo Real
    barra = st.progress(0, text="Inicializando drivers...")
    log_box = st.empty()
    
    try:
        data_formatada = data_selecionada.strftime("%Y-%m-%d")
        
        # Chama o Backend passando os elementos
        robo_voos.buscar_precos(
            origem=origem, 
            destino=destino, 
            data_inicial=data_formatada, 
            dias_analise=dias_analise, 
            preco_maximo=preco_alvo, 
            barra_progresso=barra,
            log_status=log_box
        )
        
        log_box.empty()
        st.success("✅ Processo finalizado! Atualizando dashboard...")
        time.sleep(1.5)
        st.rerun()
        
    except Exception as e:
        st.error(f"Falha na execução: {e}")

# --- ABA 2: TABELA DE DADOS ---
with aba2:
    st.markdown("### 🌎 Relatório Completo")
    df = carregar_dados()
    
    if not df.empty:
        # Configuração da Tabela Interativa
        st.dataframe(
            df[['data_voo', 'origem', 'destino', 'companhia', 'horario', 'valor', 'status', 'link']]
            .style
            .format({"valor": "R$ {:.2f}"})
            .map(highlight_status, subset=['status']),
            
            column_config={
                "link": st.column_config.LinkColumn(
                    "Ação",
                    display_text="🔗 Comprar"
                )
            },
            width="stretch",
            height=500
        )
    else:
        st.info("Aguardando dados...")

# --- ABA 3: ADMINISTRAÇÃO ---
with aba3:
    st.header("⚠️ Zona de Gerenciamento")
    st.write("Ferramentas para manutenção do banco de dados local.")
    
    col_del1, col_del2 = st.columns(2)
    
    with col_del1:
        if st.button(f"🗑️ Limpar histórico: {origem}->{destino}"):
            conn = sqlite3.connect("meus_voos.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM precos WHERE origem = ? AND destino = ?", (origem, destino))
            conn.commit()
            conn.close()
            st.warning(f"Dados da rota {origem}-{destino} removidos.")
            time.sleep(1)
            st.rerun()
            
    with col_del2:
        if st.button("💣 RESET TOTAL (Apagar Banco)"):
            conn = sqlite3.connect("meus_voos.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM precos")
            conn.commit()
            conn.close()
            st.error("Banco de dados completamente reiniciado.")
            time.sleep(1)
            st.rerun()