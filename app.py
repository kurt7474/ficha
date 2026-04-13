import streamlit as st
from docxtpl import DocxTemplate
import io
import re
import json
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Ficha Inteligente - TJSP",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PERSISTÊNCIA DE DADOS (JSON) ---
DB_FILE = "database.json"

def carregar_dados():
    """Carrega dados do JSON ou retorna valores padrão se não existir."""
    peritos_padrao = [
        "PEDRO DEMÉTRIO HAICK – CRM: 217.178, RG: 48.725.734-92, CPF: 391.134.878-92",
        "PEDRO LUIS DOS SANTOS PRIOR PEREIRA DA SILVA – CRM: 162862, RG: 44.894.580-0, CPF: 378.342.678-25",
        "AARON ÉSSIO PEREIRA GRANDIZOLI, CRM: 223.536 RG: 39.369.333-8 CPF: 458.508.618-82",
        "ABRÃO MOISÉS ALTMAN, CRM: 1477, CPF: 048.942.948-34, NIT: 1.001.877.456-0",
        "MILTON ANTONIO PAPI, CRM: 81405, CPF: 477.275.190-49, NIT: 1.140.372.913-6",
        "MAURICI ARAGÃO TAVARES, CRM: 33.006, CPF: 327.796.407/82, NIT: 10112466181",
        "LUCAS PEDROSO FERNANDES FERREIRA LEAL, CRM: 124.83, CPF: 314.508.888/28, NIT: 119835377/18",
        "DIEGO ABAD DOS SANTOS, CRM: 120.907, CPF: 296.924.128-57"
    ]
    
    campos_vazios = {c: [] for c in ["cargo", "comarca", "advogado", "oabn", "email", "custas", "cid10", "andamento"]}
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {"lista_peritos": peritos_padrao, "historicos": campos_vazios}

