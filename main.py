from app.config.design import *
apply_design()

from app.integrations.spc_integration import *
from app.integrations.contract_integration import *
from app.config.settings import *
from app.dialogs.report_dialog import report_dialog
from app.services.cep_search_service import *
from app.services.document_validator import *
from app.src.funcs import *
from app.services.login_service import login_screen
from app.services.google_sheets_service import *
from app.services.redis_service import *
from app.src.funcs import *
from app.src.manage_data_funcs import load_data, save_data

import streamlit as st
from datetime import date, datetime 
import pytz
import io 
import docx
import unidecode
import os
import subprocess
from streamlit_cookies_manager import EncryptedCookieManager
from dotenv import load_dotenv
import warnings
import glob


warnings.filterwarnings("ignore")
load_dotenv()

st.session_state.cookies = EncryptedCookieManager(
    password=os.environ.get("COOKIE_SECRET", "a_very_secret_password_12345"),
)

# --- Configurações Gerais ---
apply_general_settings()

# --- Inicialização de Variáveis de Estado ---
if 'dados_spc_json' not in st.session_state:
    st.session_state.dados_spc_json = None
if 'pdf_bytes_spc' not in st.session_state:
    st.session_state.pdf_bytes_spc = None
if 'pdf_filename_spc' not in st.session_state:
    st.session_state.pdf_filename_spc = "relatorio_spc.pdf"
if 'consulta_realizada_spc' not in st.session_state:
    st.session_state.consulta_realizada_spc = False
if "dados_cobranca_cep_flag" not in st.session_state:
    st.session_state["dados_cobranca_cep_flag"] = None
if "added_additional_data" not in st.session_state:
    st.session_state["added_additional_data"] = False
if "user_additional_data" not in st.session_state:
    st.session_state["user_additional_data"] = []
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

def popular_formulario_com_dados_usuario(user_data):
    """Preenche o formulário de cadastro com dados de um usuário da API."""
    if not user_data:
        st.warning("Não há dados do usuário para preencher o formulário.")
        return

    permission_map = {1: "Único", 2: "Frotista", 3: "Operador", 4: "Master"}

    # Preenche as informações básicas
    st.session_state.form_ativo = bool(user_data.get('ativo', 0))
    st.session_state.form_aviso_inadimplencia = bool(user_data.get('financ', 0))
    st.session_state.form_tipo_usuario = permission_map.get(user_data.get('nivel', 2), "Frotista")
    st.session_state.form_pessoa_tipo = "Jurídica" if user_data.get('pessoa') == 2 else "Física"
    st.session_state.form_nome = unidecode.unidecode(user_data.get('nome', '')).upper()
    st.session_state.form_responsavel = user_data.get('respon', '').upper()
    st.session_state.form_endereco = user_data.get('endereco', '').upper()
    st.session_state.form_tel_celular = user_data.get('fcel', '')
    st.session_state.form_tel_residencial = user_data.get('fres', '')
    st.session_state.form_email = user_data.get('email', '')
    st.session_state.form_data_nascimento = format_date_from_api(user_data.get('birth_date'))
    st.session_state.form_cpf_cnpj = user_data.get('cnpj', '')
    st.session_state.form_valor_mensalidade = float(user_data.get('financ_mensalidade', 0.0))

    if user_data.get('additional_data', {}):
        st.session_state.dados_cobranca_iss_retido_index = 0 if user_data.get('additional_data', {}).get('billing_info').get('nfe_iss_retido', '') else 1

    # Preenche os dados de acesso
    st.session_state.form_login = user_data.get('login', '')
    financ_obs = user_data.get('financ_obs', '')

    # Preenche o financeiro
    try:
        mensalidade = float(user_data.get('financ_mensalidade', 0.0))
    except (ValueError, TypeError):
        mensalidade = 0.0
    st.session_state.form_valor_mensalidade = mensalidade
    try:
        vencimento = int(user_data.get('financ_data_vencimento', 10))
    except (ValueError, TypeError):
        vencimento = 10
    st.session_state.form_dia_vencimento = vencimento
    st.session_state.form_obs_financeiro = financ_obs

    st.success("Dados do usuário carregados. Verifique e edite conforme necessário.")
   
# --- Fim das Funções Auxiliares ---

# --- Tooltips ---
tooltip_info_basicas = "Preencha as informações básicas do Usuário, fique atento a campos obrigatórios (*)." 
tooltip_dados_acesso = "Dados para o seu cliente poder efetuar login no sistema." 
tooltip_funcionalidades = "Ative ou desative funcionalidades para este usuário." 
tooltip_financeiro = "Dados para controle financeiro do Usuário. Preencha todos os campos para ter relatórios e gráficos completos."
tooltip_spc = "Consulte a situação do CPF ou CNPJ do cliente nos serviços de proteção ao crédito. Os dados retornados podem pré-preencher o formulário abaixo."
tooltip_contrato = "Configure e gere o contrato de prestação de serviços e o manual do aplicativo para o cliente."
tooltip_dados_cobranca = "Preencha os dados de cobrança do usuário, para emissão de boletos e assinaturas."
tooltip_dados_adicionais = "Preencha os dados adicionais do Usuário."

