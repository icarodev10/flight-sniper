import streamlit as st
import pandas as pd
import robo_voos 
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Monitor de Voos ✈️",
    page_icon="✈️",
    layout="wide"
)

# --- TÍTULO E CABEÇALHO ---
st.title("✈️ Dashboard de Monitoramento de Passagens")
st.markdown("Este painel monitora preços de voos automaticamente utilizando **Python + Selenium**.")

# --- BARRA LATERAL (ENTRADA DE DADOS) ---
with st.sidebar:
    st.header("⚙️ Configuração da Viagem")
    
    # Campos de Texto
    origem = st.text_input("Origem (Código IATA)", "VCP").upper() 
    destino = st.text_input("Destino (Código IATA)", "CNF").upper()
    
    # Campo de Data 
    data_selecionada = st.date_input("Data de Ida", date(2026, 5, 20))
    
    # Campo de Números 
    dias_analise = st.slider("Quantos dias analisar pra frente?", 1, 7, 3)
    preco_alvo = st.number_input("Preço Máximo (R$)", value=1500.00, step=50.0)
    
    st.divider()
    
    # BOTÃO DE AÇÃO
    botao = st.button("🚀 INICIAR BUSCA AUTOMÁTICA")

# --- LÓGICA DO BOTÃO ---
if botao:
    with st.spinner(f'O Robô está varrendo passagens de {origem} para {destino}...'):
        # Formata a data pro robô
        data_formatada = data_selecionada.strftime("%Y-%m-%d")
        # Chama a função do outro arquivo
        robo_voos.buscar_precos(origem, destino, data_formatada, dias_analise, preco_alvo)
        
    st.success("Busca finalizada! Veja os resultados abaixo.")
    st.rerun() # Atualiza a página 

# --- CARREGAR DADOS ---
try:
    st.subheader("📊 Resultados da Última Busca")
    
    # Lê o arquivo CSV
    df = pd.read_csv("relatorio_passagens.csv", sep=";")
    
    # Limpeza rápida dos dados 
    df = df[df["Preço Encontrado (R$)"] != "N/A"] # Tira erros
    df["Preço Encontrado (R$)"] = df["Preço Encontrado (R$)"].astype(float) # Garante que é número

    # --- MÉTRICAS (KPIs) ---
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        
        menor_preco = df["Preço Encontrado (R$)"].min()
        media_preco = df["Preço Encontrado (R$)"].mean()
        qtd_voos = len(df)

        col1.metric("Menor Preço Encontrado", f"R$ {menor_preco:.2f}")
        col2.metric("Média de Preços", f"R$ {media_preco:.2f}")
        col3.metric("Dias Analisados", qtd_voos)

        # --- TABELA E GRÁFICO ---
        st.write("---") # Linha divisória
        
        # Filtro visual: Mostra todos, mas pinta de verde/vermelho baseado na meta
        def colorir_precos(val):
            color = 'green' if val <= preco_alvo else 'red'
            return f'color: {color}'

        st.subheader("Lista de Voos Encontrados")
        # Aplica a cor na coluna de preço
        st.dataframe(
            df.style
            .format({"Preço Encontrado (R$)": "R$ {:.2f}"}) 
            .map(colorir_precos, subset=['Preço Encontrado (R$)']),
            use_container_width=True
        )

        # Gráfico de barras (Data x Preço)
        st.subheader("Variação de Preço por Data")
        st.bar_chart(df, x="Data do Voo", y="Preço Encontrado (R$)")
        
    else:
        st.warning("O robô rodou, mas não encontrou dados válidos. Tente outra data.")

except FileNotFoundError:
    st.info("👈 Configure sua viagem na barra lateral e clique em INICIAR para gerar o primeiro relatório.")