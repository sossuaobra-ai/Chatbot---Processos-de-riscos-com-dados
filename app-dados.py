import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from openai import AzureOpenAI

# 1. Configuração da página e tema visual estilo WhatsApp Web
st.set_page_config(
    page_title="RiskAnalytics AI — Chat & Azure RAG",
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
        font-family: sans-serif;
    }
    .chat-bubble-assistant {
        background-color: #202c33;
        color: #e9edef;
        padding: 10px 14px;
        border-radius: 8px 8px 8px 0px;
        margin: 8px auto 8px 0px;
        max-width: 85%;
        box-shadow: 0 1px 0.5px rgba(11,20,26,.13);
        font-family: sans-serif;
    }
    .chat-time {
        font-size: 0.7em;
        color: #8696a0;
        text-align: right;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Barra Lateral: Configurações do Azure e Upload de Arquivos
with st.sidebar:
    st.header("⚙️ Configurações Azure AI")
    
    api_key = st.text_input("Azure OpenAI API Key", type="password")
    azure_endpoint = st.text_input("Azure Endpoint", placeholder="https://seu-recurso.openai.azure.com/")
    model_deployment = st.text_input("Nome do Deployment / Modelo", value="gpt-4o")
    api_version = st.text_input("API Version", value="2024-02-01")
    
    st.markdown("---")
    st.header("📂 Base de Conhecimento (RAG)")
    uploaded_files = st.file_uploader(
        "Envie documentos de RAG (PDF, TXT, CSV, XLSX)", 
        type=["pdf", "txt", "csv", "xlsx"], 
        accept_multiple_files=True
    )
    
    system_persona = st.text_area(
        "Persona da IA / Instruções de Sistema", 
        value="Você é um assistente especialista sênior em gestão de riscos e auditoria de processos de atendimento. Responda com base nos documentos carregados e análise de dados."
    )
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        start_chat = st.button("🚀 Iniciar Chat")
    with col2:
        clear_chat = st.button("🧹 Limpar Conversa")

if clear_chat:
    st.session_state.messages = []
    st.rerun()

# 3. Inicialização do Histórico no Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Insira suas credenciais da Azure na barra lateral, envie seus arquivos de contexto e clique em **Iniciar Chat** para começarmos a interagir."}
    ]

# Extração de texto dos arquivos enviados (RAG)
rag_context = ""
df_data = None

if uploaded_files:
    for file in uploaded_files:
        if file.name.endswith(".csv"):
            df_data = pd.read_csv(file)
            rag_context += f"\n--- Conteúdo do CSV ({file.name}) ---\n" + df_data.to_string()
        elif file.name.endswith(".xlsx"):
            df_data = pd.read_excel(file)
            rag_context += f"\n--- Conteúdo do Excel ({file.name}) ---\n" + df_data.to_string()
        elif file.name.endswith(".txt"):
            text_content = file.read().decode("utf-8")
            rag_context += f"\n--- Conteúdo do TXT ({file.name}) ---\n" + text_content
        elif file.name.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(file)
                pdf_text = "".join([page.extract_text() for page in reader.pages])
                rag_context += f"\n--- Conteúdo do PDF ({file.name}) ---\n" + pdf_text
            except Exception as e:
                st.sidebar.error(f"Erro ao ler PDF: {e}")

# Header Principal
st.title("💬 RiskAnalytics AI — WhatsApp Style & Azure RAG")
st.caption("Aplicativo integrado com OpenAI (Azure) para análise interativa de processos de risco.")

# Renderização do Histórico Estilo WhatsApp
for msg in st.session_state.messages:
    now = datetime.now().strftime("%H:%M")
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}<div class="chat-time">{now} ✓✓</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-assistant">**Atente-se a resposta abaixo:**<br>{msg["content"]}<div class="chat-time">{now}</div></div>', unsafe_allow_html=True)
        if "chart" in msg and msg["chart"] is not None:
            st.plotly_chart(msg["chart"], use_container_width=True)

# Entrada do Chat
prompt = st.chat_input("Digite sua pergunta sobre os riscos, custos ou solicite gráficos...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Processamento da Resposta do Assistente
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"].lower()
    
    # Verificação se o usuário pediu gráficos e temos dados estruturados (pandas)
    chart1, chart2, chart3 = None, None, None
    if any(w in user_query for w in ["grafico", "gráficos", "dashboard", "analise", "análise"]) and df_data is not None:
        try:
            col_etapa = [c for c in df_data.columns if "Etapa" in c or "etapa" in c][0]
            col_vol = [c for c in df_data.columns if "Volume" in c or "Ocorrências" in c or "Ocorrencias" in c][0]
            df_etapa = df_data.groupby(col_etapa)[col_vol].sum().reset_index()
            chart1 = px.bar(df_etapa, x=col_etapa, y=col_vol, title="1. Volume de Erros por Etapa", template="plotly_dark", color=col_etapa)
            
            col_id = [c for c in df_data.columns if "ID" in c or "Risco" in c][0]
            col_custo = [c for c in df_data.columns if "Custo" in c or "Valor" in c][0]
            chart2 = px.bar(df_data, x=col_custo, y=col_id, orientation='h', title="2. Impacto Financeiro (R$) por Risco", template="plotly_dark", color=col_custo, color_continuous_scale="Reds")
            
            col_status = [c for c in df_data.columns if "Status" in c or "status" in c][0]
            df_status = df_data.groupby(col_status).size().reset_index(name='Qtd')
            chart3 = px.pie(df_status, names=col_status, values='Qtd', hole=0.4, title="3. Status de Mitigação", template="plotly_dark")
        except Exception:
            pass

    # Chamada real ao Azure OpenAI se credenciais fornecidas
    ai_response = ""
    if api_key and azure_endpoint:
        try:
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint
            )
            
            messages_payload = [
                {"role": "system", "content": f"{system_persona}\n\nContexto dos Documentos:\n{rag_context}"}
            ]
            for m in st.session_state.messages:
                if m["role"] in ["user", "assistant"]:
                    messages_payload.append({"role": m["role"], "content": m["content"]})
                    
            response = client.chat.completions.create(
                model=model_deployment,
                messages=messages_payload,
                temperature=0.2,
                stream=False
            )
            ai_response = response.choices[0].message.content
        except Exception as e:
            ai_response = f"Erro ao comunicar com a API da Azure OpenAI: {e}"
    else:
        ai_response = "Por favor, insira as credenciais da Azure OpenAI na barra lateral para receber respostas geradas pela IA. Abaixo estão os dados preliminares da sua solicitação."

    # Adiciona resposta ao histórico
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    if chart1:
        st.session_state.messages.append({"role": "assistant", "content": "📊 **Visão Operacional:**", "chart": chart1})
    if chart2:
        st.session_state.messages.append({"role": "assistant", "content": "💰 **Visão Financeira:**", "chart": chart2})
    if chart3:
        st.session_state.messages.append({"role": "assistant", "content": "🎯 **Visão de Governança:**", "chart": chart3})
    st.rerun()
