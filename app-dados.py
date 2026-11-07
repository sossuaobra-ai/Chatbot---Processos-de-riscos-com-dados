import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configuração da página e tema visual estilo WhatsApp Web
st.set_page_config(
    page_title="RiskAnalytics AI - Chat & Dashboard",
    page_icon="💬",
    layout="wide"
)

# Estilização CSS personalizada para o layout do WhatsApp
st.markdown("""
<style>
    .stApp {
        background-color: #0b141a;
        color: #e9edef;
    }
    [data-testid="stSidebar"] {
        background-color: #111b21;
        border-right: 1px solid #222d34;
    }
    .chat-bubble-user {
        background-color: #005c4b;
        color: #e9edef;
        padding: 10px 14px;
        border-radius: 8px 8px 0px 8px;
        margin: 8px 0px 8px auto;
        max-width: 75%;
        box-shadow: 0 1px 0.5px rgba(11,20,26,.13);
    }
    .chat-bubble-assistant {
        background-color: #202c33;
        color: #e9edef;
        padding: 10px 14px;
        border-radius: 8px 8px 8px 0px;
        margin: 8px auto 8px 0px;
        max-width: 85%;
        box-shadow: 0 1px 0.5px rgba(11,20,26,.13);
    }
    .chat-time {
        font-size: 0.7em;
        color: #8696a0;
        text-align: right;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Header e Barra Lateral
st.title("💬 RiskAnalytics — WhatsApp Risk Assistant")
st.caption("Faça o upload do seu arquivo de riscos (.xlsx ou .csv) e interaja no chat para gerar análises visuais.")

with st.sidebar:
    st.header("⚙️ Painel de Dados")
    uploaded_file = st.file_uploader("Envie sua Planilha (.xlsx ou .csv)", type=["xlsx", "csv"])
    
    st.markdown("---")
    if uploaded_file is not None:
        st.success("✅ Arquivo carregado com sucesso!")
    else:
        st.warning("⏳ Aguardando upload da planilha...")

# 3. Estado da Conversa no Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu assistente de gestão de riscos. Faça o upload da sua planilha para começarmos a gerar os gráficos!"}
    ]

# 4. Processamento da Planilha enviada
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".xlsx"):
            xls = pd.ExcelFile(uploaded_file)
            sheet = "Matriz de Riscos e Atendimento" if "Matriz de Riscos e Atendimento" in xls.sheet_names else xls.sheet_names[0]
            df = pd.read_excel(uploaded_file, sheet_name=sheet)
        else:
            df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        df = None
else:
    df = None

# 5. Renderização do Chat
for msg in st.session_state.messages:
    now = datetime.now().strftime("%H:%M")
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}<div class="chat-time">{now} ✓✓</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-assistant">{msg["content"]}<div class="chat-time">{now}</div></div>', unsafe_allow_html=True)
        if "chart" in msg and msg["chart"] is not None:
            st.plotly_chart(msg["chart"], use_container_width=True)

# 6. Entrada do Usuário e Interação por comandos de voz/texto
prompt = st.chat_input("Digite um comando (ex: 'mostrar gráficos', 'resumo de custos')...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"].lower()
    
    if df is None:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Por favor, faça primeiro o upload da sua planilha Excel ou CSV na barra lateral à esquerda!"
        })
    else:
        if any(w in user_query for w in ["grafico", "gráficos", "dashboard", "analise", "análise"]):
            # Identificação das colunas da planilha
            col_etapa = [c for c in df.columns if "Etapa" in c][0]
            col_vol = [c for c in df.columns if "Volume" in c or "Ocorrências" in c][0]
            col_id = [c for c in df.columns if "ID" in c or "Risco" in c][0]
            col_custo = [c for c in df.columns if "Custo" in c or "Valor" in c][0]
            col_status = [c for c in df.columns if "Status" in c][0]
            
            # Gráfico 1: Colunas (Operacional)
            df_etapa = df.groupby(col_etapa)[col_vol].sum().reset_index()
            fig1 = px.bar(df_etapa, x=col_etapa, y=col_vol, title="1. Volume de Erros por Etapa de Atendimento", template="plotly_dark", color=col_etapa)
            
            # Gráfico 2: Barras Horizontais (Financeiro)
            fig2 = px.bar(df, x=col_custo, y=col_id, orientation='h', title="2. Impacto Financeiro (R$) por Risco", template="plotly_dark", color=col_custo, color_continuous_scale="Reds")
            
            # Gráfico 3: Rosca/Pizza (Governança/Status)
            df_status = df.groupby(col_status).size().reset_index(name='Quantidade')
            fig3 = px.pie(df_status, names=col_status, values='Quantidade', hole=0.4, title="3. Status de Implementação das Mitigações", template="plotly_dark")
            
            # Adiciona gráficos nas bolhas de conversa do WhatsApp
            st.session_state.messages.append({"role": "assistant", "content": "Análise gerada com sucesso! Veja abaixo os 3 gráficos solicitados:"})
            st.session_state.messages.append({"role": "assistant", "content": "📊 **Visão Operacional (Volume por Etapa):**", "chart": fig1})
            st.session_state.messages.append({"role": "assistant", "content": "💰 **Visão Financeira (Custo por Risco):**", "chart": fig2})
            st.session_state.messages.append({"role": "assistant", "content": "🎯 **Visão de Governança (Status de Mitigação):**", "chart": fig3})
            
        elif any(w in user_query for w in ["custo", "financeiro", "valor"]):
            col_custo = [c for c in df.columns if "Custo" in c or "Valor" in c][0]
            total = df[col_custo].sum()
            st.session_state.messages.append({"role": "assistant", "content": f"O custo total de falhas mapeado é de **R$ {total:,.2f}**."})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Comando recebido! Experimente digitar **'mostrar gráficos'** para gerar o painel visual no chat."})
    st.rerun()
