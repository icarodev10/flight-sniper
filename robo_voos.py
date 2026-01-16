"""
ROBÔ BACKEND V2.0 - Monitoramento de Voos com Inteligência de Dados
------------------------------------------------------------------
Este módulo é responsável por:
1. Automatizar a busca no Google Flights usando Undetected Chromedriver.
2. Extrair dados complexos (Preço, Cia, Horário) via Regex.
3. Calcular média histórica de preços para identificar promoções reais.
4. Persistir dados em SQLite e notificar via E-mail.
"""

import os
import re
import sqlite3
import smtplib
from typing import Optional, Any
from datetime import datetime, timedelta
from time import sleep
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Bibliotecas de Automação Web
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Configurações de Credenciais
EMAIL_REMETENTE = os.getenv("EMAIL_CONTA")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")
EMAIL_DESTINATARIO = os.getenv("EMAIL_CONTA")

# ==============================================================================
# FUNÇÃO: ENVIO DE NOTIFICAÇÕES
# ==============================================================================
def enviar_alerta_email(origem: str, destino: str, data_voo: str, valor: float, status: str, link: str) -> None:
    """
    Configura e envia um e-mail HTML formatado com os detalhes da oferta encontrada.
    Utiliza o servidor SMTP do Gmail (porta 587).
    """
    if not EMAIL_REMETENTE or not EMAIL_SENHA:
        print("   ⚠️ Credenciais de e-mail não configuradas no arquivo .env")
        return

    try:
        # Montagem do E-mail (MIME)
        msg = MIMEMultipart()
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = EMAIL_DESTINATARIO
        msg['Subject'] = f"✈️ ALERTA: {origem}->{destino} por R$ {valor:.2f}"

        # Corpo do E-mail em HTML
        corpo_html = f"""
        <html>
            <body>
                <h2 style="color: #2E86C1;">✈️ Flight Sniper Encontrou uma Oferta!</h2>
                <p><strong>Rota:</strong> {origem} ➡️ {destino}</p>
                <p><strong>Data:</strong> {data_voo}</p>
                <p><strong>Status:</strong> <span style="background-color: yellow;">{status}</span></p>
                <h1 style="color: green;">R$ {valor:.2f}</h1>
                <p><a href="{link}">🔗 CLIQUE AQUI PARA COMPRAR</a></p>
                <hr>
                <p><em>Enviado automaticamente pelo Flight Sniper Bot.</em></p>
            </body>
        </html>
        """
        msg.attach(MIMEText(corpo_html, 'html'))

        # Conexão e Envio via SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        text = msg.as_string()
        server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, text)
        server.quit()
        print("   📧 Notificação por e-mail enviada com sucesso!")
        
    except Exception as e:
        print(f"   ❌ Erro ao enviar e-mail: {e}")

# ==============================================================================
# FUNÇÃO: INTELIGÊNCIA DE DADOS (MÉDIA)
# ==============================================================================
def calcular_media_historica(origem: str, destino: str) -> float:
    """
    Consulta o banco de dados local para calcular a média aritmética
    de todos os preços coletados anteriormente para esta rota específica.
    """
    conexao = sqlite3.connect("meus_voos.db")
    cursor = conexao.cursor()
    
    # Verificação de segurança: checa se a tabela existe antes de consultar
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='precos'")
    if not cursor.fetchone():
        return 0.0
        
    cursor.execute('SELECT AVG(valor) FROM precos WHERE origem = ? AND destino = ?', (origem, destino))
    resultado = cursor.fetchone()[0]
    conexao.close()
    
    # Retorna 0.0 se não houver histórico, senão retorna a média
    return resultado if resultado else 0.0

