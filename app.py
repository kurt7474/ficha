import streamlit as st
from docxtpl import DocxTemplate
import io
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Ficha Inteligente - TJSP",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LISTA DE DDDS DO BRASIL ---
DDDS_BRASIL = [
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "21", "22", "24", 
    "27", "28", "31", "32", "33", "34", "35", "37", "38", "41", "42", "43", 
    "44", "45", "46", "47", "48", "49", "51", "53", "54", "55", "61", "62", 
    "63", "64", "65", "66", "67", "68", "69", "71", "73", "74", "75", "77", 
    "79", "81", "82", "83", "84", "85", "86", "87", "88", "89", "91", "92", 
    "93", "94", "95", "96", "97", "98", "99"
]

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
        div.stButton > button[kind="primary"] { background-color: #1E40AF !important; color: white !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO ---
if 'lista_peritos' not in st.session_state:
    # Recomenda-se preencher com dados fictícios para subir ao GitHub
    st.session_state.lista_peritos = [
        "EXEMPLO: DR. NOME DO PERITO – CRM: 000000, CPF: 000.000.000-00"
    ]

campos_hist = ["cargo", "comarca", "advogado", "oabn", "email", "custas", "cid10", "andamento"]
for c in campos_hist:
    if f"hist_{c}" not in st.session_state:
        st.session_state[f"hist_{c}"] = []

# --- FUNÇÕES ---
def limpar_formulario():
    """Limpa os campos de entrada sem apagar o banco de peritos ou histórico."""
    chaves_input = [
        'nome', 'filiacaopai', 'filiacaomae', 'rg', 'cpf', 'endereco', 'processo',
        'cargo_txt', 'adv_txt', 'email_txt', 'com_txt', 'oab_txt', 'custas_txt',
        'perito_man', 'peritoesp', 'assisa', 'assisb', 'queixa', 'cid_txt', 'and_txt', 'tel_adv'
    ]
    for chave in chaves_input:
        if chave in st.session_state:
            st.session_state[chave] = ""

def formatar_cpf(cpf):
    c = re.sub(r'\D', '', cpf)
    return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}" if len(c) == 11 else cpf

def formatar_telefone(ddd, numero):
    num = re.sub(r'\D', '', numero)
    if len(num) == 9: return f"({ddd}) {num[:5]}-{num[5:]}"
    if len(num) == 8: return f"({ddd}) {num[:4]}-{num[4:]}"
    return f"({ddd}) {num}"

def salvar_hist(campo, valor):
    if valor and str(valor).strip():
        chave = f"hist_{campo}"
        valor_limpo = str(valor).strip().upper() if campo != "email" else str(valor).strip().lower()
        if valor_limpo not in st.session_state[chave]:
            st.session_state[chave].append(valor_limpo)

# --- LAYOUT ---
st.markdown('<div class="header-banner"><h1>FICHA INTELIGENTE</h1><p>TJ/SP - PERÍCIA ACIDENTÁRIA</p></div>', unsafe_allow_html=True)

col_e, col_c, col_d = st.columns([0.5, 9, 0.5])

