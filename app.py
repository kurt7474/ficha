import streamlit as st
from docxtpl import DocxTemplate
import io
import re
import json
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Ficha Inteligente - Santos/SP",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PERSISTÊNCIA DE DADOS (JSON) ---
DB_FILE = "database.json"

def carregar_dados():
    peritos_padrao = ["PEDRO DEMÉTRIO HAICK – CRM: 217.178", "EXEMPLO DE PERITO 02"]
    campos_vazios = {c: [] for c in ["cargo", "comarca", "advogado", "oabn", "email", "custas", "cid10", "andamento"]}
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"lista_peritos": peritos_padrao, "historicos": campos_vazios, "notas_diarias": ""}

def salvar_no_disco():
    dados = {
        "lista_peritos": st.session_state.lista_peritos,
        "historicos": {c: st.session_state[f"hist_{c}"] for c in campos_hist},
        "notas_diarias": st.session_state.notas_diarias,
        "zoom_level": st.session_state.zoom_level,
        "tema_escolhido": st.session_state.tema_escolhido
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- INICIALIZAÇÃO DO ESTADO ---
dados_salvos = carregar_dados()

if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = dados_salvos.get("zoom_level", 100)
if 'tema_escolhido' not in st.session_state:
    st.session_state.tema_escolhido = dados_salvos.get("tema_escolhido", "Frio Escuro (Conforto)")
if 'notas_diarias' not in st.session_state:
    st.session_state.notas_diarias = dados_salvos.get("notas_diarias", "")
if 'lista_peritos' not in st.session_state:
    st.session_state.lista_peritos = dados_salvos["lista_peritos"]

campos_hist = ["cargo", "comarca", "advogado", "oabn", "email", "custas", "cid10", "andamento"]
for c in campos_hist:
    if f"hist_{c}" not in st.session_state:
        st.session_state[f"hist_{c}"] = dados_salvos["historicos"].get(c, [])

# --- LÓGICA DE TEMAS E ACESSIBILIDADE ---
temas = {
    "Frio Escuro (Conforto)": {"bg": "#0F172A", "text": "#E2E8F0", "card": "#1E293B", "input": "#334155"},
    "Azul Suave": {"bg": "#F0F4F8", "text": "#1E293B", "card": "#FFFFFF", "input": "#F8FAFC"},
    "Alto Contraste": {"bg": "#000000", "text": "#FFFFFF", "card": "#1A1A1A", "input": "#333333"}
}

t = temas[st.session_state.tema_escolhido]
zoom = st.session_state.zoom_level / 100

st.markdown(f"""
    <style>
        .stApp {{
            background-color: {t['bg']};
            color: {t['text']};
            zoom: {zoom};
        }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
        
        /* Banner */
        .header-banner {{
            background-color: {t['card']};
            padding: 20px;
            border-radius: 8px;
            border-left: 10px solid #38B2AC;
            margin-bottom: 20px;
        }}
        
        /* Bloco de Notas */
        .stTextArea textarea {{
            background-color: {t['input']} !important;
            color: {t['text']} !important;
        }}

        /* Botões */
        div.stButton > button {{
            border-radius: 5px;
            transition: 0.3s;
        }}
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.title("⚙️ Ajustes")
    
    st.subheader("Visual")
    tema = st.selectbox("Paleta de Cores", list(temas.keys()), index=list(temas.keys()).index(st.session_state.tema_escolhido))
    if tema != st.session_state.tema_escolhido:
        st.session_state.tema_escolhido = tema
        salvar_no_disco()
        st.rerun()

    st.subheader("Zoom")
    col_z1, col_z2 = st.columns(2)
    with col_z1:
        if st.button("➕ Aumentar"):
            st.session_state.zoom_level += 10
            salvar_no_disco()
            st.rerun()
    with col_z2:
        if st.button("➖ Diminuir"):
            st.session_state.zoom_level -= 10
            salvar_no_disco()
            st.rerun()
    
    st.divider()
    st.subheader("📓 Bloco de Notas (Auto-save)")
    notas = st.text_area("Anotações do dia:", value=st.session_state.notas_diarias, height=300, key="txt_notas")
    if notas != st.session_state.notas_diarias:
        st.session_state.notas_diarias = notas
        salvar_no_disco()

# --- CONTEÚDO PRINCIPAL ---
st.markdown(f'<div class="header-banner"><h1>FICHA INTELIGENTE - SANTOS/SP</h1><p style="color:#38B2AC">Setor de Acidentes do Trabalho</p></div>', unsafe_allow_html=True)

# Botão Limpar reposicionado para o lado das ações
def limpar_form():
    for key in list(st.session_state.keys()):
        if key not in ['lista_peritos', 'notas_diarias', 'zoom_level', 'tema_escolhido'] + [f"hist_{c}" for c in campos_hist]:
            st.session_state[key] = ""

aba1, aba2, aba3, aba4 = st.tabs(["👤 Dados", "📂 Processo", "⚕️ Peritos", "📝 Exame"])

with aba1:
    nome = st.text_input("Nome Completo", key="nome").upper()
    c1, c2 = st.columns(2)
    with c1:
        rg = st.text_input("RG", key="rg")
        cargo_sel = st.selectbox("Profissão", [""] + st.session_state.hist_cargo)
        cargo = st.text_input("Outra Profissão", key="c_txt").upper() if not cargo_sel else cargo_sel
    with c2:
        cpf = st.text_input("CPF", key="cpf")
        endereco = st.text_area("Endereço", key="end").upper()

# ... (O restante das abas segue a mesma lógica dos códigos anteriores) ...

with aba3:
    st.subheader("Gerenciamento de Peritos")
    perito_selecionado = st.selectbox("Banco de Dados", options=[""] + st.session_state.lista_peritos)
    if st.button("➕ Adicionar Perito"):
        # lógica de adicionar...
        pass

st.divider()

# --- AÇÕES FINAIS ---
c_btn1, c_btn2, c_btn3 = st.columns([3, 3, 2])

with c_btn1:
    if st.button("📄 GERAR FICHA DOCX", use_container_width=True, type="primary"):
        # Lógica de salvar histórico e gerar documento...
        st.success("Ficha preparada!")

with c_btn2:
    if st.button("📜 TERMO DE NOMEAÇÃO", use_container_width=True):
        st.info("Selecione o perito na aba correspondente.")

with c_btn3:
    if st.button("⚠️ LIMPAR TUDO", use_container_width=True):
        limpar_form()
        st.rerun()
