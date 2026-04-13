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
    campos_hist_ini = {c: [] for c in ["cargo", "comarca", "advogado", "oabn", "email", "custas", "cid10", "andamento"]}
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Garante que chaves novas existam ao carregar de um JSON antigo
            if "notas_diarias" not in data: data["notas_diarias"] = ""
            if "zoom_level" not in data: data["zoom_level"] = 100
            if "tema_escolhido" not in data: data["tema_escolhido"] = "Frio Escuro (Conforto)"
            return data
    return {"lista_peritos": peritos_padrao, "historicos": campos_hist_ini, "notas_diarias": "", "zoom_level": 100, "tema_escolhido": "Frio Escuro (Conforto)"}

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

# --- INICIALIZAÇÃO ---
dados_salvos = carregar_dados()
campos_hist = ["cargo", "comarca", "advogado", "oabn", "email", "custas", "cid10", "andamento"]

for key in ["zoom_level", "tema_escolhido", "notas_diarias", "lista_peritos"]:
    if key not in st.session_state: st.session_state[key] = dados_salvos[key]

for c in campos_hist:
    if f"hist_{c}" not in st.session_state:
        st.session_state[f"hist_{c}"] = dados_salvos["historicos"].get(c, [])

# --- TEMAS E ESTILO ---
temas = {
    "Frio Escuro (Conforto)": {"bg": "#0F172A", "text": "#F1F5F9", "card": "#1E293B", "input": "#0F172A", "border": "#334155"},
    "Cinza Profissional": {"bg": "#1E1E1E", "text": "#E0E0E0", "card": "#2D2D2D", "input": "#1E1E1E", "border": "#404040"},
    "Soft Blue (Claro)": {"bg": "#F0F4F8", "text": "#1E293B", "card": "#FFFFFF", "input": "#F8FAFC", "border": "#CBD5E1"}
}

tm = temas[st.session_state.tema_escolhido]
zoom = st.session_state.zoom_level / 100