with col_c:
    st.button("🧹 LIMPAR APENAS CAMPOS (NOVA FICHA)", on_click=limpar_formulario, type="secondary")
    
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
            endereco = st.text_area("Endereço Completo", key="endereco").upper()

    with aba2:
        processo = st.text_input("Nº Processo", key="processo").upper()
        col3, col4 = st.columns(2)
        with col3:
            adv_sel = st.selectbox("Histórico Advogado", [""] + st.session_state.hist_advogado)
            adv_txt = st.text_input("Novo Advogado", key="adv_txt").upper()
            advogado = adv_txt if adv_txt else adv_sel

            email_sel = st.selectbox("Histórico E-mail", [""] + st.session_state.hist_email)
            email_txt = st.text_input("Novo E-mail", key="email_txt").lower() # CAIXA BAIXA
            email = email_txt if email_txt else email_sel
        with col4:
            com_sel = st.selectbox("Histórico Comarca", [""] + st.session_state.hist_comarca)
            com_txt = st.text_input("Nova Comarca", key="com_txt").upper()
            comarca = com_txt if com_txt else com_sel

            # Telefone do Advogado com DDD
            c_ddd, c_num = st.columns([1, 3])
            with c_ddd: ddd_adv = st.selectbox("DDD", DDDS_BRASIL, index=2) # Index 2 = DDD 13
            with c_num: tel_raw = st.text_input("Telefone Advogado", key="tel_adv")
            tel_advogado = formatar_telefone(ddd_adv, tel_raw)

            oab_sel = st.selectbox("Histórico OAB", [""] + st.session_state.hist_oabn)
            oab_txt = st.text_input("Nova OAB", key="oab_txt").upper()
            oabn = oab_txt if oab_txt else oab_sel

    with aba3:
        st.subheader("Gerenciamento de Peritos")
        cp1, cp2 = st.columns([3, 2])
        with cp1:
            perito_selecionado = st.selectbox("Banco de Dados de Peritos", [""] + st.session_state.lista_peritos)
            if st.button("🗑️ REMOVER PERITO"):
                if perito_selecionado:
                    st.session_state.lista_peritos.remove(perito_selecionado)
                    st.rerun()
        with cp2:
            novo_p = st.text_input("Cadastrar Novo Perito (NOME, CRM, CPF, RG, NIT)").upper()
            if st.button("➕ ADICIONAR"):
                if novo_p:
                    st.session_state.lista_peritos.append(novo_p)
                    st.rerun()
        perito_manual = st.text_input("Perito Principal (Ficha)", key="perito_man").upper()
        peritoesp = st.text_input("Perito Especialista", key="peritoesp").upper()

    with aba4:
        queixa = st.text_area("Queixa", key="queixa").upper()
        cid_sel = st.selectbox("Histórico CID", [""] + st.session_state.hist_cid10)
        cid_txt = st.text_input("Novo CID", key="cid_txt").upper()
        cid10 = cid_txt if cid_txt else cid_sel
        and_sel = st.selectbox("Histórico Andamento", [""] + st.session_state.hist_andamento)
        and_txt = st.text_area("Novo Andamento", key="and_txt").upper()
        andamento = and_txt if and_txt else and_sel

    # --- BOTÕES DE GERAÇÃO ---
    st.markdown("---")
    cf, cp = st.columns(2)
    with cf:
        if st.button("📄 GERAR FICHA (FICHA.DOCX)", use_container_width=True):
            # Salva históricos
            for c, v in [("cargo", cargo), ("comarca", comarca), ("advogado", advogado), 
                         ("oabn", oabn), ("email", email), ("cid10", cid10)]:
                salvar_hist(c, v)
            try:
                doc = DocxTemplate("ficha.docx")
                ctx = {
                    "nome": nome, "filiacaopai": filiacaopai, "filiacaomae": filiacaomae, 
                    "rg": rg, "cpf": formatar_cpf(cpf), "cargo": cargo, "endereço": endereco, 
                    "processo": processo, "comarca": comarca, "perito": perito_manual, 
                    "peritoesp": peritoesp, "advogado": advogado, "oabn": oabn, 
                    "email": email, "telefone_adv": tel_advogado, "queixa": queixa, 
                    "cid10": cid10, "andamento": andamento
                }
                doc.render(ctx)
                bio = io.BytesIO()
                doc.save(bio)
                st.download_button("📥 BAIXAR FICHA", bio.getvalue(), f"{nome} {processo} AT.docx", use_container_width=True)
            except Exception as e: st.error(f"Erro: {e}")

    with cp:
        if st.button("⚖️ GERAR NOMEAÇÃO", type="primary", use_container_width=True):
            if perito_selecionado:
                try:
                    doc_p = DocxTemplate("perito.docx")
                    doc_p.render({"perito": perito_selecionado})
                    bio_p = io.BytesIO()
                    doc_p.save(bio_p)
                    n_arq = perito_selecionado.split("–")[0].strip().upper()
                    st.download_button(f"📥 BAIXAR NOMEAÇÃO", bio_p.getvalue(), f"{n_arq}.docx", use_container_width=True)
                except Exception as e: st.error(f"Erro: {e}")
            else: st.warning("Selecione um perito na aba EQUIPE.")