# ==============================================================================
# FUNÇÃO PRINCIPAL (CORE)
# ==============================================================================
def buscar_precos(
    origem: str, 
    destino: str, 
    data_inicial: str, 
    dias_analise: int, 
    preco_maximo: float, 
    barra_progresso: Optional[Any] = None, 
    log_status: Optional[Any] = None
) -> None:
    """
    Executa o fluxo principal de RPA:
    1. Abre o navegador (Undetected Chrome).
    2. Varre as datas solicitadas.
    3. Extrai dados via Regex.
    4. Salva no SQLite e dispara alertas se necessário.
    
    Args:
        barra_progresso: Objeto Streamlit para feedback visual de progresso.
        log_status: Objeto Streamlit (st.empty) para logs em tempo real na interface.
    """
    dias_analise = int(dias_analise)
    preco_maximo = float(preco_maximo)

    print(f"\n🚀 Iniciando Varredura: {origem} -> {destino}")
    
    # Configuração do WebDriver (Modo Anti-Bloqueio)
    options = uc.ChromeOptions()
    options.add_argument("--log-level=3") # Suprime logs técnicos do Chrome
    # options.add_argument("--headless")  # Descomente para rodar sem interface gráfica
    
    navegador = uc.Chrome(options=options)
    navegador.set_window_size(1200, 800) # Resolução HD para garantir carregamento dos cards

    # --- Inicialização do Banco de Dados ---
    conexao = sqlite3.connect("meus_voos.db")
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_voo TEXT,
            origem TEXT,
            destino TEXT,
            valor REAL,
            companhia TEXT,
            horario TEXT,
            link TEXT,
            status TEXT,
            data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conexao.commit()

    data_obj = datetime.strptime(data_inicial, "%Y-%m-%d")

    try:
        # 1. Obtenção da Inteligência (Média Histórica)
        media_rota = calcular_media_historica(origem, destino)
        print(f"📊 Média Histórica da Rota: R$ {media_rota:.2f}")

        # 2. Loop de Varredura (Data por Data)
        for i in range(dias_analise):

            # Atualização da Interface (Streamlit)
            if barra_progresso:
                percentual = (i + 1) / dias_analise
                barra_progresso.progress(percentual, text=f"🔍 Analisando dia {i+1}/{dias_analise}...")

            # Cálculo da Data Atual
            data_atual = data_obj + timedelta(days=i)
            data_url = data_atual.strftime("%Y-%m-%d")    # Formato URL (YYYY-MM-DD)
            data_formatada_br = data_atual.strftime("%d/%m/%Y") # Formato Visual (DD/MM/YYYY)

            # Logs de Interface
            if log_status:
                log_status.info(f"🔎 Varrendo Google Flights para o dia {data_formatada_br}...")
            
            print(f"\n📅 [Analisando] {data_formatada_br}...")
            
            # Navegação
            url = f"https://www.google.com/travel/flights?q=Flights%20to%20{destino}%20from%20{origem}%20on%20{data_url}"
            navegador.get(url)
            sleep(6) # Espera explícita para carregamento do DOM (Scripts do Google)

            if log_status:
                log_status.warning(f"⏳ Processando HTML da página... (Dia {i+1}/{dias_analise})")
            
            # 3. Extração de Dados (Scraping)
            # Busca todos os elementos <li> dentro do container principal de resultados
            cards_voo = navegador.find_elements(By.XPATH, "//div[@role='main']//li")
            
            menor_preco_do_dia = float('inf')
            melhor_voo_info = {}

            print(f"   🔎 Analisando {len(cards_voo)} cartões de voo encontrados...")

            for card in cards_voo:
                texto_completo = card.text # Captura todo o texto visível do cartão
                
                if "R$" in texto_completo:
                    try:
                        # A. Extração de Preço via Regex
                        # Procura por "R$" seguido de números, ignorando espaços e pontos
                        match_preco = re.search(r"R\$\s*([\d\.]+)", texto_completo)
                        
                        if match_preco:
                            valor_str = match_preco.group(1).replace(".", "")
                            valor_atual = float(valor_str)
                            
                            # Verifica se é o menor preço encontrado hoje
                            if valor_atual < menor_preco_do_dia:
                                menor_preco_do_dia = valor_atual
                                
                                # B. Identificação da Companhia Aérea (Palavras-chave)
                                companhia = "Outra"
                                if "GOL" in texto_completo.upper(): companhia = "GOL"
                                elif "LATAM" in texto_completo.upper(): companhia = "LATAM"
                                elif "AZUL" in texto_completo.upper(): companhia = "AZUL"
                                elif "VOEPASS" in texto_completo.upper(): companhia = "VOEPASS"
                                
                                # C. Extração de Horário via Regex
                                # Busca o padrão HH:MM (ex: 14:30)
                                match_hora = re.search(r"(\d{2}:\d{2})", texto_completo)
                                if match_hora:
                                    horario = match_hora.group(1)
                                else:
                                    horario = "00:00"

                                # Armazena o "Voo Campeão" temporariamente
                                melhor_voo_info = {
                                    "valor": valor_atual,
                                    "companhia": companhia,
                                    "horario": horario,
                                    "link": url
                                }
                    except Exception:
                        pass # Ignora cartões que falharam na leitura (anúncios, etc)

            # 4. Tomada de Decisão e Persistência
            if menor_preco_do_dia != float('inf') and melhor_voo_info:
                
                status = "Normal"
                valor_final = melhor_voo_info['valor']
                
                # Regras de Negócio
                if valor_final <= preco_maximo: status = "✅ META ATINGIDA"
                if media_rota > 0 and valor_final < (media_rota * 0.8): status = "🔥 SUPER PROMOÇÃO"
                if valor_final > preco_maximo and valor_final > media_rota: status = "❌ Caro"

                print(f"   🏆 Melhor Voo: {melhor_voo_info['companhia']} às {melhor_voo_info['horario']} | R$ {valor_final:.2f} ({status})")

                # Disparo de Notificações
                if "META" in status or "PROMO" in status:
                    enviar_alerta_email(origem, destino, data_formatada_br, valor_final, status, melhor_voo_info['link'])

                # Insert no Banco de Dados
                cursor.execute('''
                    INSERT INTO precos (data_voo, origem, destino, valor, companhia, horario, status, link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data_formatada_br, origem, destino, valor_final, melhor_voo_info['companhia'], melhor_voo_info['horario'], status, melhor_voo_info['link']))
                conexao.commit()
            else:
                if log_status:
                    log_status.error(f"⚠️ Nenhum voo legível encontrado para {data_formatada_br}.")
                print("   ⚠️ Não consegui extrair preços válidos para esta data.")

    except Exception as e:
        print(f"❌ Erro Crítico na execução: {e}")
    finally:
        conexao.close()
        navegador.quit()

if __name__ == "__main__":
    # Teste local direto
    buscar_precos("CGH", "SDU", "2026-02-19", 3, 600.00)