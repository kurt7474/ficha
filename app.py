import streamlit as st
from docxtpl import DocxTemplate
import io
import re
import json
import os

# --- Sistema de Histórico Local ---
ARQUIVO_HISTORICO = 'historico.json'

def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_historico(dados):
    with open(ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

historico_db = carregar_historico()

def atualizar_historico(chave, valor):
    if not valor or str(valor).strip() == "": 
        return
    if chave not in historico_db:
        historico_db[chave] = []
    # Salva apenas se o valor ainda não existir no histórico daquele campo
    if valor not in historico_db[chave]:
        historico_db[chave].append(valor)
        salvar_historico(historico_db)

# Função auxiliar para criar campos com histórico
def campo_com_historico(label, chave, is_area=False):
    opcoes = historico_db.get(chave, [])
    # Cria o selectbox para escolher do histórico
    escolha = st.selectbox(f"📋 Histórico: {label}", ["(Novo Cadastro)"] + opcoes, key=f"sel_{chave}")
    
    # Se for um novo cadastro, o campo fica vazio. Se puxou do histórico, preenche para edição.
    if escolha == "(Novo Cadastro)":
        if is_area:
            return st.text_area(f"Digite: {label}", value="", key=chave)
        else:
            return st.text_input(f"Digite: {label}", value="", key=chave)
    else:
        if is_area:
            return st.text_area(f"Confirmar/Editar: {label}", value=escolha, key=chave)
        else:
            return st.text_input(f"Confirmar/Editar: {label}", value=escolha, key=chave)


# Configuração da página
st.set_page_config(page_title="Ficha Inteligente", layout="wide")

# --- Função corrigida para limpar os dados ---
def limpar_dados():
    for key in st.session_state.keys():
        if key.startswith("sel_"):
            st.session_state[key] = "(Novo Cadastro)"
        elif key == "orgao_emissor":
            st.session_state[key] = "SSP/SP"
        elif isinstance(st.session_state[key], str):
            st.session_state[key] = ""

def formatar_cpf(cpf):
    cpf_limpo = re.sub(r'\D', '', cpf)
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf

st.title("Ficha Inteligente - Gerador de Documentos")

col_titulo, col_botao = st.columns([4, 1])
with col_botao:
    st.button("🧹 Limpar Ficha", on_click=limpar_dados, use_container_width=True)

st.markdown("---")

aba_pessoal, aba_processo, aba_peritos, aba_medica = st.tabs([
    "Dados Pessoais", "Dados do Processo", "Equipe Técnica", "Dados Clínicos/Andamento"
])

with aba_pessoal:
    nome = st.text_input("Nome", key="nome")
    col1, col2 = st.columns(2)
    with col1:
        filiacaopai = st.text_input("Filiação (Pai)", key="filiacaopai")
        rg = st.text_input("RG nº (Apenas números)", key="rg")
        orgao_emissor = st.selectbox("Órgão Emissor / Estado do RG", [
            "SSP/SP", "SSP/RJ", "SSP/MG", "SSP/ES", "SSP/BA", "SSP/PR", "SSP/SC", "SSP/RS", 
            "SSP/GO", "SSP/MT", "SSP/MS", "SSP/DF", "SSP/PE", "SSP/CE", "SSP/MA", "SSP/PB", 
            "SSP/RN", "SSP/AL", "SSP/SE", "SSP/PI", "SSP/PA", "SSP/AM", "SSP/RO", "SSP/AC", 
            "SSP/AP", "SSP/RR", "SSP/TO", "Outro"
        ], key="orgao_emissor")
        
        # Campo com Histórico: Profissão
        st.markdown("---")
        cargo = campo_com_historico("Profissão", "cargo")
        
    with col2:
        filiacaomae = st.text_input("Filiação (Mãe)", key="filiacaomae")
        cpf = st.text_input("CPF nº (Digite apenas números)", key="cpf")
        telefone = st.text_input("Telefone", key="telefone")
    
    st.markdown("---")
    endereco = st.text_input("Endereço", key="endereco")

with aba_processo:
    col3, col4 = st.columns(2)
    with col3:
        processo = st.text_input("Nº do Processo", key="processo")
        st.markdown("---")
        # Campos com Histórico
        advogado = campo_com_historico("Advogado", "advogado")
        st.markdown("---")
        email = st.text_input("E-mail", key="email")
    with col4:
        # Campos com Histórico
        comarca = campo_com_historico("Comarca", "comarca")
        st.markdown("---")
        oabn = campo_com_historico("OAB Nº", "oabn")
        st.markdown("---")
        custas = campo_com_historico("Juntada de Custas", "custas")

with aba_peritos:
    col5, col6 = st.columns(2)
    with col5:
        perito = campo_com_historico("Perito Principal", "perito")
        st.markdown("---")
        assisa = campo_com_historico("Assistente Técnico do Autor", "assisa")
    with col6:
        peritoesp = campo_com_historico("Perito Especialista", "peritoesp")
        st.markdown("---")
        assisb = campo_com_historico("Assistente Técnico do Réu", "assisb")

with aba_medica:
    queixa = st.text_area("Queixa", key="queixa")
    st.markdown("---")
    cid10 = campo_com_historico("CID10 + Patologia", "cid10")
    st.markdown("---")
    andamento = campo_com_historico("Andamento", "andamento", is_area=True)

st.markdown("---")

# Botão para gerar o documento
if st.button("Gerar Ficha Inteligente", type="primary"):
    
    # 1. Salvar as novas entradas no arquivo historico.json
    atualizar_historico("cargo", cargo)
    atualizar_historico("advogado", advogado)
    atualizar_historico("comarca", comarca)
    atualizar_historico("oabn", oabn)
    atualizar_historico("custas", custas)
    atualizar_historico("perito", perito)
    atualizar_historico("peritoesp", peritoesp)
    atualizar_historico("assisa", assisa)
    atualizar_historico("assisb", assisb)
    atualizar_historico("cid10", cid10)
    atualizar_historico("andamento", andamento)

    # 2. Renderizar o Documento
    try:
        doc = DocxTemplate("ficha.docx")
        
        contexto = {
            "nome": nome.upper(),
            "filiacaopai": filiacaopai.upper(),
            "filiacaomae": filiacaomae.upper(),
            "rg": f"{rg} - {orgao_emissor}" if rg else "",
            "cpf": formatar_cpf(cpf),
            "cargo": cargo.upper(),
            "endereço": endereco.upper(),
            "processo": processo,
            "comarca": comarca.upper(),
            "perito": perito.upper(),
            "peritoesp": peritoesp.upper(),
            "assisa": assisa.upper(),
            "assisb": assisb.upper(),
            "custas": custas,
            "advogado": advogado.upper(),
            "oabn": oabn,
            "email": email.lower(),
            "queixa": queixa.upper(),
            "cid10": cid10.upper(),
            "andamento": andamento.upper()
        }
        
        doc.render(contexto)
        
        bio = io.BytesIO()
        doc.save(bio)
        
        nome_arquivo = f"{nome.upper()} {processo} AT.docx"
        
        st.success("✅ Ficha gerada com sucesso! Os novos itens já foram salvos no seu histórico.")
        st.download_button(
            label="📥 Baixar Documento Preenchido",
            data=bio.getvalue(),
            file_name=nome_arquivo,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        st.error(f"Erro ao gerar o documento. Certifique-se de que o arquivo 'ficha.docx' está na mesma pasta. Erro: {e}")