def salvar_no_disco():
    """Salva o estado atual do session_state no arquivo JSON."""
    dados = {
        "lista_peritos": st.session_state.lista_peritos,
        "historicos": {c: st.session_state[f"hist_{c}"] for c in campos_hist}
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- INICIALIZAÇÃO DO ESTADO ---
dados_salvos = carregar_dados()

if 'lista_peritos' not in st.session_state:
    st.session_state.lista_peritos = dados_salvos["lista_peritos"]

campos_hist = ["cargo", "comarca", "advogado", "oabn", "email", "custas", "cid10", "andamento"]
for c in campos_hist:
    if f"hist_{c}" not in st.session_state:
        st.session_state[f"hist_{c}"] = dados_salvos["historicos"].get(c, [])

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
        .block-container { max-width: 1100px; padding-top: 2rem; }
        .header-banner {
            background-color: #1E3A8A; 
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 25px;
        }
        .header-banner h1 { color: white !important; margin: 0; font-size: 2.2rem; }
        .header-banner p { color: #BFDBFE; margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-transform: uppercase; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #F1F5F9; padding: 10px 10px 0 10px; border-radius: 8px; }
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: #E2E8F0; border-radius: 8px 8px 0 0; color: #475569; font-weight: 600; }
        .stTabs [aria-selected="true"] { background-color: #1E40AF !important; color: white !important; }
        div.stButton > button[kind="primary"] { background-color: #1E40AF !important; color: white !important; font-weight: bold; }
        div.stButton > button[kind="secondary"] { background-color: #64748B !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE INTERAÇÃO ---
def limpar_tudo():
    for key in list(st.session_state.keys()):
        if key not in ['lista_peritos'] + [f"hist_{c}" for c in campos_hist]:
            st.session_state[key] = ""

def formatar_cpf(cpf):
    c = re.sub(r'\D', '', cpf)
    return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}" if len(c) == 11 else cpf

def salvar_hist(campo, valor):
    if valor and valor.strip():
        chave = f"hist_{campo}"
        if valor.strip().upper() not in [x.upper() for x in st.session_state[chave]]:
            st.session_state[chave].append(valor.strip().upper())
            salvar_no_disco()

# --- LAYOUT INTERFACE ---
st.markdown("""
    <div class="header-banner">
        <h1>FICHA INTELIGENTE</h1>
        <p>TJ/SP - PERÍCIA ACIDENTÁRIA</p>
    </div>
""", unsafe_allow_html=True)

col_e, col_c, col_d = st.columns([0.5, 9, 0.5])

with col_c:
    c_espaço, c_limpa = st.columns([7, 2])
    with c_limpa:
        st.button("🧹 LIMPAR FORMULÁRIO", on_click=limpar_tudo, type="secondary", use_container_width=True)

    st.write("##")
    aba1, aba2, aba3, aba4 = st.tabs(["👤 PESSOAL", "📂 PROCESSO", "⚕️ EQUIPE", "📝 CLÍNICA"])

    with aba1:
        nome = st.text_input("Nome Completo", key="nome").upper()
        c1, c2 = st.columns(2)
        with c1:
            filiacaopai = st.text_input("Filiação (Pai)", key="filiacaopai").upper()
            rg = st.text_input("RG", key="rg").upper()
            cargo_sel = st.selectbox("Histórico Profissão", [""] + st.session_state.hist_cargo)
            cargo_txt = st.text_input("Nova Profissão", key="cargo_txt").upper()
            cargo = cargo_txt if cargo_txt else cargo_sel
        with c2:
            filiacaomae = st.text_input("Filiação (Mãe)", key="filiacaomae").upper()
            cpf = st.text_input("CPF", key="cpf")
            endereco = st.text_area("Endereço Completo", key="endereco", height=100).upper()

    with aba2:
        processo = st.text_input("Nº Processo", key="processo").upper()
        col3, col4 = st.columns(2)
        with col3:
            adv_sel = st.selectbox("Histórico Advogado", [""] + st.session_state.hist_advogado)
            advogado = (st.text_input("Novo Advogado", key="adv_txt") if not adv_sel else adv_sel).upper()
            email_sel = st.selectbox("Histórico E-mail", [""] + st.session_state.hist_email)
            email = (st.text_input("Novo E-mail", key="email_txt") if not email_sel else email_sel).lower()
        with col4:
            com_sel = st.selectbox("Histórico Comarca", [""] + st.session_state.hist_comarca)
            comarca = (st.text_input("Nova Comarca", key="com_txt") if not com_sel else com_sel).upper()
            oab_sel = st.selectbox("Histórico OAB", [""] + st.session_state.hist_oabn)
            oabn = (st.text_input("Nova OAB", key="oab_txt") if not oab_sel else oab_sel).upper()
            custas_sel = st.selectbox("Histórico Custas", [""] + st.session_state.hist_custas)
            custas = (st.text_input("Nova Custa", key="custas_txt") if not custas_sel else custas_sel).upper()

    with aba3:
        st.subheader("Gerenciamento de Peritos")
        cp1, cp2 = st.columns([3, 2])
        with cp1:
            perito_selecionado = st.selectbox("Banco de Dados de Peritos", options=[""] + st.session_state.lista_peritos, key="sel_p")
            if st.button("🗑️ REMOVER PERITO", type="secondary"):
                if perito_selecionado:
                    st.session_state.lista_peritos.remove(perito_selecionado)
                    salvar_no_disco()
                    st.rerun()
        with cp2:
            novo_p = st.text_input("Cadastrar Novo Perito", key="inp_p").upper()
            if st.button("➕ ADICIONAR AO BANCO", type="secondary"):
                if novo_p:
                    st.session_state.lista_peritos.append(novo_p)
                    salvar_no_disco()
                    st.rerun()
        st.markdown("---")
        perito_manual = st.text_input("Perito Principal (Para Ficha)", key="perito_man").upper()
        peritoesp = st.text_input("Perito Especialista", key="peritoesp").upper()
        ca1, ca2 = st.columns(2)
        with ca1: assisa = st.text_input("Assis. Autor", key="assisa").upper()
        with ca2: assisb = st.text_input("Assis. Réu", key="assisb").upper()

    with aba4:
        queixa = st.text_area("Queixa", key="queixa").upper()
        cid_sel = st.selectbox("Histórico CID", [""] + st.session_state.hist_cid10)
        cid10 = (st.text_input("Novo CID", key="cid_txt") if not cid_sel else cid10_sel).upper()
        and_sel = st.selectbox("Histórico Andamento", [""] + st.session_state.hist_andamento)
        andamento = (st.text_area("Novo Andamento", key="and_txt") if not and_sel else and_sel).upper()

    st.write("##")
    st.markdown("---")
    
    cf, cp = st.columns(2)
    with cf:
        if st.button("📄 GERAR FICHA (FICHA.DOCX)", type="secondary", use_container_width=True):
            for c, v in [("cargo", cargo), ("comarca", comarca), ("advogado", advogado), ("oabn", oabn), ("email", email), ("custas", custas), ("cid10", cid10), ("andamento", andamento)]:
                salvar_hist(c, v)
            try:
                doc = DocxTemplate("ficha.docx")
                ctx = {
                    "nome": nome, "filiacaopai": filiacaopai, "filiacaomae": filiacaomae, 
                    "rg": rg, "cpf": formatar_cpf(cpf), "cargo": cargo, "endereço": endereco, 
                    "processo": processo, "comarca": comarca, "perito": perito_manual, 
                    "peritoesp": peritoesp, "assisa": assisa, "assisb": assisb, 
                    "custas": custas, "advogado": advogado, "oabn": oabn, 
                    "email": email, "queixa": queixa, "cid10": cid10, "andamento": andamento
                }
                doc.render(ctx)
                bio = io.BytesIO()
                doc.save(bio)
                nome_doc = f"{nome} {processo} AT.docx"
                st.download_button("📥 BAIXAR FICHA", bio.getvalue(), nome_doc, use_container_width=True)
            except Exception as e: st.error(f"Erro: {e}")

    with cp:
        if st.button("⚖️ GERAR NOMEAÇÃO (PERITO.DOCX)", type="primary", use_container_width=True):
            if perito_selecionado:
                try:
                    doc_p = DocxTemplate("perito.docx")
                    doc_p.render({"perito": perito_selecionado.upper()})
                    bio_p = io.BytesIO()
                    doc_p.save(bio_p)
                    n_arq = perito_selecionado.split("–")[0].split("-")[0].strip().upper()
                    st.download_button(f"📥 BAIXAR NOMEAÇÃO: {n_arq}", bio_p.getvalue(), f"{n_arq}.docx", use_container_width=True)
                except Exception as e: st.error(f"Erro: {e}")
            else: st.warning("Selecione um perito na aba EQUIPE.")