st.markdown(f"""
    <style>
        .stApp {{ background-color: {tm['bg']}; color: {tm['text']}; zoom: {zoom}; }}
        .header-banner {{
            background-color: {tm['card']}; padding: 20px; border-radius: 8px;
            border-bottom: 4px solid #38B2AC; text-align: center; margin-bottom: 25px;
        }}
        .header-banner h1 {{ color: {tm['text']} !important; font-size: 1.6rem; margin: 0; }}
        .stTabs [data-baseweb="tab"] {{ color: {tm['text']}; font-weight: 600; }}
        input, textarea, select {{ 
            background-color: {tm['input']} !important; color: {tm['text']} !important; 
            border: 1px solid {tm['border']} !important; text-transform: uppercase;
        }}
        /* Evitar caixa alta no email */
        input[type="email"] {{ text-transform: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def limpar_tudo():
    for key in list(st.session_state.keys()):
        if key not in ['lista_peritos', 'notas_diarias', 'zoom_level', 'tema_escolhido'] + [f"hist_{c}" for c in campos_hist]:
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

# --- SIDEBAR (ZOOM, TEMA, NOTAS) ---
with st.sidebar:
    st.title("⚙️ CONFIGURAÇÕES")
    
    st.subheader("VISUAL")
    novo_tema = st.selectbox("Esquema de Cores", list(temas.keys()), index=list(temas.keys()).index(st.session_state.tema_escolhido))
    if novo_tema != st.session_state.tema_escolhido:
        st.session_state.tema_escolhido = novo_tema
        salvar_no_disco(); st.rerun()

    st.subheader("ACESSIBILIDADE")
    c_z1, c_z2 = st.columns(2)
    with c_z1: 
        if st.button("➕ ZOOM"): st.session_state.zoom_level += 5; salvar_no_disco(); st.rerun()
    with c_z2: 
        if st.button("➖ ZOOM"): st.session_state.zoom_level -= 5; salvar_no_disco(); st.rerun()
    
    st.divider()
    st.subheader("📓 BLOCO DE NOTAS")
    txt_notas = st.text_area("Anotações Gerais (JSON)", value=st.session_state.notas_diarias, height=250)
    if txt_notas != st.session_state.notas_diarias:
        st.session_state.notas_diarias = txt_notas
        salvar_no_disco()

# --- CONTEÚDO PRINCIPAL ---
st.markdown('<div class="header-banner"><h1>FICHA INTELIGENTE - TJ/SP SETOR DE ACIDENTES DA COMARCA DE SANTOS/SP</h1></div>', unsafe_allow_html=True)

col_main = st.columns([1, 10, 1])[1]

with col_main:
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
            perito_selecionado = st.selectbox("Banco de Dados", options=[""] + st.session_state.lista_peritos)
            if st.button("🗑️ REMOVER PERITO"):
                if perito_selecionado:
                    st.session_state.lista_peritos.remove(perito_selecionado); salvar_no_disco(); st.rerun()
        with cp2:
            novo_p = st.text_input("Cadastrar Novo Perito").upper()
            if st.button("➕ ADICIONAR"):
                if novo_p:
                    st.session_state.lista_peritos.append(novo_p); salvar_no_disco(); st.rerun()
        st.markdown("---")
        perito_manual = st.text_input("Perito Principal", key="perito_man").upper()
        peritoesp = st.text_input("Perito Especialista", key="peritoesp").upper()
        ca1, ca2 = st.columns(2)
        with ca1: assisa = st.text_input("Assist. Autor", key="assisa").upper()
        with ca2: assisb = st.text_input("Assist. Réu", key="assisb").upper()

    with aba4:
        queixa = st.text_area("Queixa", key="queixa").upper()
        cid_sel = st.selectbox("Histórico CID", [""] + st.session_state.hist_cid10)
        cid10 = (st.text_input("Novo CID", key="cid_txt") if not cid_sel else cid_sel).upper()
        and_sel = st.selectbox("Histórico Andamento", [""] + st.session_state.hist_andamento)
        andamento = (st.text_area("Novo Andamento", key="and_txt") if not and_sel else and_sel).upper()

    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # BOTÕES FINAIS
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("📄 GERAR FICHA", use_container_width=True):
            for c, v in [("cargo", cargo), ("comarca", comarca), ("advogado", advogado), ("oabn", oabn), ("email", email), ("custas", custas), ("cid10", cid10), ("andamento", andamento)]:
                salvar_hist(c, v)
            try:
                doc = DocxTemplate("ficha.docx")
                doc.render({"nome": nome, "filiacaopai": filiacaopai, "filiacaomae": filiacaomae, "rg": rg, "cpf": formatar_cpf(cpf), "cargo": cargo, "endereço": endereco, "processo": processo, "comarca": comarca, "perito": perito_manual, "peritoesp": peritoesp, "assisa": assisa, "assisb": assisb, "custas": custas, "advogado": advogado, "oabn": oabn, "email": email, "queixa": queixa, "cid10": cid10, "andamento": andamento})
                bio = io.BytesIO(); doc.save(bio)
                st.download_button("📥 BAIXAR FICHA", bio.getvalue(), f"{nome} {processo} AT.docx", use_container_width=True)
            except Exception as e: st.error(f"Erro: {e}")

    with b2:
        if st.button("⚖️ GERAR NOMEAÇÃO", use_container_width=True):
            if perito_selecionado:
                try:
                    doc_p = DocxTemplate("perito.docx")
                    doc_p.render({"perito": perito_selecionado.upper()})
                    bio_p = io.BytesIO(); doc_p.save(bio_p)
                    n_arq = perito_selecionado.split("–")[0].strip()
                    st.download_button(f"📥 BAIXAR NOMEAÇÃO", bio_p.getvalue(), f"{n_arq}.docx", use_container_width=True)
                except Exception as e: st.error(f"Erro: {e}")
            else: st.warning("Selecione um perito.")

    with b3:
        if st.button("⚠️ LIMPAR FORMULÁRIO", use_container_width=True):
            limpar_tudo(); st.rerun()