def page_cadastro_usuario():
    if "populate_form_client_data" in st.session_state and st.session_state.populate_form_client_data:
        popular_formulario_com_dados_usuario(st.session_state.user_to_edit_data)
        st.session_state.populate_form_client_data = False

    if "default_additional_data" not in st.session_state:
        st.session_state.default_additional_data = {}

        if st.session_state.user_to_edit_data:
            st.session_state.default_additional_data = st.session_state.user_to_edit_data.get('additional_data', {})

            if "billing_info" in st.session_state.default_additional_data:
                del st.session_state.default_additional_data['billing_info']

            if not st.session_state.default_additional_data:
                st.session_state.default_additional_data = {}

    st.markdown(get_cabecalho("Juan"), unsafe_allow_html=True)

    caption = "Adicionando" if not st.session_state.user_to_edit_data else "Editando"
    st.caption(f"Navegação: Menu de Opções > Usuários > {caption} Usuário") 
    st.markdown("---") 
    col_form_icon, col_form_title = st.columns([0.05, 0.95], gap="small")
    with col_form_icon:
        st.write('')
        st.markdown("<span class='material-icons' style='font-size: 2.8rem; color: var(--section-title-color);'>group_add</span>", unsafe_allow_html=True) 
    with col_form_title:
        st.title(f"{caption} Usuário")


    # --- SPC integration ---
    st.markdown("---")
    st.markdown(f"""<h3 class="section-title">Consulta SPC/SERASA <span class="material-icons tooltip-icon" title="{tooltip_spc}">credit_score</span></h3>""", unsafe_allow_html=True)

    with st.container(key="consulta_spc_form_widget"): # Renomeado para evitar conflito com a key do form principal
        col_doc_spc, col_tipo_spc = st.columns(2)
        with col_doc_spc:
            st.text_input("Documento (CPF ou CNPJ):", placeholder="Digite o CPF ou CNPJ", key="documento_spc_text_input")
        with col_tipo_spc:
            st.radio("Tipo de Pessoa:", ("Pessoa Física (CPF)", "Pessoa Jurídica (CNPJ)"), horizontal=True, key="tipo_pessoa_spc_radio_select")


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
                response = consultar_spc_api(doc_limpo, tipo_doc_api)
                dados_consulta = None
                if response:
                    if response.status_code == 500:
                        st.error("Houve um erro no servidor do SPC/SERASA. Pode ser devido a um documento INCORRETO informado. tente novamente ou contate o suporte.")

                    else:
                        try:
                            dados_consulta = response.json()
                        except json.JSONDecodeError:
                            st.error("Houve um erro ao decodificar a resposta JSON do SPC/SERASA. tente novamente ou contate o suporte.")

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

    # --- Formulário Principal de Cadastro de Cliente ---
    with st.container(key="cadastro_cliente_form"): 
        st.markdown(f"""<h3 class="section-title">Informações Básicas <span class="material-icons tooltip-icon" title="{tooltip_info_basicas}">help_outline</span></h3>""", unsafe_allow_html=True) 
        # ... (campos do formulário de cadastro usando st.session_state.form_*) ...
        cols_info1 = st.columns(5) 
        with cols_info1[0]: 
            st.checkbox("Ativo", key="form_ativo", value=True) 
        with cols_info1[1]: 
            st.checkbox("Aviso Inadimplência", key="form_aviso_inadimplencia") 
        with cols_info1[2]: 
            tipo_usuario_options = ["Único", "Frotista", "Operador", "Master"]
            st.selectbox("Tipo de Usuário:", tipo_usuario_options, index=tipo_usuario_options.index(st.session_state.form_tipo_usuario) if st.session_state.form_tipo_usuario in tipo_usuario_options else 1, key="form_tipo_usuario") 
        with cols_info1[3]: 
            pessoa_options = ["Física", "Jurídica"] 
            default_pessoa = st.session_state.tipo_pessoa_spc_radio_select.split(" ")[1]
            st.selectbox("Pessoa:", pessoa_options, index=pessoa_options.index(default_pessoa) if default_pessoa in pessoa_options else 0, key="form_pessoa_tipo") 
        with cols_info1[4]: 
            st.text_input("Nome:", placeholder="Nome completo ou Razão Social", key="form_nome") 

        cols_info2 = st.columns(5) 
        with cols_info2[0]:

            if not st.session_state.user_to_edit_data and st.session_state.form_pessoa_tipo == "Física":
                st.session_state.form_responsavel = st.session_state.form_nome.split("- ")[-1]

            st.text_input("Responsável:", placeholder="Nome do responsável", key="form_responsavel") 
        with cols_info2[1]: 
            st.text_input("Endereço:", placeholder="Rua, Número, Bairro, Cidade/UF - CEP", key="form_endereco") 
        with cols_info2[2]: 
            st.text_input("Tel. Celular:", placeholder="(XX) XXXXX-XXXX", key="form_tel_celular") 
        with cols_info2[3]: 
            st.text_input("Tel. Residencial:", placeholder="(XX) XXXX-XXXX", key="form_tel_residencial") 
        with cols_info2[4]: 
            st.text_input("Tel. Comercial:", placeholder="(XX) XXXX-XXXX", key="form_tel_comercial") 

        cols_info3 = st.columns(3) 
        with cols_info3[0]: 
            st.text_input("E-mail:", placeholder="exemplo@dominio.com", key="form_email") 
        with cols_info3[1]: 
            st.date_input("Data de nascimento:", format='DD/MM/YYYY', key="form_data_nascimento") 
        with cols_info3[2]: 

            def_document = ''
            if not st.session_state.user_to_edit_data and st.session_state.documento_spc_text_input:
                def_document = st.session_state.documento_spc_text_input

            cpf_cnpj_label = "CPF:" if st.session_state.form_pessoa_tipo == "Física" else "CNPJ:" 
            cpf_cnpj_placeholder = "000.000.000-00" if st.session_state.form_pessoa_tipo == "Física" else "00.000.000/0000-00" 
            st.text_input(cpf_cnpj_label, placeholder=cpf_cnpj_placeholder, key="form_cpf_cnpj", value=def_document) 
        
        # ... (Restante dos campos: Dados de Acesso, Funcionalidades, Financeiro) ...
        st.markdown("---") 
        st.markdown(f"""<h3 class="section-title">Dados de Acesso <span class="material-icons tooltip-icon" title="{tooltip_dados_acesso}">vpn_key</span></h3>""", unsafe_allow_html=True) 
        cols_acesso = st.columns(3) 
        with cols_acesso[0]:
            def_login = ""

            if st.session_state.user_to_edit_data:
                def_login = st.session_state.user_to_edit_data.get('login', '')
            elif st.session_state.form_nome:
                def_login = st.session_state.form_nome.split("- ")[-1].split(" ")[0].lower()
            st.text_input("Login:", placeholder="Login desejado", key="form_login", value=def_login) 
        
        default_senha = ''.join(list(filter(str.isdigit, st.session_state.form_cpf_cnpj)))[:6] if not st.session_state.user_to_edit_data else ''
        with cols_acesso[1]: 
            st.text_input("Senha:", placeholder="Senha forte", value=default_senha, key="form_senha") 
        with cols_acesso[2]: 
            st.text_input("Repita a senha:", placeholder="Confirme a senha", value=default_senha, key="form_confirmar_senha") 
        st.markdown("---")
        st.markdown(f"""<h3 class="section-title">Dados Adicionais <span class="material-icons tooltip-icon" title="{tooltip_financeiro}">view_list</span></h3>""", unsafe_allow_html=True)

        def add_additional_data_row():
            number_identifier = 0
            all_keys = list(st.session_state.default_additional_data.keys()) if st.session_state.default_additional_data else list({}.keys())
            keys_adc = [k for k in all_keys if k.startswith("chave_adicional")]
            if keys_adc:
                number_identifier = max([int(k.split("_")[-1]) for k in keys_adc]) + 1
            
            st.session_state.user_additional_data.append({f"chave_adicional_{number_identifier}": ""})

        if not st.session_state.user_to_edit_data:
            st.session_state.default_additional_data = {
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
    "pessoas_acesso_liberado": "."
                }
        
        if st.session_state.user_additional_data:
            for user_add in st.session_state.user_additional_data:
                for key, value in user_add.items():
                    st.session_state.default_additional_data[key] = value

        for key, value in st.session_state.default_additional_data.items() if st.session_state.user_additional_data else {}.items():
            if not st.session_state.user_additional_data:
                cols_additional_data = st.columns([1, 0.05, 1])
            else:
                cols_additional_data = st.columns([0.9, 0.05, 0.9, 0.15])

            with cols_additional_data[0]:
                st.text_area(label="", label_visibility="hidden", value=f"{key.replace('_', ' ').upper()}:", key=f"form_additional_data_{key}", height=150)
            with cols_additional_data[2]:
                st.text_area(label="", label_visibility="hidden", value=value, key=f"form_additional_data_{key}_value", height=150)
            if st.session_state.user_additional_data and key not in list(st.session_state.default_additional_data.keys())[:5]:
                with cols_additional_data[3]:
                    st.write(" ")
                    st.write(" ")
                    st.write(" ")

                    def remove_additional_data_row(key):
                        for user_add in st.session_state.user_additional_data:
                            if key in user_add:
                                st.session_state.user_additional_data.remove(user_add)

                        if len(st.session_state.default_additional_data) == 5:
                            st.session_state.added_additional_data = False

                    st.button("Remover", key=f"form_remover_additional_data_{key}", on_click=lambda key=key: remove_additional_data_row(key))
    
        _, col_add_dados_adc, _ = st.columns([1.15, 0.5, 1])
        with col_add_dados_adc:
            st.button("Adicionar Dados Adicionais", key="form_adicionar_dados_adicionais", on_click=add_additional_data_row)

        st.markdown("---") 
        st.markdown(f"""<h3 class="section-title"><strong>Funcionalidades</strong><span class="material-icons tooltip-icon" title="{tooltip_funcionalidades}">toggle_on</span></h3>""", unsafe_allow_html=True) 
        cols_func = st.columns(5) 
        with cols_func[0]: 
            st.checkbox("Habilitar Gestão de Manutenção", key="form_gestao_manutencao", value=True) 
            st.checkbox("Gestão de Controle de Cargas", key="form_gestao_controle_carga") 
        with cols_func[1]: 
            st.checkbox("Habilitar App Meu Veículo", key="form_meu_veiculo_app", value=True) 
            st.checkbox("I-Button Suntech", key="form_i_button_suntech") 
        with cols_func[2]:
            st.checkbox("Habilitar Zona de Segurança", key="form_zona_seguranca", value=True) 
            st.checkbox("Habilitar Comandos", key="form_comandos") 
        with cols_func[3]:
            st.checkbox("V-Button Gestão de motorista", key="form_vbutton_gestao_motorista") 
            st.checkbox("Listagem 'Eventos e Alertas'", key="form_listagem_eventos_alertas", value=True)
        with cols_func[4]:
            st.checkbox("Habilitar Cerca Eletrônica", key="form_cerca_eletronica", value=True) 
            st.checkbox("Listagem 'Falha no Sinal'", key="form_listagem_falha_sinal", value=True)

        st.markdown("---") 
        st.markdown(f"""<h3 class="section-title"><strong>Financeiro</strong><span class="material-icons tooltip-icon" title="{tooltip_dados_adicionais}">monetization_on</span></h3>""", unsafe_allow_html=True) 
        cols_financeiro = st.columns(3) 
        with cols_financeiro[0]: 
            st.number_input("Valor da mensalidade (base):", min_value=0.0, format="%.2f", step=0.01, key="form_valor_mensalidade", help="Valor base da mensalidade. Será usado por veículo se não especificado individualmente.") 
        with cols_financeiro[1]: 
            st.write('')
            st.number_input("Dia de Vencimento:", min_value=1, max_value=31, step=1, format="%d", key="form_dia_vencimento") 
        with cols_financeiro[2]: 
            st.text_area("Observação (Financeiro Cliente):", placeholder="Detalhes financeiros do cliente...", value=f'Senha: {st.session_state.form_senha}. {st.session_state.username}', key="form_obs_financeiro") 

        st.markdown("<br>", unsafe_allow_html=True) 
        cols_submit_button_main = st.columns([0.6, 0.4]) 
        with cols_submit_button_main[1]:
            submitted_form = st.button("✔ Salvar Usuário", type="primary", use_container_width=True)

    if submitted_form: 
        if st.session_state.form_senha != st.session_state.form_confirmar_senha: 
            st.error("As senhas não correspondem!")
        else:                
            if validate_form_cadastro():
                data_on_sheet = get_data_from_sheet("CODIGOS")
                if not data_on_sheet:
                    st.error("Não foi possível obter os dados do Google Sheets. Por favor, tente novamente mais tarde.")
                    return
                
                else:
                  
                  if not st.session_state.user_to_edit_id and not st.session_state.user_to_edit_data:
                    with safe_redis_lock("save_data_to_sheet"):
                        with st.spinner("Salvando dados no Google Sheets..."):

                            first_row = data_on_sheet[0]

                            name_client = first_row.get("CLIENTE", "")

                            new_date = datetime.now(pytz.timezone("America/Sao_Paulo")).date()

                            new_date_str = new_date.strftime("%d/%m/%Y")

                            older_cod = name_client.split("-")[0]

                            if not older_cod.isdigit():
                                st.error("O código do cliente não é um número válido. Verifique a planilha e tente novamente.")
                                return
                            
                            new_cod = str(int(older_cod) + 1)

                            new_name_client = f"{new_cod}- {st.session_state.form_nome}".upper()

                            st.session_state.form_nome_modified = new_name_client

                            data = [new_date_str, new_name_client, st.session_state.username.upper()]

                            update_planilha(data, "CODIGOS")


                dados_formulario_cliente = {key.replace("form_", ""): st.session_state[key] for key in form_keys_defaults if "additional_data" not in key}

                if "form_nome_modified" in st.session_state and st.session_state.form_nome_modified:
                    dados_formulario_cliente["nome"] = st.session_state.form_nome_modified

                dados_adicionais = {}
                for k in st.session_state:
                    k = str(k)
                    if k.startswith("form_additional_data_") and not k.endswith("_value"):
                        if k.replace("form_additional_data_", "") not in dados_adicionais:
                            dados_adicionais[k.replace("form_additional_data_", "").replace("_", ' ').upper()] = st.session_state[f"{k}_value"]
                
                order_dados = ["POS VENDAS", "FINANCEIRO", "NEGOCIACAO", "FALHA SINAL", "PESSOAS ACESSO LIBERADO", "*"]    

                dados_adicionais_in_order = {}
                for order in order_dados:
                    for key, value in dados_adicionais.items():
                        if order == key:
                            dados_adicionais_in_order[key] = value

                        elif order == "*":
                            dados_adicionais_in_order[key] = value

                        

                dados_formulario_cliente['dados_adicionais'] = dados_adicionais_in_order

                st.toast("Formulário 'Cadastro de Usuário' submetido!") 

                if st.session_state.user_to_edit_id and st.session_state.user_to_edit_data:
                    st.session_state.user_to_edit_data = get_user_data_by_id(st.session_state.user_to_edit_id)
                    response = atualizar_cadastro(dados_formulario_cliente, False if st.session_state.form_pessoa_tipo == "Física" else True, update_data=st.session_state.user_to_edit_data)
                    print(response)
                    if response:
                        st.session_state.user_to_edit_data = response
                        add_funcoes()
                        send_single_telegram_message(f"Atualização de cadastro de usuário: {st.session_state.user_to_edit_id} - {st.session_state.form_nome} - {st.session_state.form_cpf_cnpj}, pelo usuario {st.session_state.username}.", "-4875656287")
                
                else:
                    response = cadastrar_cliente(dados_formulario_cliente, False if st.session_state.form_pessoa_tipo == "Física" else True)
                    if response:
                        st.session_state.user_to_edit_id = response.get("id", "")
                        st.session_state.user_to_edit_data = response
                        add_funcoes()
                        send_single_telegram_message(f"Novo cadastro de usuário: {st.session_state.user_to_edit_id} - {st.session_state.form_nome} - {st.session_state.form_cpf_cnpj}, pelo usuario {st.session_state.username}.", "-4875656287")

                    else:
                        delete_row_from_sheet("CODIGOS", 2)
                        st.info("Retirado cliente da planilha")
            
            else:
                st.toast("Formulário inválido!")

    st.markdown("---")
    st.markdown(f"""<h3 class="section-title">🧾 Dados para emissão de cobrança <span class="material-icons tooltip-icon" title="{tooltip_dados_cobranca}">article</span></h3>""", unsafe_allow_html=True)
    
    billing_info = {}
    if st.session_state.user_to_edit_data:
        add_d = st.session_state.user_to_edit_data.get("additional_data", {})
        if add_d:
            billing_info = add_d.get("billing_info", {})

    with st.container():
        # --- Seção de Informações Pessoais ---
        col1, col2 = st.columns([3, 2]) # Colunas para Nome e Telefone
        with col1:
            def_nome_dc = billing_info.get("name", "") if billing_info else st.session_state.form_nome.split("- ")[-1]
            st.text_input("Nome", key="dados_cobranca_nome", value=def_nome_dc)
        with col2:
            def_telefone_dc = billing_info.get("phone", "") if billing_info else st.session_state.form_tel_celular
            st.text_input("Telefone Principal", key="dados_cobranca_telefone", value=def_telefone_dc)

        col1, col2 = st.columns([2, 3]) # Colunas para Tipo de Pessoa e Documento
        with col1:
            form_pessoa_tipo = st.session_state.form_pessoa_tipo
            def_doc_dc = billing_info.get("cpfcnpj", "")
            if def_telefone_dc and len(def_telefone_dc) == 11:
                form_pessoa_tipo = "Física"

            pessoa_index = 0 if form_pessoa_tipo == "Física" else 1
            st.radio("Tipo de Pessoa:", ["Pessoa Física (CPF)", "Pessoa Jurídica (CNPJ)"], key="dados_cobranca_tipo_pessoa", horizontal=True, index=pessoa_index)
        with col2:
            def_doc_dc = billing_info.get("cpfcnpj", "") if billing_info else st.session_state.form_cpf_cnpj
            st.text_input("Documento:", key="dados_cobranca_documento", placeholder="Digite o CPF ou CNPJ", value=def_doc_dc)

        col1, col2 = st.columns(2) # Colunas para Data de Nascimento e E-mail
        with col1:
            def_data_nasc_dc = billing_info.get("birth_date", "") if billing_info else st.session_state.form_data_nascimento
            if def_data_nasc_dc and not isinstance(def_data_nasc_dc, date):
                def_data_nasc_dc = datetime.strptime(def_data_nasc_dc, "%Y-%m-%d").date()

            st.date_input("Data de nascimento", key="dados_cobranca_data_nasc", format='DD/MM/YYYY', value=def_data_nasc_dc if def_data_nasc_dc else None)
        with col2:
            def_email_dc = billing_info.get("email", "") if billing_info else st.session_state.form_email
            st.text_input("E-mail", key="dados_cobranca_email",  value=def_email_dc)
        
        def_observacao_dc = billing_info.get("observation", "") if billing_info else ""
        st.text_area("Observação:", key="dados_cobranca_obs", help="Este campo é opcional.", value=def_observacao_dc)
        
        # --- Seção de Endereço ---
        col1, col2 = st.columns([1, 2])
        with col1:
            def_cep_dc = billing_info.get("cep", "") if billing_info else ""
            new_cep = st.text_input("CEP", key="dados_cobranca_cep", value=def_cep_dc)
            if new_cep and new_cep != st.session_state.dados_cobranca_cep_flag and new_cep != def_cep_dc:
                cep_search = search_cep(st.session_state.dados_cobranca_cep)

                if cep_search:
                   st.session_state.dados_cobranca_endereco = cep_search['logradouro']
                   st.session_state.dados_cobranca_bairro = cep_search['bairro']
                   st.session_state.dados_cobranca_cidade = cep_search['localidade']
                   st.session_state.dados_cobranca_estado = cep_search['uf']
                   st.session_state.dados_cobranca_ibge_code = cep_search['ibge']
                   st.session_state.dados_cobranca_cep_flag = new_cep
                   st.rerun()
        with col2:
            def_nfe_config_dc = billing_info.get("nfe_issuance_automation_type", "") if billing_info else ""
            config_nfe_index = None
            if def_nfe_config_dc:
                config_nfe_index = 0 if def_nfe_config_dc == "manual_issuance" else 1 if def_nfe_config_dc == "on_billing" else 2 if def_nfe_config_dc == "on_settlement" else None
            st.selectbox(
                "Configuração NFS-e",
                ["Emitir NF manualmente", "Emitir NF no faturamento", "Emitir NF na liquidação"],
                key="dados_cobranca_nfse",
                index=config_nfe_index,
            )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            def_endereco_dc = billing_info.get("address", "") if billing_info else ""
            st.text_input("Endereço", key="dados_cobranca_endereco", value=def_endereco_dc)
        with col2:
            def_numero_dc = billing_info.get("address_number", "") if billing_info else ""
            st.text_input("Número", key="dados_cobranca_numero", value=def_numero_dc)
        
        def_complemento_dc = billing_info.get("address_complement", "") if billing_info else ""
        st.text_input("Complemento", key="dados_cobranca_complemento", value=def_complemento_dc)

        col1, col2, col3 = st.columns(3)
        with col1:
            def_bairro_dc = billing_info.get("neighborhood", "") if billing_info else ""
            st.text_input("Bairro", key="dados_cobranca_bairro", value=def_bairro_dc)
        with col2:
            def_cidade_dc = billing_info.get("city", "") if billing_info else ""
            st.text_input("Cidade", key="dados_cobranca_cidade", value=def_cidade_dc)
        with col3:
            def_estado_dc = billing_info.get("state", "") if billing_info else ""
            st.text_input("Estado", key="dados_cobranca_estado", value=def_estado_dc)

        st.write("")
        btn_cols = st.columns([1, 1, 7])
        
        with btn_cols[0]:
            if st.button("Salvar"):
                if not validate_dados_cobranca():
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                elif not st.session_state.user_to_edit_id:
                    st.error("Por favor, selecione um usuário para editar. Ou cadastre um primeiro.")
                else:
                    response = save_dados_cobranca()
                    if response:
                        send_single_telegram_message(f"Dados de cobrança atualizados para o usuário {st.session_state.user_to_edit_id}, {st.session_state.user_to_edit_data.get('name', '')}.", "-4875656287")

        
        with btn_cols[1]:
            def_index_iss = 1
            if 'dados_cobranca_iss_retido_index' in st.session_state:
                def_index_iss = st.session_state.dados_cobranca_iss_retido_index

            st.radio("ISS Retido", key="dados_cobranca_iss_retido", options=["Sim", "Não"], index=def_index_iss, horizontal=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('---')
    st.markdown(f"""<h3 class="section-title">📄 Gerar Contrato <span class="material-icons tooltip-icon" title="{tooltip_contrato}">article</span></h3>""", unsafe_allow_html=True)

    with st.container():
        # --- Dados Gerais do Contrato ---
        st.subheader("Dados Gerais do Contrato")
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Tipo de Contrato:", ["GSM - SATELITAL", "PLANO2"], key="contract_tipo_contrato_select",
                        index=["GSM - SATELITAL", "PLANO2"].index(st.session_state.contract_tipo_contrato_select))
            locals_options = ["Luís Eduardo Magalhães - BA", "Sorriso - MT", "Barreiras - BA", "Outro"]
            st.selectbox("Local da Instalação/Contrato:", key="contract_local_instalacao_input", options=locals_options)

            if st.session_state.contract_local_instalacao_input == "Outro":
                st.text_input("Local da Instalação/Contrato:", key="contract_local_instalacao_outro_input")

            st.date_input("Data de Instalação:", key="contract_data_instalacao_input", format="DD/MM/YYYY")
            st.number_input("Valor de Adesão (R$):", min_value=0.0, key="contract_valor_adesao_input", format="%.2f")
            st.session_state.contract_valor_desinstalacao_input = st.session_state.contract_valor_adesao_input # Conforme original
            st.caption(f"Valor de Desinstalação: {formatar_valor_financeiro_contrato(st.session_state.contract_valor_desinstalacao_input)}")


        with c2:
            st.text_input("Operadora:", key="contract_operadora_input", value="VIVO / SATELITAL")
            st.text_input("Forma de Cobrança:", key="contract_forma_cobranca_input", value="BOLETO / ASSINATURA")
            st.text_input("Atendente:", key="contract_atendente_input", value=st.session_state.username)
            st.number_input("Valor de Reinstalação (R$):", min_value=0.0, key="contract_valor_reinstalacao_input", value=100.0, format="%.2f", disabled=True)
            if st.session_state.contract_tipo_contrato_select == "PLANO2":
                st.number_input("Valor da Cobertura (R$):", min_value=0.0, key="contract_valor_cobertura_input", format="%.2f")


        # --- Dados do Seguro (Opcional) ---
        st.subheader("Dados do Seguro (Opcional)")
        s1, s2, s3 = st.columns(3)
        with s1:
            cliente_seguradora = st.checkbox("Cliente de Seguradora?", key="contract_cliente_seguradora_checkbox")
            if cliente_seguradora:
                st.text_input("Nome da Seguradora:", key="contract_seguradora_input")

        with s2:
            veiculo_financiado = st.checkbox("Veículo Financiado?", key="contract_veiculo_financiado_checkbox")
            if st.session_state.contract_veiculo_financiado_checkbox or veiculo_financiado:
                st.text_input("Quantidade de Parcelas:", key="contract_qtd_parcelas_input")
        with s3:
            if veiculo_financiado:
                st.text_input("Valor das Parcelas (R$):", key="contract_valor_parcelas_input")
                st.date_input("Data da Última Parcela:", key="contract_data_ultima_parcela_input", format="DD/MM/YYYY")

        # --- Veículos/Placas ---
        st.subheader("Veículos Contratados")

        if st.button("➕ Adicionar Veículo", key="add_vehicle_button_contract", help="Adiciona um novo veículo ao contrato"):
            default_mensalidade = st.session_state.form_valor_mensalidade if st.session_state.form_valor_mensalidade > 0 else 60.0
            st.session_state.contract_placas_list.append({
                "id": len(st.session_state.contract_placas_list) + 1, # ID simples para a chave do widget
                "placa": "", "marca": "", "modelo": "", 
                "mensalidade": default_mensalidade,
                "rastreador": "GSM GPRS",
                "plano_spc": "GSM"
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
                    options_technology = ["GSM GPRS", "SATELITAL", "GSM GPRS/SATELITAL"]
                    placa_data["rastreador"] = st.selectbox(f"Tecnologia", options_technology, index=options_technology.index(placa_data["rastreador"]), key=f"contract_rastreador_{placa_data['id']}")
                    placa_data["plano_spc"] = st.selectbox(f"Plano (Contrato)", ["GSM", "SATELITAL", "PGS"], index=["GSM", "SATELITAL", "PGS"].index(placa_data["plano_spc"]), key=f"contract_plano_spc_{placa_data['id']}")

            with cols_placa[3]:
                st.write("")
                st.write("")
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
            if st.button("📋 Gerar e Baixar Contrato (.docx)", key="generate_contract_docx_button", help="Gera o contrato em formato DOCX"):
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
                            for file in glob.glob("temp_contract_*.docx"):
                                os.remove(file)

                            st.session_state.temp_docx_path = f"temp_contract_{date.today().strftime('%Y%m%d%H%M%S')}.docx"
                            doc.save(st.session_state.temp_docx_path)

                            st.toast("Contrato DOCX gerado!")
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
                if st.button("📄 Gerar e Baixar Contrato (.pdf)", key="generate_contract_pdf_button", help="Converte o contrato gerado para PDF (requer Word/LibreOffice)"):
                    with st.spinner("Convertendo contrato para PDF... (Isso pode levar um momento)"):
                        try:
                            # Salvar o DOCX temporariamente para conversão
                            temp_pdf_path = st.session_state.temp_docx_path.replace(".docx", ".pdf")

                            subprocess.Popen(["libreoffice", "--headless", "--convert-to", "pdf", st.session_state.temp_docx_path]).wait()
                            with open(temp_pdf_path, "rb") as f_pdf:
                                st.session_state.contract_pdf_bytes_final = f_pdf.read()
                            
                            st.session_state.contract_pdf_filename_final = st.session_state.contract_pdf_filename.replace(".docx", ".pdf")
                            st.toast("Contrato PDF gerado!")

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
            st.checkbox("Emitir Manual do APP?", key="contract_emitir_manual_checkbox", value=True)
        if st.session_state.contract_emitir_manual_checkbox:
            with m2:
                st.selectbox("Tipo de Manual:", ["Carro", "Moto", "Frotista"], key="contract_tipo_manual_select",
                            index=["Carro", "Moto", "Frotista"].index(st.session_state.contract_tipo_manual_select))

        if st.session_state.contract_emitir_manual_checkbox:
            if st.button("🛠️ Gerar e Baixar Manual (.pdf)", key="generate_manual_button"):
                with st.spinner("Gerando manual..."):
                    # Lógica para gerar manual (similar ao contrato)
                    # 1. Preparar dados para o manual
                    dados_manual = {
                        "_NOME_USUARIO_": st.session_state.form_login,
                        "_SENHA_USUARIO_": st.session_state.form_senha,
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
                            
                            subprocess.Popen(["libreoffice", "--headless", "--convert-to", "pdf", temp_manual_docx_path]).wait()

                            with open(temp_manual_pdf_path, "rb") as f_pdf:
                                st.session_state.manual_pdf_bytes = f_pdf.read()
                            
                            st.session_state.manual_pdf_filename = f"Manual_App_{st.session_state.contract_tipo_manual_select}_{unidecode.unidecode(st.session_state.form_nome.replace(' ','_'))}.pdf"
                            st.toast("Manual PDF gerado!")
                            
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


    # --- Footer ---
    st.markdown("---") 
    st.caption("© Copyright 2021 - Todos os direitos reservados - Version 3.14.0 (Streamlit Replication)")

    if 'its_first_run' not in st.session_state:
        st.session_state.its_first_run = False
        st.rerun()


def inicio():

    if "actual_search" in st.session_state and st.session_state.actual_search:
        st.session_state.search_query_key = st.session_state.actual_search
        st.session_state.actual_search = ""
    
    if "show_report" in st.session_state and st.session_state.show_report:
        report_dialog()
        st.session_state.show_report = False

    st.markdown(get_cabecalho(st.session_state.username), unsafe_allow_html=True)

    # --- Main Content ---
    st.caption("Navegação: Menu de Opções > Usuários")

    # --- Cabeçalho da Seção de Gerenciamento ---
    st.markdown('<div class="client-management-header">', unsafe_allow_html=True)
    left, right = st.columns([0.8, 0.2])
    with left:
        st.markdown('<div class="left-side">', unsafe_allow_html=True)
        
        # Título
        st.markdown("""
            <div class="title-block">
                <span class="material-icons" style="font-size: 2.5rem;">group</span>
                <h2><strong>Usuários</strong></h2>
            </div>
        """, unsafe_allow_html=True)

        # Filtros
        cols = st.columns([6, 1])
        with cols[0]:
            search_query = st.text_input("Pesquisar...", label_visibility="collapsed", placeholder="🔎 Pesquisar...", key="search_query_key")
        with cols[1]:
            st.write(" ")
            st.write(" ")

            st.checkbox("Carregar dados de veículos", key="show_vehicles_checkbox")

        status_options = {"Todos": "", "Ativo": "1", "Inativo": "0"}
        status_filter = st.selectbox("Status", options=status_options.keys(), label_visibility="collapsed")
        
        financ_options = {"Todos": "", "Sim": "1", "Não": "0"}
        financ_filter = st.selectbox("Aviso Financ.", options=financ_options.keys(), label_visibility="collapsed")

        st.markdown('</div>', unsafe_allow_html=True)
    
    # Placeholder para contagem total, será preenchido após a chamada da API
    total_clients_placeholder = right.empty()
    st.markdown('</div>', unsafe_allow_html=True)
    
    button_cols = st.columns(5)

    with button_cols[0]:
        if st.button("🔄 Atualizar", key="update_button"):
            get_client_data.clear() 
            get_vehicles_for_client.clear()
            get_all_vehicle_data.clear()
            st.rerun()
    
    with button_cols[1]:
        if st.button("Adicionar Usuário", key="add_user_button"):
            st.session_state.page_to_show = "cadastro"
            st.session_state.user_additional_data = None
            st.rerun()
            
    st.markdown("---")

    # --- Lógica de Paginação ---
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    if search_query:
        st.session_state.current_page = 1
    
    if search_query:
        # --- Chamada da API com filtros ---
        client_data = get_client_data(
            page=st.session_state.current_page,
            search_term=search_query,
            ativo_filter=1 if status_options.get(status_filter, "") == "Ativo" else 0 if status_options.get(status_filter, "") == "Inativo" else None,
            financ_filter=1 if financ_options.get(financ_filter, "") == "Sim" else 0 if financ_options.get(financ_filter, "") == "Não" else None
        )

        if client_data:
            total_items = client_data.get('total_items_length', 0)
            items_per_page = client_data.get('items_per_page', 50)
            total_pages = (total_items + items_per_page - 1) // items_per_page # Arredonda para cima

            total_clients_placeholder.markdown(f"<div style='text-align: right;'>Total de <strong>{total_items}</strong> usuários</div>", unsafe_allow_html=True)

            # Controles de Paginação
            st.markdown('<div class="pagination-container">', unsafe_allow_html=True)
            
            navigation_cols = st.columns([1, 0.5, 0.09, 0.2, 0.4, 0.5, 1])

            with navigation_cols[1]:
                
                # Botão para página anterior
                if st.button('◀ Anterior', disabled=(st.session_state.current_page <= 1)):
                    st.session_state.current_page -= 1
                    st.rerun()

            with navigation_cols[3]:
                st.write(f"{st.session_state.current_page} de {total_pages}")

            with navigation_cols[5]:
                # Botão para próxima página
                if st.button('Próxima ▶', disabled=(st.session_state.current_page >= total_pages)):
                    st.session_state.current_page += 1
                    st.rerun()  
                
            st.markdown('</div>', unsafe_allow_html=True)

            # --- Tabela de Clientes com HTML ---
            table_html = """
            <table class="client-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Usuário</th>
                        <th>CPF/CNPJ</th>
                        <th>E-mail</th>
                        <th>Tipo</th>
                        <th>Telefone Celular</th>
                        <th>Ativo</th>
                        <th>Aviso Financ.</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            # Mapeamento do nível de permissão para o tipo de usuário
            permission_map = {1: "Único", 2: "Frotista", 3: "Operador", 4: "Master"}

            for i, user in enumerate(client_data.get('data', [])):
                index = ((st.session_state.current_page - 1) * items_per_page) + i + 1
                user_id = user.get('id', '')
                user_name = user.get('name', '---')
                user_cpf_cnpj = user.get('cpf_cnpj', '---')
                user_email = user.get('email', '---')
                user_phone = user.get('phone_number', '---')
                user_type = permission_map.get(user.get('permission_level'), 'Desconhecido')
                
                vehicles = None
                vehicle_list_str = ''
                if st.session_state.show_vehicles_checkbox:
                    vehicles = get_vehicles_for_client(user_id)
                    if not vehicles:
                        vehicles = []

                    vehicle_list_str = ','.join([f"{v.get('license_plate', '---')}/{v.get('id', '')}" for v in vehicles])


                # Ícone para status 'ativo'
                is_active = user.get('active', 0)
                active_icon = '<span class="material-icons active-icon" title="Ativo">check_box</span>' if is_active else '<span class="material-icons inactive-icon" title="Inativo">disabled_by_default</span>'
                
                # Ícone para 'aviso financeiro'
                financial_status = user.get('financial_status', 0)
                financ_icon = '<span class="material-icons active-icon" title="Com Aviso">check_box</span>' if financial_status else '<span class="material-icons" title="Sem Aviso">check_box_outline_blank</span>'

                # Link para a página de edição (exemplo)
                edit_link = f"/?user_id={user_id}"

                table_html += f"""
                <tr>
                    <td>{index}</td>
                    <td style="display: flex; justify-content: space-between; align-items: center;">
                        <a href="{edit_link}" target="_blank">{user_name}</a>
                        <span><a href="https://globalsystem.plataforma.app.br/financeiro/cliente/{user_id}" target="_blank">Acessar Financeiro</a></span>
                    </td>
                    <td>{user_cpf_cnpj}</td>
                    <td>{user_email}</td>
                    <td>{user_type}</td>
                    <td>{user_phone}</td>
                    <td style="text-align: center;">{active_icon}</td>
                    <td style="text-align: center;">{financ_icon}</td>
                    <td class="action-icons">
                        <div class="actions-wrapper">
                            <a href="https://globalsystem.plataforma.app.br/panel/rastreadores?userId={user_id}" target="_blank" class="tooltip-container">
                                <span class='material-icons' style='font-size: 1rem; color: black;'>menu</span>
                                <span class="tooltip">Clique para gerenciar seus rastreadores</span>
                            </a>
                            <a href="https://globalsystem.plataforma.app.br/panel/rastreadores/cadastro?userId={user_id}" target="_blank" class="tooltip-container">
                                <span class='material-icons' style='font-size: 1rem; color: black;'>add</span>
                                <span class="tooltip">Clique para adicionar um novo rastreador a esse usuário.</span>
                            </a>
                            <a href="/?actual_search={search_query}&report_client_name={user_name}&report_client_id={user_id}{f'&all_vehicles={vehicle_list_str}' if vehicle_list_str else ''}" target="_self" class="tooltip-container">
                                <span class='material-icons' style='font-size: 1rem; color: black;'>description</span>
                                <span class="tooltip">Clique para criar um relatório de quilometragem e infrações para esse cliente.</span>
                            </a>
                        </div>
                    </td>
                </tr>
                """
        

            # --- NOVA SEÇÃO PARA VEÍCULOS ---
                table_html += f"""
                <tr>
                    <td colspan="9" class="details-cell">
                """

                if vehicles:
                    # Cria o <details> que permite expandir/recolher
                    table_html += f"""
                    <details>
                        <summary>Ver/Ocultar {len(vehicles)} Veículo(s)</summary>
                        <table class="vehicle-table">
                            <thead>
                                <tr>
                                    <th>Placa</th>
                                    <th>Marca</th>
                                    <th>Modelo</th>
                                    <th>IMEI</th>
                                    <th>Fabricante</th>
                                    <th>Grupo</th>
                                    <th>Número do Chip</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    
                    # Itera sobre os veículos retornados pela API
                    for vehicle in vehicles:
                        all_vehicle_data = get_all_vehicle_data(vehicle.get('id', ''))
                        placa = vehicle.get('license_plate', '---')
                        marca = vehicle.get('brand', '---')
                        modelo = vehicle.get('model', '---')
                        fabricante = vehicle.get('manufacturer_name', '---')
                        imei = vehicle.get('imei', '---')
                        chip_number = vehicle.get('chip_number', '---')
                        vehicle_id = vehicle.get('id', '---')
                        
                        table_html += f"""
                                <tr>
                                    <td><a href="https://globalsystem.plataforma.app.br/web/individual/{vehicle_id}">{placa}</a></td>
                                    <td>{marca}</td>
                                    <td>{modelo}</td>
                                    <td><a href="https://globalsystem.plataforma.app.br/panel/rastreadores/cadastro/{vehicle_id}">{imei}</a></td>
                                    <td>{fabricante}</td>
                                    <td>{all_vehicle_data.get('groups')}</td>
                                    <td>{chip_number}</td>
                                </tr>
                        """

                    table_html += """
                            </tbody>
                        </table>
                    </details>
                    """
                elif vehicles is not None:
                    # Se não houver veículos, pode exibir uma mensagem simples
                    table_html += """
                        <div style="padding: 5px; font-style: italic; color: #888;">&nbsp;&nbsp;Este cliente não possui veículos cadastrados.</div>
                    """

                table_html += "</td></tr>"
                # ###############################################################
                # ## FIM DA NOVA SEÇÃO                                         ##
                # ###############################################################

            table_html += "</tbody></table>"
            st.markdown(table_html.replace('\n', ''), unsafe_allow_html=True)
        else:
            st.warning("Não foi possível carregar os dados dos clientes ou não há clientes para os filtros selecionados.")
    
    st.markdown("---")
    st.caption("© Copyright 2021 - Todos os direitos reservados - Version 3.14.0 (Streamlit Replication)")

def main():
    if not login_screen(st.session_state.cookies):
        return
    # Inicializa o estado de navegação
    if "page_to_show" not in st.session_state:
        st.session_state.page_to_show = "inicio"
    if "user_to_edit_id" not in st.session_state:
        st.session_state.user_to_edit_id = None
    if "loaded_user_id" not in st.session_state:
        st.session_state.loaded_user_id = None
    if "user_to_edit_data" not in st.session_state:
        st.session_state.user_to_edit_data = None
    if "event_register_data" not in st.session_state:
        st.session_state.event_register_data = load_data()

    # Verifica os parâmetros da URL para navegar para a página de edição
    query_params = st.query_params

    if "logout" in query_params:
        try:
            if st.session_state.cookies.ready():
                # Deletar cookies
                st.session_state.cookies.pop("auth_token")
                st.session_state.cookies.pop("username")

                print(f"Cookies de autenticação: {st.session_state.cookies}")
                st.query_params.clear()

        except Exception as e:
            print(f"Erro ao deletar cookies: {e}")
        
        else:
            st.session_state.logged_out = True
            st.rerun()

    if "go_home" in query_params:
        st.session_state.page_to_show = "inicio"
        st.query_params.clear()

    if "report_client_name" in query_params:
        st.session_state.client_name = query_params.get("report_client_name")
        st.session_state.client_id = query_params.get("report_client_id")
        st.session_state.all_vehicles = query_params.get("all_vehicles", "")
        st.session_state.show_report = True
        st.session_state.actual_search = query_params.get("actual_search", "")

        st.query_params.clear()

    if "user_id" in query_params:
        user_id_from_url = query_params.get("user_id")
        # Evita recarregamentos desnecessários se o ID já estiver sendo editado
        if st.session_state.user_to_edit_id != user_id_from_url:
            st.session_state.page_to_show = "cadastro"
            st.session_state.user_to_edit_id = user_id_from_url
            st.query_params.clear() # Limpa o parâmetro da URL
            st.rerun()

    # Renderiza a página com base no estado
    if st.session_state.page_to_show == "cadastro":
        # Carrega os dados do usuário se um ID estiver definido e ainda não foi carregado
        if st.session_state.user_to_edit_id is not None and st.session_state.loaded_user_id != st.session_state.user_to_edit_id:
            with st.spinner(f"Carregando dados do usuário ID: {st.session_state.user_to_edit_id}..."):
                st.session_state.user_to_edit_data = get_user_data_by_id(st.session_state.user_to_edit_id)
                if st.session_state.user_to_edit_data:
                    popular_formulario_com_dados_usuario(st.session_state.user_to_edit_data)
                    st.session_state.loaded_user_id = st.session_state.user_to_edit_id
                else:
                    st.error(f"Não foi possível carregar os dados para o usuário ID: {st.session_state.user_to_edit_id}.")
                    st.session_state.page_to_show = "inicio" # Volta para a lista em caso de erro
                    st.rerun()
        
        page_cadastro_usuario()
    else:
        # Garante que o modo de edição seja desativado ao voltar para a home
        st.session_state.user_to_edit_id = None
        st.session_state.loaded_user_id = None
        st.session_state.user_to_edit_data = None
        inicio()

if __name__ == "__main__":
    main()
