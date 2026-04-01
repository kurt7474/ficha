import streamlit as st
from docxtpl import DocxTemplate
import io
import re

# Configuração da página
st.set_page_config(page_title="Ficha Inteligente", layout="wide")

# Função para limpar todos os campos da interface
def limpar_dados():
    st.session_state.clear()

# Função para formatar o CPF no padrão brasileiro
def formatar_cpf(cpf):
    cpf_limpo = re.sub(r'\D', '', cpf) # Remove tudo que não for número
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf # Retorna como foi digitado se não tiver 11 números

st.title("Ficha Inteligente - Gerador de Documentos")

# Botão para limpar a ficha (fica no topo para facilitar)
col_titulo, col_botao = st.columns([4, 1])
with col_botao:
    st.button("🧹 Limpar Ficha", on_click=limpar_dados, use_container_width=True)

st.markdown("---")

# Criando abas para organizar o ambiente gráfico
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
        cargo = st.text_input("Profissão", key="cargo")
    with col2:
        filiacaomae = st.text_input("Filiação (Mãe)", key="filiacaomae")
        cpf = st.text_input("CPF nº (Digite apenas números)", key="cpf")
        telefone = st.text_input("Telefone", key="telefone")
    
    endereco = st.text_input("Endereço", key="endereco")

with aba_processo:
    col3, col4 = st.columns(2)
    with col3:
        processo = st.text_input("Nº do Processo", key="processo")
        advogado = st.text_input("Advogado", key="advogado")
        email = st.text_input("E-mail", key="email")
    with col4:
        comarca = st.text_input("Comarca", key="comarca")
        oabn = st.text_input("OAB Nº", key="oabn")
        custas = st.text_input("Juntada de Custas", key="custas")

with aba_peritos:
    perito = st.text_input("Perito Principal", key="perito")
    peritoesp = st.text_input("Perito Especialista", key="peritoesp")
    assisa = st.text_input("Assistente Técnico do Autor", key="assisa")
    assisb = st.text_input("Assistente Técnico do Réu", key="assisb")

with aba_medica:
    queixa = st.text_area("Queixa", key="queixa")
    cid10 = st.text_input("CID10 + Patologia", key="cid10")
    andamento = st.text_area("Andamento", key="andamento")

st.markdown("---")

# Botão para gerar o documento
if st.button("Gerar Ficha Inteligente", type="primary"):
    doc = DocxTemplate("ficha.docx")
    
    # Dicionário com o contexto preenchido na interface e as formatações
    # O .upper() deixa tudo em MAIÚSCULO e o .lower() em minúsculo
    contexto = {
        "nome": nome.upper(),
        "filiacaopai": filiacaopai.upper(),
        "filiacaomae": filiacaomae.upper(),
        "rg": f"{rg} - {orgao_emissor}" if rg else "", # Junta o RG com o Estado
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
    
    # Renderiza o documento com os dados formatados
    doc.render(contexto)
    
    # Salva em memória para o usuário baixar
    bio = io.BytesIO()
    doc.save(bio)
    
    # Cria o nome do arquivo: NOME + PROCESSO + AT.docx
    nome_arquivo = f"{nome.upper()} {processo} AT.docx"
    
    st.success("✅ Ficha gerada com sucesso com as novas formatações!")
    st.download_button(
        label="📥 Baixar Documento Preenchido",
        data=bio.getvalue(),
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
