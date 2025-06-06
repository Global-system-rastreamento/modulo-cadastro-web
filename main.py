from src.spc_integration.spc_integration import *
from src.contract.contract_integration import *

import streamlit as st
from datetime import date, datetime 
import requests 
import io 
import docx
import unidecode
import os
import subprocess
import warnings

warnings.filterwarnings("ignore")


# --- Configuração da Página e CSS (Existente) ---
st.set_page_config(layout="wide", page_title="Cadastro de Clientes", page_icon=":house:")
custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    :root {
        --franchisee-main-color: #006535;
        --header-bg-color: #0b3747;
        --button-text-color: black;
        --input-bg-color: #f4f4f4;
        --input-border-color: #ced4da;
        --input-text-color: #555;
        --label-text-color: #666;
        --body-text-color: #212529;
        --section-title-color: #333;
        --streamlit-font-family: 'Roboto', Arial, sans-serif;
    }

    body, .stApp {
        font-family: var(--streamlit-font-family) !important;
        background-color: #EBEBEB;
        color: var(--body-text-color);
    }

    section[data-testid="stSidebar"] {
        display: none !important; /* OCULTA A SIDEBAR ORIGINAL */
    }

    /* --- Estilos para o Novo Cabeçalho no Topo da Página --- */
    .app-header-container {
        background-color: var(--header-bg-color) !important;
        padding: 15px 25px !important; /* Padding horizontal maior */
        color: var(--button-text-color) !important;
        margin-bottom: 1.5rem; /* Espaço antes do conteúdo principal */
        border-bottom: 3px solid var(--franchisee-main-color);
    }

    .app-header-container h5 { /* Saudação */
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: var(--button-text-color) !important;
        margin-bottom: 0.5rem;
        text-align: left;
    }

    .app-header-container .stImage img {
        background-color: #ececec;
        border-radius: 12px;
        padding: 10px;
        max-width: 150px; /* Limita tamanho da logo */
    }

    .app-header-container .stButton button,
    .app-header-container .stLinkButton a {
        border: 2px solid var(--button-text-color) !important;
        border-radius: 20px !important;
        padding: 6px 12px !important; /* Botões menores no header */
        font-weight: 700 !important;
        font-size: 0.85rem !important; /* Texto menor */
        text-align: center;
        margin-right: 8px; /* Espaçamento entre botões */
        margin-bottom: 8px; /* Espaçamento se quebrar linha */
        text-decoration: none;
        transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
        background-color: #7a7b43;
        color: var(--button-text-color) !important;
        display: inline-block; /* Para ficarem na mesma linha */
    }

    .app-header-container .stButton button:hover,
    .app-header-container .stLinkButton a:hover {
        background-color: #5e5f34 !important;
        transform: translateY(-1px);
    }
    
    .app-header-container .stButton button[kind="secondary"], /* Para botões específicos, se necessário */
    .app-header-container .stLinkButton a[href*="manutencoes"] { background-color: #a77a24 !important; }
    .app-header-container .stLinkButton a[href*="painel"] { background-color: #2f073b !important; }
    .app-header-container .stLinkButton a[href*="financeiro"] { background-color: #2344a4 !important; }
    /* etc. para outros botões com cores específicas */

    .header-section-title {
        font-size: 0.9rem !important;
        font-weight: bold !important;
        color: var(--button-text-color) !important;
        margin-top: 10px;
        margin-bottom: 5px;
        display: block;
        width: 100%; /* Ocupar toda a largura da coluna */
        text-align: left;
    }
    .header-logo-greet-col {
        display: flex;
        align-items: center; /* Alinha logo e saudação verticalmente */
        gap: 20px; /* Espaço entre logo e saudação */
    }


    /* --- Estilos do Conteúdo Principal (Restante da página) --- */
    .main .block-container {
        padding-top: 1rem !important; /* Reduzido pois o header agora tem margin-bottom */
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    .main .block-container h1 { /* st.title */
        font-family: var(--streamlit-font-family) !important;
        color: var(--section-title-color) !important;
        font-weight: bold !important;
        font-size: 1.9em !important;
        margin-bottom: 1rem;
    }

    .section-title {
        font-family: var(--streamlit-font-family) !important;
        font-size: 1.4em !important;
        font-weight: 700 !important;
        color: var(--section-title-color) !important;
        margin-top: 25px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    .section-title strong {
        color: var(--section-title-color) !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea,
    div[data-baseweb="select"] > div {
        font-family: var(--streamlit-font-family) !important;
        font-size: 0.9em !important;
        font-weight: 400 !important;
        color: var(--input-text-color) !important;
        background-color: var(--input-bg-color) !important;
        border: 1px solid var(--input-border-color) !important;
        border-radius: 4px !important;
        box-shadow: 0 1px 1px rgba(0,0,0,0.075) inset !important;
        height: 38px !important;
        box-sizing: border-box;
    }
    .stTextArea > div > div > textarea {
        height: auto !important;
        min-height: 76px;
    }
    div[data-baseweb="select"] input {
        color: var(--input-text-color) !important;
    }
    div[data-baseweb="select"] svg {
        fill: var(--input-text-color) !important;
    }

    .stTextInput > label,
    .stNumberInput > label,
    .stDateInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stCheckbox > label {
        font-family: var(--streamlit-font-family) !important;
        font-size: 1em !important;
        font-weight: 700 !important;
        color: var(--label-text-color) !important;
        margin-bottom: 5px !important;
        display: block !important;
        padding-left: 0px !important;
    }
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p {
        font-weight: 400 !important;
        color: var(--input-text-color) !important;
    }

    .stForm .stButton button[kind="primary"] {
        font-family: var(--streamlit-font-family) !important;
        background-color: var(--franchisee-main-color) !important;
        color: var(--button-text-color) !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        font-size: 1.05em !important;
        transition: background-color 0.2s ease;
    }
    .stForm .stButton button[kind="primary"]:hover {
        background-color: #004a27 !important;
    }

    .stCaption {
        font-family: var(--streamlit-font-family);
        font-size: 0.9em !important;
        color: #555 !important;
        margin-bottom: 1rem;
    }

    .tooltip-icon {
        font-family: 'Material Icons';
        font-size: 1.3rem;
        color: var(--label-text-color);
        margin-left: 8px;
        cursor: help;
        vertical-align: middle;
    }
    .tooltip-icon:hover {
        color: var(--franchisee-main-color);
    }

    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin-top: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

if 'dados_spc_json' not in st.session_state:
    st.session_state.dados_spc_json = None
if 'pdf_bytes_spc' not in st.session_state:
    st.session_state.pdf_bytes_spc = None
if 'pdf_filename_spc' not in st.session_state:
    st.session_state.pdf_filename_spc = "relatorio_spc.pdf"
if 'consulta_realizada_spc' not in st.session_state:
    st.session_state.consulta_realizada_spc = False
if "nome_operador" not in st.session_state:
    st.session_state["nome_operador"] = "Juan"


# --- Tooltips (Existente) ---
tooltip_info_basicas = "Preencha as informações básicas do Usuário, fique atento a campos obrigatórios (*)." 
tooltip_dados_acesso = "Dados para o seu cliente poder efetuar login no sistema." 
tooltip_funcionalidades = "Ative ou desative funcionalidades para este usuário." 
tooltip_financeiro = "Dados para controle financeiro do Usuário. Preencha todos os campos para ter relatórios e gráficos completos."
tooltip_spc = "Consulte a situação do CPF ou CNPJ do cliente nos serviços de proteção ao crédito. Os dados retornados podem pré-preencher o formulário abaixo."
tooltip_contrato = "Configure e gere o contrato de prestação de serviços e o manual do aplicativo para o cliente."
tooltip_dados_adicionais = "Preencha os dados adicionais do Usuário."

# --- Cabeçalho (Existente) ---
with st.container():
    st.markdown('<div class="app-header-container">', unsafe_allow_html=True)
    col1_header, _, col3_header = st.columns([0.25, 0.5, 0.25]) 
    with col1_header:
        st.markdown('<div class="header-logo-greet-col">', unsafe_allow_html=True)
        try:
            st.image("https://sisras-logos.s3.sa-east-1.amazonaws.com/globalsystem3.jpg", width=120) 
        except Exception:
            st.caption("Logo")
        now = datetime.now()
        greeting = "Bom Dia" if now.hour < 12 else "Boa Tarde" if now.hour < 18 else "Boa Noite"
        st.markdown(f"<h5>{greeting}!</h5>", unsafe_allow_html=True) 
        st.markdown('</div>', unsafe_allow_html=True)
    with col3_header:
        st.markdown('<div class="header-section-title">Navegação Principal</div>', unsafe_allow_html=True) 
        nav_cols = st.columns(2) 
        with nav_cols[0]:
            if st.button("🏠 Início", key="header_home_button", help="Ir para o menu principal", use_container_width=True): 
                st.toast("Navegando para Início (exemplo)") 
        with nav_cols[1]:
            if st.button("Sair", key="header_logout_button", help="Deslogar do sistema", use_container_width=True): 
                st.toast("Logout solicitado (funcionalidade de exemplo)") 
    st.markdown('</div>', unsafe_allow_html=True) 

# --- Conteúdo Principal (Existente) ---
st.caption("Navegação: Menu de Opções > Usuários > Adicionando Usuário") 
st.markdown("---") 
col_form_icon, col_form_title = st.columns([0.05, 0.95], gap="small")
with col_form_icon:
    st.write('') # Placeholder for icon if needed
    st.markdown("<span class='material-icons' style='font-size: 2.8rem; color: var(--section-title-color);'>group_add</span>", unsafe_allow_html=True) 
with col_form_title:
    st.title("Adicionando Usuário") 

# Formulário Principal
form_keys_defaults = {
    "form_ativo": True, "form_aviso_inadimplencia": False,
    "form_tipo_usuario": "Frotista", "form_pessoa_tipo": "Física",
    "form_nome": "", "form_responsavel": "", "form_endereco": "",
    "form_tel_celular": "", "form_tel_residencial": "", "form_tel_comercial": "",
    "form_email": "", "form_data_nascimento": None, "form_cpf_cnpj": "",
    "form_login": "", "form_senha": "", "form_confirmar_senha": "",
    "form_gestao_manutencao": True, "form_meu_veiculo_app": True, "form_zona_seguranca": True,
    "form_vbutton_gestao_motorista": False, "form_cerca_eletronica": True, "form_comandos": False,
    "form_listagem_eventos_alertas": True, "form_listagem_falha_sinal": True,
    "form_gestao_controle_carga": False, "form_i_button_suntech": False,
    "form_valor_mensalidade": 0.0, "form_dia_vencimento": 10, "form_obs_financeiro": ""
}
for key, default_value in form_keys_defaults.items():
    if key not in st.session_state: st.session_state[key] = default_value

# Contrato
contract_keys_defaults = {
    "contract_tipo_contrato_select": "GSM - SATELITAL", # 'PLANO2' ou 'GSM - SATELITAL'
    "contract_local_instalacao_input": "Luís Eduardo Magalhães - BA",
    "contract_data_instalacao_input": date.today(),
    "contract_operadora_input": "SATELITAL / VIVO",
    "contract_forma_cobranca_input": "BOLETO / ASSINATURA",
    "contract_atendente_input": "AUTOATENDIMENTO", # Idealmente nome do usuário logado
    "contract_valor_adesao_input": 0.0,
    "contract_valor_desinstalacao_input": 0.0, # No original, usa o mesmo da adesão
    "contract_valor_reinstalacao_input": 100.0, # Fixo no original
    "contract_valor_cobertura_input": 0.0,
    "contract_cliente_seguradora_checkbox": False, # Mapeia para 'Sim'/'Não'
    "contract_seguradora_input": "---",
    "contract_veiculo_financiado_checkbox": False, # Mapeia para 'Sim'/'Não'
    "contract_qtd_parcelas_input": "---",
    "contract_valor_parcelas_input": "---", # String, pois pode ser "---"
    "contract_data_ultima_parcela_input": None,
    "contract_emitir_manual_checkbox": True,
    "contract_tipo_manual_select": "Carro", # 'Carro', 'Moto', 'Frotista'
    "contract_placas_list": [], # Lista de dicionários para as placas
    "contract_pdf_bytes": None,
    "contract_pdf_filename": "contrato.pdf",
    "manual_pdf_bytes": None,
    "manual_pdf_filename": "manual.pdf"
}
for key, default_value in contract_keys_defaults.items():
    if key not in st.session_state: st.session_state[key] = default_value
# --- Fim da Inicialização ---

# --- Função para popular formulário ---
def popular_formulario_com_spc(dados_spc_json):
    if not dados_spc_json or not dados_spc_json.get('result', {}).get('return_object', {}):
        st.warning("Não há dados do SPC para preencher o formulário.")
        return

    resultado = dados_spc_json.get('result', {}).get('return_object', {}).get('resultado', {})
    consumidor = resultado.get('consumidor', {})
    consumidor_pf = consumidor.get('consumidorPessoaFisica', {})
    consumidor_pj = consumidor.get('consumidorPessoaJuridica', {})

    if consumidor_pf:
        st.session_state.form_pessoa_tipo = "Física"
        st.session_state.form_nome = unidecode.unidecode(consumidor_pf.get('nome', '')).upper()
        if resultado.get('restricao', False):
            st.session_state.form_nome = "I- " + st.session_state.form_nome

        st.session_state.form_responsavel = consumidor_pf.get('nome', '').upper()
        st.session_state.form_cpf_cnpj = formatar_documento_spc(consumidor_pf.get('cpf', {}), 'F')
        st.session_state.form_data_nascimento = formatar_data_spc(consumidor_pf.get('dataNascimento'))
        
        # Endereço PF
        end_pf = consumidor_pf.get('endereco', {})
        logradouro_pf = end_pf.get('logradouro', '')
        numero_pf = end_pf.get('numero', '')
        complemento_pf = end_pf.get('complemento', '')
        bairro_pf = end_pf.get('bairro', '')
        cidade_pf = end_pf.get('cidade', {}).get('nome', '')
        estado_pf = end_pf.get('cidade', {}).get('estado', {}).get('siglaUf', '')
        cep_pf = end_pf.get('cep', '')
        st.session_state.form_endereco = f"{logradouro_pf}, {numero_pf} {complemento_pf} - {bairro_pf}, {cidade_pf}/{estado_pf} - CEP: {cep_pf}".strip(", - ")

        # Telefone Celular PF (prioritário)
        tel_cel_pf = consumidor_pf.get('telefoneCelular', {})
        if tel_cel_pf.get('numeroDdd') and tel_cel_pf.get('numero'):
            st.session_state.form_tel_celular = formatar_telefone_spc(tel_cel_pf.get('numeroDdd'), tel_cel_pf.get('numero'))
        else: # Tenta outros telefones se celular não disponível
            tel_res_pf = consumidor_pf.get('telefoneResidencial', {})
            if tel_res_pf.get('numeroDdd') and tel_res_pf.get('numero'):
                 st.session_state.form_tel_residencial = formatar_telefone_spc(tel_res_pf.get('numeroDdd'), tel_res_pf.get('numero'))

        st.session_state.form_email = consumidor_pf.get('email', '')

    elif consumidor_pj:
        st.session_state.form_pessoa_tipo = "Jurídica" # Atualiza o seletor do formulário principal
        st.session_state.form_nome = unidecode.unidecode(consumidor_pj.get('razaoSocial', '')).upper()
        st.session_state.form_cpf_cnpj = formatar_documento_spc(consumidor_pj.get('cnpj', {}), 'J')
        st.session_state.form_data_nascimento = formatar_data_spc(consumidor_pj.get('dataAbertura')) 
        
        # Endereço PJ
        end_pj = consumidor_pj.get('endereco', {})
        logradouro_pj = end_pj.get('logradouro', '')
        numero_pj = end_pj.get('numero', '')
        complemento_pj = end_pj.get('complemento', '')
        bairro_pj = end_pj.get('bairro', '')
        cidade_pj = end_pj.get('cidade', {}).get('nome', '')
        estado_pj = end_pj.get('cidade', {}).get('estado', {}).get('siglaUf', '')
        cep_pj = end_pj.get('cep', '')
        st.session_state.form_endereco = f"{logradouro_pj}, {numero_pj} {complemento_pj} - {bairro_pj}, {cidade_pj}/{estado_pj} - CEP: {cep_pj}".strip(", - ")
        
        # Telefone PJ
        tel_pj = consumidor_pj.get('telefone', {})
        if tel_pj.get('numeroDdd') and tel_pj.get('numero'):
            st.session_state.form_tel_comercial = formatar_telefone_spc(tel_pj.get('numeroDdd'), tel_pj.get('numero')) # Ou celular se preferir

        st.session_state.form_email = consumidor_pj.get('email', '') # API SPC pode não ter email para PJ
        st.session_state.form_responsavel = consumidor_pj.get('nomeContato', '').upper()

    st.info("Formulário pré-preenchido com dados da consulta SPC. Revise e complete as informações.")

def cadastrar_cliente(dados_formulario, is_cnpj=False):

    url = "https://api.plataforma.app.br/user"

    headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://globalsystem.plataforma.app.br",
            "Referer": "https://globalsystem.plataforma.app.br/",
            "Sec-Ch-Ua": '"Not A(Brand";v="8", "Chromium";v="132", "Opera GX";v="117"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0",
            "X-Token": "c0f9e2df-d26b-11ef-9216-0e3d092b76f7",
            "Content-Type": "application/json"
        }
    
    data = {
                "sisras_user": {
                    "additionalData": {
                        k: v for k, v in dados_formulario['dados_adicionais'].items()
                    },
                    "ativo": 1,
                    "financ": 1,
                    "nivel": 2,
                    "admin": 0,
                    "pessoa": 2 if is_cnpj else 1,
                    "nome": unidecode.unidecode(dados_formulario["nome"]).upper(),
                    "respon": dados_formulario['responsavel'].upper(),
                    "endereco": dados_formulario['endereco'].upper(),
                    "fcel": dados_formulario['tel_celular'],
                    "fres": dados_formulario['tel_residencial'],
                    "fcom": dados_formulario['tel_comercial'],
                    "email": dados_formulario['email'],
                    "birthDate": "",
                    "cnpj": ''.join(list(filter(str.isdigit, dados_formulario["cpf_cnpj"]))),
                    "login": dados_formulario["login"],
                    "senha": dados_formulario["senha"],
                    "financMensalidade": int(int(dados_formulario['valor_mensalidade']) / 100),
                    "financDataVencimento": dados_formulario['dia_vencimento'],
                    "financObs": dados_formulario["obs_financeiro"],
                    "respfr": 2
                }
            }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        st.success("Cliente cadastrado com sucesso!")
    else:
        st.error("Erro ao cadastrar cliente. Verifique os dados e tente novamente.")
        st.write(response.json())
    


# Formulário Principal (adicionar chaves para todos os campos controláveis)
for key, default_value in form_keys_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# --- SPC integration ---
st.markdown("---")
st.markdown(f"""<h3 class="section-title">Consulta SPC/SERASA <span class="material-icons tooltip-icon" title="{tooltip_spc}">credit_score</span></h3>""", unsafe_allow_html=True)

with st.container(key="consulta_spc_form_widget", border=True): # Renomeado para evitar conflito com a key do form principal

    col_doc_spc, col_tipo_spc = st.columns(2)
    with col_doc_spc:
        documento_spc_input = st.text_input("Documento (CPF ou CNPJ):", placeholder="Digite o CPF ou CNPJ", key="documento_spc_text_input")
    with col_tipo_spc:
        tipo_pessoa_spc_radio = st.radio("Tipo de Pessoa:", ("Pessoa Física (CPF)", "Pessoa Jurídica (CNPJ)"), horizontal=True, key="tipo_pessoa_spc_radio_select")


    submit_button_spc = st.button("🔍 Consultar SPC/SERASA")

if submit_button_spc:
    st.session_state.dados_spc_json = None 
    st.session_state.pdf_bytes_spc = None
    st.session_state.consulta_realizada_spc = True

    doc_limpo = "".join(filter(str.isdigit, st.session_state.documento_spc_text_input))
    tipo_doc_api = 'F' if "Física" in st.session_state.tipo_pessoa_spc_radio_select else 'J'

    if not doc_limpo:
        st.error("Por favor, insira um número de documento válido.")
        st.session_state.consulta_realizada_spc = False
    else:
        with st.spinner("Consultando SPC/SERASA... Aguarde."):
            dados_consulta = consultar_spc_api(doc_limpo, tipo_doc_api)
        
        if dados_consulta:
            if dados_consulta.get('result', {}).get('error') == 'true':
                mensagem_erro_api = dados_consulta.get('result', {}).get('message', 'Erro desconhecido retornado pela API.')
                st.error(f"Erro na consulta SPC: {mensagem_erro_api}")
                st.session_state.dados_spc_json = None
            elif not dados_consulta.get('result', {}).get('return_object', {}).get('resultado'):
                 st.warning("A consulta foi realizada, mas não retornou dados de resultado para o documento informado.")
                 st.session_state.dados_spc_json = None 
            else:
                st.success("Consulta SPC/SERASA realizada com sucesso!")
                st.session_state.dados_spc_json = dados_consulta

                # Tenta popular o formulário principal
                popular_formulario_com_spc(st.session_state.dados_spc_json)

                markdown_report = gerar_relatorio_spc_markdown(st.session_state.dados_spc_json)
                if "## Erro" not in markdown_report: 
                    pdf_data, pdf_name = markdown_para_pdf_streamlit(markdown_report, f"relatorio_spc_{doc_limpo}.pdf")
                    if pdf_data:
                        st.session_state.pdf_bytes_spc = pdf_data
                        st.session_state.pdf_filename_spc = pdf_name
                    else:
                        st.error("Falha ao gerar o arquivo PDF para download.")
                else:
                    st.error("Falha ao gerar o conteúdo do relatório para o PDF.")
                    with st.expander("Detalhes do Erro na Geração do Relatório (Markdown)", expanded=False):
                        st.markdown(markdown_report)
        else:
            st.session_state.dados_spc_json = None

if st.session_state.consulta_realizada_spc:
    if st.session_state.dados_spc_json:
        if st.session_state.pdf_bytes_spc:
            st.download_button(
                label="📄 Baixar Relatório SPC em PDF",
                data=st.session_state.pdf_bytes_spc,
                file_name=st.session_state.pdf_filename_spc,
                mime="application/pdf",
                key="download_spc_pdf_button"
            )
        
        resultado_geral = st.session_state.dados_spc_json.get('result', {}).get('return_object', {}).get('resultado', {})
        if resultado_geral:
            restricao_status = "RESTRITO" if resultado_geral.get('restricao', False) else "REGULAR"
            st.info(f"Situação Geral do Documento (SPC): **{restricao_status}**")
    elif not submit_button_spc: 
        st.info("Nenhum dado de consulta SPC para exibir ou houve um erro na última tentativa.")

# --- Formulário Principal de Cadastro de Cliente (Existente) ---
with st.container(key="cadastro_cliente_form", border=True): 
    st.markdown(f"""<h3 class="section-title">Informações Básicas <span class="material-icons tooltip-icon" title="{tooltip_info_basicas}">help_outline</span></h3>""", unsafe_allow_html=True) 
    # ... (campos do formulário de cadastro usando st.session_state.form_*) ...
    cols_info1 = st.columns(5) 
    with cols_info1[0]: 
        st.checkbox("Ativo", key="form_ativo") 
    with cols_info1[1]: 
        st.checkbox("Aviso Inadimplência", value=st.session_state.form_aviso_inadimplencia, key="form_aviso_inadimplencia") 
    with cols_info1[2]: 
        tipo_usuario_options = ["Único", "Frotista", "Operador", "Master"] 
        st.selectbox("Tipo de Usuário:", tipo_usuario_options, index=tipo_usuario_options.index(st.session_state.form_tipo_usuario) if st.session_state.form_tipo_usuario in tipo_usuario_options else 1, key="form_tipo_usuario") 
    with cols_info1[3]: 
        pessoa_options = ["Física", "Jurídica"] 
        default_pessoa = st.session_state.tipo_pessoa_spc_radio_select.split(" ")[1]
        st.selectbox("Pessoa:", pessoa_options, index=pessoa_options.index(default_pessoa) if default_pessoa in pessoa_options else 0, key="form_pessoa_tipo") 
    with cols_info1[4]: 
        st.text_input("Nome:", placeholder="Nome completo ou Razão Social", value=unidecode.unidecode(st.session_state.form_nome), key="form_nome") 

    cols_info2 = st.columns(5) 
    with cols_info2[0]: 
        st.text_input("Responsável:", placeholder="Nome do responsável", value=st.session_state.form_responsavel, key="form_responsavel") 
    with cols_info2[1]: 
        st.text_input("Endereço:", placeholder="Rua, Número, Bairro, Cidade/UF - CEP", value=st.session_state.form_endereco, key="form_endereco") 
    with cols_info2[2]: 
        st.text_input("Tel. Celular:", placeholder="(XX) XXXXX-XXXX", value=st.session_state.form_tel_celular, key="form_tel_celular") 
    with cols_info2[3]: 
        st.text_input("Tel. Residencial:", placeholder="(XX) XXXX-XXXX", value=st.session_state.form_tel_residencial, key="form_tel_residencial") 
    with cols_info2[4]: 
        st.text_input("Tel. Comercial:", placeholder="(XX) XXXX-XXXX", value=st.session_state.form_tel_comercial, key="form_tel_comercial") 

    cols_info3 = st.columns(3) 
    with cols_info3[0]: 
        st.text_input("E-mail:", placeholder="exemplo@dominio.com", value=st.session_state.form_email, key="form_email") 
    with cols_info3[1]: 
        st.date_input("Data de nascimento:", value=st.session_state.form_data_nascimento, min_value=date(1900,1,1), format='DD/MM/YYYY', key="form_data_nascimento") 
    with cols_info3[2]: 
        cpf_cnpj_label = "CPF:" if st.session_state.form_pessoa_tipo == "Física" else "CNPJ:" 
        cpf_cnpj_placeholder = "000.000.000-00" if st.session_state.form_pessoa_tipo == "Física" else "00.000.000/0000-00" 
        st.text_input(cpf_cnpj_label, placeholder=cpf_cnpj_placeholder, value=st.session_state.form_cpf_cnpj, key="form_cpf_cnpj") 
    
    # ... (Restante dos campos: Dados de Acesso, Funcionalidades, Financeiro) ...
    st.markdown("---") 
    st.markdown(f"""<h3 class="section-title">Dados de Acesso <span class="material-icons tooltip-icon" title="{tooltip_dados_acesso}">vpn_key</span></h3>""", unsafe_allow_html=True) 
    cols_acesso = st.columns(3) 
    with cols_acesso[0]: 
        st.text_input("Login:", placeholder="Login desejado", value=st.session_state.form_login, key="form_login") 
    with cols_acesso[1]: 
        st.text_input("Senha:", placeholder="Senha forte", value=''.join(list(filter(str.isdigit, st.session_state.form_cpf_cnpj)))[:6], key="form_senha") 
    with cols_acesso[2]: 
        st.text_input("Repita a senha:", placeholder="Confirme a senha", value=''.join(list(filter(str.isdigit, st.session_state.form_cpf_cnpj)))[:6], key="form_confirmar_senha") 
    st.markdown("---")
    st.markdown(f"""<h3 class="section-title">Dados Adicionais <span class="material-icons tooltip-icon" title="{tooltip_financeiro}">view_list</span></h3>""", unsafe_allow_html=True)

    default_additional_data = {
        "pos_vendas": f"""Responsável: {st.session_state.form_responsavel}
Função: Proprietário
Telefone: {st.session_state.form_tel_celular}""",
    "financeiro": f"""BOLETO/NF {st.session_state.form_dia_vencimento}

E-mail: {st.session_state.form_email}

Whatsapp para boletos:
Telefone: {st.session_state.form_tel_celular}
Nome: {st.session_state.form_responsavel}""",    
    "negociacao": f"""Adesão: {0.00}
Mensalidade: {0.00}
Desinstalação: {0.00}
Reinstalação: 100,00""",    
    "falha_sinal": f"""Responsável: {st.session_state.form_responsavel}
Função: Proprietário
Telefone: {st.session_state.form_tel_celular}""",
    "pessoas_acesso": "."
    }

    for key, value in default_additional_data.items():
        cols_additional_data = st.columns([1, 0.05, 1])
        with cols_additional_data[0]:
            st.text_area(label="", label_visibility="hidden", value=f"{key.replace('_', ' ').upper()}:", key=f"form_additional_data_{key}", height=150)
        with cols_additional_data[2]:
            st.text_area(label="", label_visibility="hidden", value=value, key=f"form_additional_data_{key}_value", height=150)

    st.markdown("---") 
    st.markdown(f"""<h3 class="section-title"><strong>Funcionalidades</strong><span class="material-icons tooltip-icon" title="{tooltip_funcionalidades}">toggle_on</span></h3>""", unsafe_allow_html=True) 
    cols_func = st.columns(5) 
    with cols_func[0]: 
        st.checkbox("Habilitar Gestão de Manutenção", value=st.session_state.form_gestao_manutencao, key="form_gestao_manutencao") 
        st.checkbox("Gestão de Controle de Cargas", value=st.session_state.form_gestao_controle_carga, key="form_gestao_controle_carga") 
    with cols_func[1]: 
        st.checkbox("Habilitar App Meu Veículo", value=st.session_state.form_meu_veiculo_app, key="form_meu_veiculo_app") 
        st.checkbox("I-Button Suntech", value=st.session_state.form_i_button_suntech, key="form_i_button_suntech") 
    with cols_func[2]:
        st.checkbox("Habilitar Zona de Segurança", value=st.session_state.form_zona_seguranca, key="form_zona_seguranca") 
        st.checkbox("Habilitar Comandos", value=st.session_state.form_comandos, key="form_comandos") 
    with cols_func[3]:
        st.checkbox("V-Button Gestão de motorista", value=st.session_state.form_vbutton_gestao_motorista, key="form_vbutton_gestao_motorista") 
        st.checkbox("Listagem 'Eventos e Alertas'", value=st.session_state.form_listagem_eventos_alertas, key="form_listagem_eventos_alertas")
    with cols_func[4]:
        st.checkbox("Habilitar Cerca Eletrônica", value=st.session_state.form_cerca_eletronica, key="form_cerca_eletronica") 
        st.checkbox("Listagem 'Falha no Sinal'", value=st.session_state.form_listagem_falha_sinal, key="form_listagem_falha_sinal")

    st.markdown("---") 
    st.markdown(f"""<h3 class="section-title"><strong>Financeiro</strong><span class="material-icons tooltip-icon" title="{tooltip_dados_adicionais}">monetization_on</span></h3>""", unsafe_allow_html=True) 
    cols_financeiro = st.columns(3) 
    with cols_financeiro[0]: 
        st.number_input("Valor da mensalidade (base):", min_value=0.0, value=st.session_state.form_valor_mensalidade, format="%.2f", step=0.01, key="form_valor_mensalidade", help="Valor base da mensalidade. Será usado por veículo se não especificado individualmente.") 
    with cols_financeiro[1]: 
        st.write('')
        st.number_input("Dia de Vencimento:", min_value=1, max_value=31, value=st.session_state.form_dia_vencimento, step=1, format="%d", key="form_dia_vencimento") 
    with cols_financeiro[2]: 
        st.text_area("Observação (Financeiro Cliente):", placeholder="Detalhes financeiros do cliente...", value=f'Senha: {st.session_state.form_senha}. {st.session_state.nome_operador}', key="form_obs_financeiro") 

    st.markdown("<br>", unsafe_allow_html=True) 
    cols_submit_button_main = st.columns([0.6, 0.4]) 
    with cols_submit_button_main[1]:
        submitted_main_form = st.button("✔ Salvar Usuário", type="primary", use_container_width=True)

if submitted_main_form: 
    if st.session_state.form_senha != st.session_state.form_confirmar_senha: 
        st.error("As senhas não correspondem!")
    else: 
        dados_formulario_cliente = {key.replace("form_", ""): st.session_state[key] for key in form_keys_defaults if "additional_data" not in key}
        dados_adicionais = {}
        for k in st.session_state:
            k = str(k)
            if k.startswith("form_additional_data_") and not k.endswith("_value"):
                if k.replace("form_additional_data_", "") not in dados_adicionais:
                    dados_adicionais[k.replace("form_additional_data_", "")] = st.session_state[f"{k}_value"]

            
        dados_formulario_cliente['dados_adicionais'] = dados_adicionais

        st.success("Formulário 'Salvar usuário' submetido!") 

        cadastrar_cliente(dados_formulario_cliente, False if st.session_state.form_pessoa_tipo == "Física" else True)

# --- Seção de Geração de Contrato ---
st.markdown("---")
st.markdown(f"""<h3 class="section-title">📄 Gerar Contrato <span class="material-icons tooltip-icon" title="{tooltip_contrato}">article</span></h3>""", unsafe_allow_html=True)

with st.expander("Configurações do Contrato e Veículos", expanded=True):
    # --- Dados Gerais do Contrato ---
    st.subheader("Dados Gerais do Contrato")
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Tipo de Contrato:", ["GSM - SATELITAL", "PLANO2"], key="contract_tipo_contrato_select",
                     index=["GSM - SATELITAL", "PLANO2"].index(st.session_state.contract_tipo_contrato_select))
        st.text_input("Local da Instalação/Contrato:", key="contract_local_instalacao_input", value=st.session_state.contract_local_instalacao_input)
        st.date_input("Data de Instalação:", key="contract_data_instalacao_input", value=st.session_state.contract_data_instalacao_input, format="DD/MM/YYYY")
        st.number_input("Valor de Adesão (R$):", min_value=0.0, key="contract_valor_adesao_input", format="%.2f", value=st.session_state.contract_valor_adesao_input)
        st.session_state.contract_valor_desinstalacao_input = st.session_state.contract_valor_adesao_input # Conforme original
        # st.number_input("Valor de Desinstalação (R$):", min_value=0.0, key="contract_valor_desinstalacao_input", format="%.2f", value=st.session_state.contract_valor_desinstalacao_input)
        st.caption(f"Valor de Desinstalação: {formatar_valor_financeiro_contrato(st.session_state.contract_valor_desinstalacao_input)}")


    with c2:
        st.text_input("Operadora:", key="contract_operadora_input", value=st.session_state.contract_operadora_input)
        st.text_input("Forma de Cobrança:", key="contract_forma_cobranca_input", value=st.session_state.contract_forma_cobranca_input)
        st.text_input("Atendente:", key="contract_atendente_input", value=st.session_state.contract_atendente_input)
        st.number_input("Valor de Reinstalação (R$):", min_value=0.0, key="contract_valor_reinstalacao_input", format="%.2f", value=st.session_state.contract_valor_reinstalacao_input, disabled=True)


    # --- Dados do Seguro (Opcional) ---
    st.subheader("Dados do Seguro (Opcional)")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.checkbox("Cliente de Seguradora?", key="contract_cliente_seguradora_checkbox", value=st.session_state.contract_cliente_seguradora_checkbox)
        if st.session_state.contract_cliente_seguradora_checkbox:
            st.text_input("Nome da Seguradora:", key="contract_seguradora_input", value=st.session_state.contract_seguradora_input)
            st.number_input("Valor da Cobertura (R$):", min_value=0.0, key="contract_valor_cobertura_input", format="%.2f", value=st.session_state.contract_valor_cobertura_input)

    with s2:
        st.checkbox("Veículo Financiado?", key="contract_veiculo_financiado_checkbox", value=st.session_state.contract_veiculo_financiado_checkbox)
        if st.session_state.contract_veiculo_financiado_checkbox:
            st.text_input("Quantidade de Parcelas:", key="contract_qtd_parcelas_input", value=st.session_state.contract_qtd_parcelas_input)
    with s3:
        if st.session_state.contract_veiculo_financiado_checkbox:
            st.text_input("Valor das Parcelas (R$):", key="contract_valor_parcelas_input", value=st.session_state.contract_valor_parcelas_input)
            st.date_input("Data da Última Parcela:", key="contract_data_ultima_parcela_input", value=st.session_state.contract_data_ultima_parcela_input)

    # --- Veículos/Placas ---
    st.subheader("Veículos Contratados")

    if st.button("➕ Adicionar Veículo", key="add_vehicle_button_contract", help="Adiciona um novo veículo ao contrato"):
        # Adiciona um novo dicionário de placa à lista no session_state
        # O valor da mensalidade padrão pode vir do cadastro do cliente ou ser um valor fixo
        default_mensalidade = st.session_state.form_valor_mensalidade if st.session_state.form_valor_mensalidade > 0 else 60.0
        st.session_state.contract_placas_list.append({
            "id": len(st.session_state.contract_placas_list) + 1, # ID simples para a chave do widget
            "placa": "", "marca": "", "modelo": "", 
            "mensalidade": default_mensalidade,
            "rastreador": "GSM GPRS", # Padrão
            "plano_spc": "GSM" # Padrão para o contrato GSM
        })

    # Exibe os campos para cada placa na lista
    indices_para_remover = []
    for i, placa_data in enumerate(st.session_state.contract_placas_list):
        st.markdown(f"<div class='vehicle-column'>", unsafe_allow_html=True)
        st.markdown(f"##### Veículo {i+1}")
        cols_placa = st.columns([3,3,3,1])
        with cols_placa[0]:
            placa_data["placa"] = st.text_input(f"Placa", value=placa_data["placa"], key=f"contract_placa_{placa_data['id']}", placeholder="AAA-0000").upper()
            placa_data["marca"] = st.text_input(f"Marca", value=placa_data["marca"], key=f"contract_marca_{placa_data['id']}")
        with cols_placa[1]:
            placa_data["modelo"] = st.text_input(f"Modelo", value=placa_data["modelo"], key=f"contract_modelo_{placa_data['id']}")
            placa_data["mensalidade"] = st.number_input(f"Mensalidade (R$)", min_value=0.0, value=float(placa_data["mensalidade"]), key=f"contract_mensalidade_placa_{placa_data['id']}", format="%.2f")
        with cols_placa[2]:
            if st.session_state.contract_tipo_contrato_select == "PLANO2":
                placa_data["rastreador"] = "ONEBLOCK COM BLOQUEIO" # Fixo para PLANO2
                placa_data["plano_spc"] = "PGS"
                st.text_input(f"Tecnologia", value=placa_data["rastreador"], key=f"contract_rastreador_{placa_data['id']}", disabled=True)
                st.text_input(f"Plano (Contrato)", value=placa_data["plano_spc"], key=f"contract_plano_spc_{placa_data['id']}", disabled=True)
            else: # GSM - SATELITAL
                placa_data["rastreador"] = st.selectbox(f"Tecnologia", ["GSM GPRS", "SATELITAL"], index=["GSM GPRS", "SATELITAL"].index(placa_data["rastreador"]), key=f"contract_rastreador_{placa_data['id']}")
                placa_data["plano_spc"] = st.selectbox(f"Plano (Contrato)", ["GSM", "SATELITAL", "PGS"], index=["GSM", "SATELITAL", "PGS"].index(placa_data["plano_spc"]), key=f"contract_plano_spc_{placa_data['id']}")

        with cols_placa[3]:
            st.write("") # Espaçamento
            st.write("") # Espaçamento
            if st.button("🗑️", key=f"remove_placa_{placa_data['id']}", help="Remover este veículo"):
                indices_para_remover.append(i)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")


    # Remove os itens marcados (iterando de trás para frente para evitar problemas de índice)
    for index in sorted(indices_para_remover, reverse=True):
        st.session_state.contract_placas_list.pop(index)
        # Força re-execução para atualizar a UI sem os itens removidos
        st.rerun()


    # --- Ações do Contrato ---
    st.subheader("Ações")
    cols_actions_docx = st.columns(2)
    with cols_actions_docx[0]:
        if st.button("📋 Gerar e Baixar Contrato (.docx)", key="generate_contract_docx_button", help="Gera o contrato em formato DOCX", use_container_width=True, type="primary"):
            if not st.session_state.contract_placas_list:
                st.warning("Adicione pelo menos um veículo ao contrato.")
            else:
                with st.spinner("Gerando contrato DOCX..."):
                    # 1. Coletar todos os dados
                    dados_contrato_final = preparar_dados_para_template_contrato()
                    
                    # 2. Baixar/Carregar template DOCX
                    template_url_base = "https://api-data-automa-system-production.up.railway.app/download_doc/"
                    template_name = "template_contrato_plano2.docx" if dados_contrato_final['contract_type'] == "PLANO2" else "template_contrato_GSM.docx"
                    
                    doc_bytes = baixar_template_docx(template_url_base + template_name + "?path=docs")

                    if doc_bytes:
                        doc = docx.Document(io.BytesIO(doc_bytes))
                        
                        # 3. Preencher o template
                        preencher_template_contrato(doc, dados_contrato_final)
                        
                        # 4. Salvar em BytesIO para download
                        bio = io.BytesIO()
                        doc.save(bio)
                        st.session_state.contract_pdf_bytes = bio.getvalue() # Usando a mesma variável para DOCX por simplicidade
                        st.session_state.contract_pdf_filename = f"Contrato_{unidecode.unidecode(st.session_state.form_nome.replace(' ','_'))}_{date.today().strftime('%Y%m%d')}.docx"

                        # 5. Salvar localmente
                        st.session_state.temp_docx_path = f"temp_contract_{date.today().strftime('%Y%m%d%H%M%S')}.docx"
                        doc.save(st.session_state.temp_docx_path)

                        st.success("Contrato DOCX gerado!")
                    else:
                        st.error("Falha ao baixar o template do contrato.")
                        
    with cols_actions_docx[1]:
        if st.session_state.contract_pdf_bytes and st.session_state.contract_pdf_filename.endswith(".docx"):
            st.download_button(
                label="📥 Baixar Contrato DOCX",
                data=st.session_state.contract_pdf_bytes,
                file_name=st.session_state.contract_pdf_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="download_contract_docx_final_button",
                use_container_width=True
            )
    
    cols_actions_pdf = st.columns(2)

    with cols_actions_pdf[0]:
        
        # Geração de PDF (separada para clareza e porque pode falhar)
        if st.session_state.contract_pdf_bytes and st.session_state.contract_pdf_filename.endswith(".docx"):
            if st.button("📄 Gerar e Baixar Contrato (.pdf)", key="generate_contract_pdf_button", help="Converte o contrato gerado para PDF (requer Word/LibreOffice)", use_container_width=True):
                with st.spinner("Convertendo contrato para PDF... (Isso pode levar um momento)"):
                    try:
                        # Salvar o DOCX temporariamente para conversão
                        temp_pdf_path = st.session_state.temp_docx_path.replace(".docx", ".pdf")

                        subprocess.Popen(["libreoffice", "--headless", "--convert-to", "pdf", st.session_state.temp_docx_path])
                        with open(temp_pdf_path, "rb") as f_pdf:
                            st.session_state.contract_pdf_bytes_final = f_pdf.read()
                        
                        st.session_state.contract_pdf_filename_final = st.session_state.contract_pdf_filename.replace(".docx", ".pdf")
                        st.success("Contrato PDF gerado!")

                        # # Limpar arquivos temporários
                        if os.path.exists(st.session_state.temp_docx_path): os.remove(st.session_state.temp_docx_path)
                        if os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)

                    except Exception as e:
                        st.error(f"Erro ao converter para PDF: {e}. Verifique se o Microsoft Word ou LibreOffice está instalado e acessível.")
                        # Limpar arquivos temporários em caso de erro também
                        if 'temp_docx_path' in locals() and os.path.exists(st.session_state.temp_docx_path): os.remove(st.session_state.temp_docx_path)
                        if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)

    with cols_actions_pdf[1]:
        
        if st.session_state.get("contract_pdf_bytes_final") and st.session_state.get("contract_pdf_filename_final", "").endswith(".pdf"):
            st.download_button(
                label="📥 Baixar Contrato PDF",
                data=st.session_state.contract_pdf_bytes_final,
                file_name=st.session_state.contract_pdf_filename_final,
                mime="application/pdf",
                key="download_contract_pdf_final_button",
                use_container_width=True
            )


    # --- Geração do Manual ---
    st.subheader("Manual do Aplicativo")
    m1, m2 = st.columns(2)
    with m1:
        st.checkbox("Emitir Manual do APP?", key="contract_emitir_manual_checkbox", value=st.session_state.contract_emitir_manual_checkbox)
    if st.session_state.contract_emitir_manual_checkbox:
        with m2:
            st.selectbox("Tipo de Manual:", ["Carro", "Moto", "Frotista"], key="contract_tipo_manual_select",
                         index=["Carro", "Moto", "Frotista"].index(st.session_state.contract_tipo_manual_select))

    if st.session_state.contract_emitir_manual_checkbox:
        if st.button("🛠️ Gerar e Baixar Manual (.pdf)", key="generate_manual_button", use_container_width=True):
            with st.spinner("Gerando manual..."):
                # Lógica para gerar manual (similar ao contrato)
                # 1. Preparar dados para o manual
                dados_manual = {
                    "_LOGIN_": st.session_state.form_login,
                    "_SENHA_": st.session_state.form_senha, # Cuidado com a exposição de senhas
                    # Outros placeholders se houver no manual
                }
                # 2. Baixar template do manual
                template_manual_name = f"Manual App {st.session_state.contract_tipo_manual_select}.docx"
                manual_url_base = "https://api-data-automa-system-production.up.railway.app/download_doc/"
                
                manual_doc_bytes = baixar_template_docx(manual_url_base + template_manual_name.replace(" ", "%20") + "?path=docs")

                if manual_doc_bytes:
                    manual_doc = docx.Document(io.BytesIO(manual_doc_bytes))
                    # 3. Preencher template do manual
                    preencher_template_manual(manual_doc, dados_manual)
                    
                    # 4. Salvar DOCX em BytesIO
                    manual_bio_docx = io.BytesIO()
                    manual_doc.save(manual_bio_docx)
                    manual_docx_bytes_temp = manual_bio_docx.getvalue()

                    # 5. Converter para PDF
                    try:
                        temp_manual_docx_path = f"temp_manual_{date.today().strftime('%Y%m%d%H%M%S')}.docx"
                        temp_manual_pdf_path = temp_manual_docx_path.replace(".docx", ".pdf")

                        with open(temp_manual_docx_path, "wb") as f:
                            f.write(manual_docx_bytes_temp)
                        
                        subprocess.Popen(["libreoffice", "--headless", "--convert-to", "pdf", temp_manual_docx_path])

                        with open(temp_manual_pdf_path, "rb") as f_pdf:
                            st.session_state.manual_pdf_bytes = f_pdf.read()
                        
                        st.session_state.manual_pdf_filename = f"Manual_App_{st.session_state.contract_tipo_manual_select}_{unidecode.unidecode(st.session_state.form_nome.replace(' ','_'))}.pdf"
                        st.success("Manual PDF gerado!")
                        
                        if os.path.exists(temp_manual_docx_path): os.remove(temp_manual_docx_path)
                        if os.path.exists(temp_manual_pdf_path): os.remove(temp_manual_pdf_path)

                    except Exception as e:
                        st.error(f"Erro ao converter manual para PDF: {e}")
                        st.info("Oferecendo download do manual em formato DOCX.")
                        st.session_state.manual_pdf_bytes = manual_docx_bytes_temp # Salva o DOCX em vez do PDF
                        st.session_state.manual_pdf_filename = f"Manual_App_{st.session_state.contract_tipo_manual_select}_{unidecode.unidecode(st.session_state.form_nome.replace(' ','_'))}.docx"
                        if 'temp_manual_docx_path' in locals() and os.path.exists(temp_manual_docx_path): os.remove(temp_manual_docx_path)
                        if 'temp_manual_pdf_path' in locals() and os.path.exists(temp_manual_pdf_path): os.remove(temp_manual_pdf_path)
                else:
                    st.error(f"Falha ao baixar o template do manual: {template_manual_name}")


    if st.session_state.manual_pdf_bytes:
        mime_type = "application/pdf" if st.session_state.manual_pdf_filename.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        st.download_button(
            label=f"📥 Baixar Manual ({'.pdf' if mime_type == 'application/pdf' else '.docx'})",
            data=st.session_state.manual_pdf_bytes,
            file_name=st.session_state.manual_pdf_filename,
            mime=mime_type,
            key="download_manual_final_button",
            use_container_width=True
        )


# --- Footer (Existente) ---
st.markdown("---") 
st.caption("© Copyright 2021 - Todos os direitos reservados - Version 3.14.0 (Streamlit Replication)")

if 'its_first_run' not in st.session_state:
    st.session_state.its_first_run = True

if st.session_state.its_first_run:
    st.session_state.its_first_run = False
    st.rerun()