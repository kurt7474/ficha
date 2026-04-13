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
    dados = {
        "lista_peritos": st.session_state.lista_peritos,
        "historicos": {c: st.session_state[f"hist_{c}"] for c in campos_hist}
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- INICIALIZAÇÃO ---
dados_salvos = carregar_dados()
if 'lista_peritos' not in st.session_state:
    st.session_state.lista_peritos = dados_salvos["lista_peritos"]

campos_hist = ["cargo", "comarca", "advogado", "oabn", "email", "custas", "cid10", "andamento"]
for c in campos_hist:
    if f"hist_{c}" not in st.session_state:
        st.session_state[f"hist_{c}"] = dados_salvos["historicos"].get(c, [])

# --- ESTILIZAÇÃO FORMAL (CORES FRIAS) ---
st.markdown("""
    <style>
        /* Fundo e Container */
        .main { background-color: #F8FAFC; }
        .block-container { max-width: 1200px; padding-top: 2rem; }
        
        /* Banner Formal */
        .header-banner {
            background-color: #0F172A; /* Azul marinho profundo */
            padding: 30px;
            border-radius: 4px;
            border-bottom: 5px solid #334155;
            text-align: center;
            margin-bottom: 35px;
        }
        .header-banner h1 { 
            color: #F1F5F9 !important; 
            margin: 0; 
            font-size: 1.8rem; 
            letter-spacing: 1px;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Abas */
        .stTabs [data-baseweb="tab-list"] { 
            gap: 8px; 
            background-color: transparent; 
        }
        .stTabs [data-baseweb="tab"] { 
            height: 45px; 
            background-color: #E2E8F0; 
            border-radius: 4px 4px 0 0; 
            color: #475569; 
            padding: 0 20px;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #334155 !important; 
            color: white !important; 
        }

        /* Botões Separados e Estilizados */
        div.stButton > button {
            width: 100%;
            border-radius: 4px;
            height: 3em;
            transition: all 0.3s;
            text-transform: uppercase;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 10px; /* Separação entre botões */
        }
        
        /* Botão Primário (Azul Escuro) */
        div.stButton > button[kind="primary"] {
            background-color: #1E293B !important;
            color: white !important;
            border: none;
        }
        
        /* Botão Secundário (Cinza/Azul Frio) */
        div.stButton > button[kind="secondary"] {
            background-color: #64748B !important;
            color: white !important;
            border: none;
        }
        
        div.stButton > button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Campos de Entrada */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border-radius: 4px !important;
            border: 1px solid #CBD5E1 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
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

# --- INTERFACE ---
st.markdown("""
    <div class="header-banner">
        <h1>FICHA INTELIGENTE - TJ/SP SETOR DE ACIDENTES DA COMARCA DE SANTOS/SP</h1>
    </div>
""", unsafe_allow_html=True)

col_c = st.columns([1, 10, 1])[1]

with col_c:
    # Botão de limpeza isolado no topo direito
    c_limpa_espaço, c_limpa_btn = st.columns([8, 2])
    with c_limpa_btn:
        st.button("🧹 LIMPAR CAMPOS", on_click=limpar_tudo, type="secondary")

    aba1, aba2, aba3, aba4 = st.tabs(["👤 DADOS PESSOAIS", "📂 PROCESSO", "⚕️ GERENCIAMENTO PERITOS", "📝 EXAME CLÍNICO"])

    with aba1:
        nome = st.text_input("Nome Completo", key="nome").upper()
        c1, c2 = st.columns(2)
        with c1:
            filiacaopai = st.text_input("Filiação (Pai)", key="filiacaopai").upper()
            rg = st.text_input("RG", key="rg").upper()
            cargo_sel = st.selectbox("Profissões Cadastradas", [""] + st.session_state.hist_cargo)
            cargo_txt = st.text_input("Nova Profissão (se não houver na lista)", key="cargo_txt").upper()
            cargo = cargo_txt if cargo_txt else cargo_sel
        with c2:
            filiacaomae = st.text_input("Filiação (Mãe)", key="filiacaomae").upper()
            cpf = st.text_input("CPF", key="cpf")
            endereco = st.text_area("Endereço", key="endereco", height=108).upper()

    with aba2:
        processo = st.text_input("Nº Processo", key="processo").upper()
        col3, col4 = st.columns(2)
        with col3:
            adv_sel = st.selectbox("Advogados no Histórico", [""] + st.session_state.hist_advogado)
            advogado = (st.text_input("Nome do Advogado", key="adv_txt") if not adv_sel else adv_sel).upper()
            email_sel = st.selectbox("E-mails no Histórico", [""] + st.session_state.hist_email)
            email = (st.text_input("E-mail para Contato", key="email_txt") if not email_sel else email_sel).lower()
        with col4:
            com_sel = st.selectbox("Comarcas no Histórico", [""] + st.session_state.hist_comarca)
            comarca = (st.text_input("Comarca", key="com_txt") if not com_sel else com_sel).upper()
            oab_sel = st.selectbox("OABs no Histórico", [""] + st.session_state.hist_oabn)
            oabn = (st.text_input("Nº OAB", key="oab_txt") if not oab_sel else oab_sel).upper()
            custas_sel = st.selectbox("Tipos de Custas", [""] + st.session_state.hist_custas)
            custas = (st.text_input("Custas Processuais", key="custas_txt") if not custas_sel else custas_sel).upper()

    with aba3:
        st.subheader("Administração de Peritos")
        cp1, cp2 = st.columns([3, 2])
        with cp1:
            perito_selecionado = st.selectbox("Selecione Perito do Banco", options=[""] + st.session_state.lista_peritos, key="sel_p")
            if st.button("🗑️ EXCLUIR PERITO SELECIONADO", type="secondary"):
                if perito_selecionado:
                    st.session_state.lista_peritos.remove(perito_selecionado)
                    salvar_no_disco()
                    st.rerun()
        with cp2:
            novo_p = st.text_input("Nome/Dados Novo Perito", key="inp_p").upper()
            if st.button("➕ CADASTRAR NOVO PERITO", type="secondary"):
                if novo_p:
                    st.session_state.lista_peritos.append(novo_p)
                    salvar_no_disco()
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Definição para o Documento")
        perito_manual = st.text_input("Perito que assina a Ficha", key="perito_man").upper()
        peritoesp = st.text_input("Perito Especialista (se houver)", key="peritoesp").upper()
        ca1, ca2 = st.columns(2)
        with ca1: assisa = st.text_input("Assistente do Autor", key="assisa").upper()
        with ca2: assisb = st.text_input("Assistente do Réu", key="assisb").upper()

    with aba4:
        queixa = st.text_area("Queixa e Histórico Clínico", key="queixa", height=150).upper()
        cid_sel = st.selectbox("CIDs Frequentes", [""] + st.session_state.hist_cid10)
        cid10 = (st.text_input("Código CID-10", key="cid_txt") if not cid_sel else cid_sel).upper()
        and_sel = st.selectbox("Andamentos Sugeridos", [""] + st.session_state.hist_andamento)
        andamento = (st.text_area("Descrição do Andamento", key="and_txt", height=100) if not and_sel else and_sel).upper()

    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # Botões de ação final separados em colunas
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("📂 GERAR ARQUIVO DA FICHA", type="secondary", use_container_width=True):
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
                st.download_button("📥 CLIQUE PARA BAIXAR FICHA (.DOCX)", bio.getvalue(), f"{nome} {processo} AT.docx", use_container_width=True)
            except Exception as e: st.error(f"Erro ao gerar ficha: {e}")

    with btn_col2:
        if st.button("📜 GERAR TERMO DE NOMEAÇÃO", type="primary", use_container_width=True):
            if perito_selecionado:
                try:
                    doc_p = DocxTemplate("perito.docx")
                    doc_p.render({"perito": perito_selecionado.upper()})
                    bio_p = io.BytesIO()
                    doc_p.save(bio_p)
                    n_arq = perito_selecionado.split("–")[0].split("-")[0].strip().upper()
                    st.download_button(f"📥 BAIXAR NOMEAÇÃO: {n_arq}", bio_p.getvalue(), f"NOMEACAO_{n_arq}.docx", use_container_width=True)
                except Exception as e: st.error(f"Erro ao gerar nomeação: {e}")
            else: st.warning("Atenção: Selecione um perito na aba 'GERENCIAMENTO PERITOS' primeiro.")
