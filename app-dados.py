import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configuração da página e layout wide
st.set_page_config(
    page_title="Painel Analítico de Manutenção e Serviços de TI",
    page_icon="📊",
    layout="wide"
)

# 2. Estilização CSS personalizada (Dashboard principal + Popup flutuante estilo WhatsApp)
st.markdown("""
<style>
    /* Estilos Gerais */
    .stApp {
        background-color: #f8f9fa;
        color: #1f2937;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* POPUP FLUTUANTE ESTILO WHATSAPP (Canto Inferior Direito) */
    .whatsapp-popup-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 360px;
        height: 520px;
        background-color: #0b141a;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        z-index: 999999;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #222d34;
        font-family: sans-serif;
    }
    
    .whatsapp-header {
        background-color: #202c33;
        color: #e9edef;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 1px solid #222d34;
    }
    
    .wa-bubble-user {
        background-color: #005c4b;
        color: #e9edef;
        padding: 8px 12px;
        border-radius: 8px 8px 0px 8px;
        align-self: flex-end;
        max-width: 80%;
        font-size: 0.85rem;
    }
    
    .wa-bubble-assistant {
        background-color: #202c33;
        color: #e9edef;
        padding: 8px 12px;
        border-radius: 8px 8px 8px 0px;
        align-self: flex-start;
        max-width: 85%;
        font-size: 0.85rem;
    }
    
    .wa-time {
        font-size: 0.65rem;
        color: #8696a0;
        text-align: right;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar de Configurações e Upload
with st.sidebar:
    st.markdown("### Deployment / Modelo:")
    model_deployment = st.text_input("Modelo", value="gpt-4.1-mini", label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### Persona da IA:")
    system_persona = st.text_area(
        "Persona", 
        value="forma ágil, clara e cordial. Consulte sempre a base anexada para orçamentos, procedimentos e SLAs.",
        label_visibility="collapsed",
        height=100
    )
    
    st.markdown("---")
    st.markdown("### Upload da Base (CSV para Dashboard + Chat):")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv", "xlsx"], label_visibility="collapsed")
    
    st.markdown("---")
    if uploaded_file is not None:
        st.success(f"Carregado: {uploaded_file.name}")
    else:
        st.info("Carregue uma base de dados (ex: tabela_custos_ti.csv)")
        
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        btn_connect = st.button("🔌 Conectar IA", type="primary")
    with col_b2:
        btn_new = st.button("💬 Novo Chat")

if btn_new:
    st.session_state.wa_messages = [
        {"role": "assistant", "content": "Olá! Como posso ajudar você hoje com o suporte de TI?", "time": "04:44"}
    ]
    st.rerun()

if "wa_messages" not in st.session_state:
    st.session_state.wa_messages = [
        {"role": "assistant", "content": "Olá! Como posso ajudar você hoje com o suporte de TI?", "time": "04:44"}
    ]

# Carregamento do DataFrame padrão ou enviado
df = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
else:
    # Dados de exemplo simulando a imagem de referência
    data_exemplo = {
        "ID_Servico": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "Categoria": ["Hardware", "Hardware", "Software", "Hardware", "Software", "Software", "Hardware", "Software", "Hardware", "Software", "Hardware", "Software"],
        "Valor_Total_Sugerido_BRL": [250, 380, 120, 390, 580, 110, 140, 120, 130, 110, 130, 90],
        "SLA_Horas": [4.5, 6.0, 3.0, 5.5, 8.0, 4.0, 5.0, 6.5, 7.0, 5.0, 4.5, 5.0]
    }
    df = pd.DataFrame(data_exemplo)

# 4. Dashboard Principal Inspirado na Imagem
st.markdown("## 📊 Painel Analítico de Manutenção e Serviços de TI")

# Métricas Topo
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total de Serviços", f"{len(df)} itens")
with col_m2:
    val_medio = df["Valor_Total_Sugerido_BRL"].mean() if "Valor_Total_Sugerido_BRL" in df.columns else 207.08
    st.metric("Ticket Médio", f"R$ {val_medio:,.2f}")
with col_m3:
    sla_medio = df["SLA_Horas"].mean() if "SLA_Horas" in df.columns else 5.9
    st.metric("SLA Médio", f"{sla_medio:.1f} h")

st.markdown("---")

# Gráficos Principais (Barras e Pizza)
col_g1, col_g2 = st.columns([1.3, 1])

with col_g1:
    st.markdown("##### Custo Total por Código de Serviço (R$)")
    if "ID_Servico" in df.columns and "Valor_Total_Sugerido_BRL" in df.columns:
        fig_bar = px.bar(
            df, x="ID_Servico", y="Valor_Total_Sugerido_BRL", 
            color="Categoria" if "Categoria" in df.columns else None,
            color_discrete_sequence=["#4f46e5", "#ef4444"]
        )
        fig_bar.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    st.markdown("##### Distribuição de Valores por Categoria")
    if "Categoria" in df.columns and "Valor_Total_Sugerido_BRL" in df.columns:
        fig_pie = px.pie(
            df, names="Categoria", values="Valor_Total_Sugerido_BRL", 
            hole=0.5,
            color_discrete_sequence=["#ef4444", "#10b981", "#3b82f6"]
        )
        fig_pie.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# 5. JANELA FLUTUANTE ESTILO WHATSAPP (Popup no canto inferior direito)
st.markdown("""
<div class="whatsapp-popup-container">
    <div class="whatsapp-header">
        <div style="background: #00a884; border-radius: 50%; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
            🎧
        </div>
        <div>
            <div style="font-weight: bold; font-size: 0.9rem;">Suporte de TI Online</div>
            <div style="font-size: 0.7rem; color: #00a884;">● online agora</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Container interativo do Chat flutuante
with st.container():
    st.markdown('<div style="position: fixed; bottom: 80px; right: 30px; width: 335px; z-index: 1000000; background: #0b141a; padding: 10px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">', unsafe_allow_html=True)
    
    chat_container = st.container(height=280)
    with chat_container:
        for m in st.session_state.wa_messages:
            if m["role"] == "user":
                st.markdown(f'<div class="wa-bubble-user">{m["content"]}<div class="wa-time">{m["time"]} ✓✓</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="wa-bubble-assistant">{m["content"]}<div class="wa-time">{m.get("time","04:44")}</div></div>', unsafe_allow_html=True)
                
    user_msg = st.chat_input("Digite sua dúvida ou código de erro...", key="wa_chat_input")
    st.markdown('</div>', unsafe_allow_html=True)

if user_msg:
    now_str = datetime.now().strftime("%H:%M")
    st.session_state.wa_messages.append({"role": "user", "content": user_msg, "time": now_str})
    
    resp_text = f"Recebi sua pergunta sobre: '{user_msg}'. O ticket médio atual é de R$ {df['Valor_Total_Sugerido_BRL'].mean():,.2f} com SLA médio de {df['SLA_Horas'].mean():.1f}h."
    st.session_state.wa_messages.append({"role": "assistant", "content": resp_text, "time": now_str})
    st.rerun()
