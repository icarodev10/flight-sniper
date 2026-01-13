"""
PROJETO: RPA - Monitoramento Inteligente de Passagens Aéreas
AUTOR: Icaro de Souza de Lima
DATA: 2026

DESCRIÇÃO:
Este robô automatiza a busca por preços de passagens no Google Flights.
Ele varre múltiplas datas, compara preços com um valor alvo,
gera um relatório em CSV e notifica o usuário
via sistema operacional caso encontre uma oportunidade.
"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime, timedelta
import csv      

# OBSERVAÇÃO SOBRE CÓDIGOS IATA:
# O sistema utiliza o padrão internacional de siglas de aeroportos (IATA).
# Exemplos:
# - VCP: Viracopos (Campinas/SP)
# - GRU: Guarulhos (São Paulo/SP)
# - CGH: Congonhas (São Paulo/SP)
# - SDU: Santos Dumont (Rio de Janeiro/RJ)
# - CNF: Confins (Belo Horizonte/MG)
# - GIG: Galeão (Rio de Janeiro/RJ)
# - JFK: John F. Kennedy (Nova York/EUA)


# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def buscar_precos(origem, destino, data_inicial, dias_analise, preco_maximo):
    print(f"\n🚀 Iniciando Varredura: {origem} -> {destino}")
    print(f"📊 Meta de Preço: R$ {preco_maximo}")

    dias_analise = int(dias_analise)
    preco_maximo = float(preco_maximo)
    
    # 1. Preparação do Arquivo de Relatório (CSV)
    # Mode 'w' cria um arquivo novo toda vez. Use 'a' se quiser adicionar ao histórico.
    arquivo = open("relatorio_passagens.csv", mode="w", newline="", encoding="utf-8")
    escritor = csv.writer(arquivo, delimiter=";") 
    
    # Cabeçalho das colunas do CSV
    escritor.writerow(["Data do Voo", "Origem", "Destino", "Preço Encontrado (R$)", "Status"])
    
    # 2. Configuração do Driver do Navegador (Selenium)
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3") # Suprime avisos desnecessários do console
    # options.add_argument("--headless")  # Descomente para rodar sem abrir a janela do navegador
    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico, options=options)

    # --- CONFIGURAÇÃO DA JANELA ---
    # Define o tamanho (Largura, Altura)
    navegador.set_window_size(800, 600) 
    
    # Define a posição na tela (X, Y)
    navegador.set_window_position(50, 50)

    # Conversão da string de data para objeto datetime
    data_obj = datetime.strptime(data_inicial, "%Y-%m-%d")

    try:
        # Loop para iterar nos dias em sequencia
        for i in range(dias_analise):
            # Lógica de Data: Soma 'i' dias à data inicial
            data_atual = data_obj + timedelta(days=i)
            data_url = data_atual.strftime("%Y-%m-%d")    # Formato para a URL do Google
            data_display = data_atual.strftime("%d/%m/%Y") # Formato Brasileiro para o Relatório
            
            print(f"\n📅 [PROCESSANDO] Verificando data: {data_display}...")
            
            # Montagem da URL
            url = f"https://www.google.com/travel/flights?q=Flights%20to%20{destino}%20from%20{origem}%20on%20{data_url}"
            navegador.get(url)
            
            # Delay para garantir o carregamento do DOM 
            sleep(4) 
            
            # 3. Extração de Dados (Web Scraping)
            # Busca todos os elementos visíveis que contenham o símbolo "R$"
            elementos = navegador.find_elements(By.XPATH, "//*[contains(text(), 'R$')]")
            
            menor_preco_do_dia = float('inf') # Inicializa com infinito para comparação

            # Itera sobre todos os preços encontrados na página para achar o menor
            for el in elementos:
                txt = el.text.strip()
                # Verifica se é um preço válido e não um texto muito longo
                if "R$" in txt and len(txt) < 15:
                    # Limpeza de Dados:
                    # Transforma "R$ 1.200,00" em "1200.00" (Float)
                    valor_limpo = txt.replace("R$", "").replace(".", "").replace(" ", "")
                    try:
                        val = float(valor_limpo)
                        if val < menor_preco_do_dia:
                            menor_preco_do_dia = val
                    except:
                        pass # Ignora elementos que não sejam números que podem ser convertidos
            
            # 4. Tomada de Decisão e Alerta
            if menor_preco_do_dia != float('inf'):
                print(f"   ✅ Preço encontrado: R$ {menor_preco_do_dia}")
                
                # O preço está abaixo da meta?
                if menor_preco_do_dia <= preco_maximo:
                    status = "COMPRAR AGORA"
                    
                else:
                    status = "Acima da Meta"
                
                # Gravação no CSV
                escritor.writerow([data_display, origem, destino, menor_preco_do_dia, status])
            else:
                print("   ⚠️ Nenhum preço detectado nesta data.")
                escritor.writerow([data_display, origem, destino, "N/A", "Erro na Leitura"])

        print("\n🏁 [FIM] Relatório 'relatorio_passagens.csv' gerado com sucesso!")

    except Exception as e:
        print(f"❌ [ERRO CRÍTICO] Ocorreu uma falha na execução: {e}")
    finally:
        # Fecha conexões e arquivos
        arquivo.close()
        navegador.quit()

# Ponto de entrada do script
if __name__ == "__main__":
    buscar_precos("VCP", "CNF", "2026-05-20", 3, 1500.00)