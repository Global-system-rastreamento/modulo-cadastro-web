import unidecode
from datetime import datetime
from app.services.document_validator import validar_cpf, validar_cnpj
import streamlit as st
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from time import sleep


X_TOKEN_API = 'c0f9e2df-d26b-11ef-9216-0e3d092b76f7'
API_BASE_URL = 'https://api.plataforma.app.br'

COMMON_API_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://globalsystem.plataforma.app.br',
    'priority': 'u=1, i',
    'referer': 'https://globalsystem.plataforma.app.br/',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Opera GX";v="118", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0',
    'x-token': X_TOKEN_API
}

def atualizar_cadastro(dados_formulario, is_cnpj=False, update_data=None):
    """
    Atualiza o cadastro do cliente com base nos dados fornecidos.
    """

    url = f"https://api.plataforma.app.br/user/{update_data.get('id', '')}"

    niveis = ["Único", "Frotista", "Operador", "Master"]

    data = update_data.copy()

    data["sisras_user"]["additionalData"] = {
        k: v for k, v in dados_formulario['dados_adicionais'].items()
    }

    data["sisras_user"]["ativo"] = dados_formulario['ativo']
    data["sisras_user"]["financ"] = 1 if dados_formulario['aviso_inadimplencia'] else 0
    data["sisras_user"]["nivel"] = niveis.index(dados_formulario['tipo_usuario']) + 1
    data["sisras_user"]["nome"] = unidecode.unidecode(dados_formulario["nome"]).upper()
    data["sisras_user"]["respon"] = dados_formulario['responsavel'].upper()
    data["sisras_user"]["endereco"] = dados_formulario['endereco'].upper()
    data["sisras_user"]["fcel"] = dados_formulario['tel_celular']
    data["sisras_user"]["fres"] = dados_formulario['tel_residencial']
    data["sisras_user"]["fcom"] = dados_formulario['tel_comercial']
    data["sisras_user"]["email"] = dados_formulario['email']
    data["sisras_user"]["birthDate"] = dados_formulario['data_nascimento'].strftime('%Y-%m-%d')
    data["sisras_user"]["cnpj"] = ''.join(list(filter(str.isdigit, dados_formulario["cpf_cnpj"])))
    data["sisras_user"]["login"] = dados_formulario["login"]
    data["sisras_user"]["senha"] = dados_formulario["senha"]
    data["sisras_user"]["financMensalidade"] = dados_formulario['valor_mensalidade']
    data["sisras_user"]["financDataVencimento"] = dados_formulario['dia_vencimento']
    data["sisras_user"]["financObs"] = dados_formulario["obs_financeiro"]
    data["sisras_user"]["pessoa"] = 2 if is_cnpj else 1
    data["sisras_user"]["respfr"] = 2
    
    response = requests.put(url, headers=COMMON_API_HEADERS, json=data)
    if response.status_code == 200:
        st.success("Cadastro atualizado com sucesso!")
    else:
        st.error("Erro ao atualizar o cadastro. Por favor, tente novamente.")
        st.error(response.text)

def cadastrar_cliente(dados_formulario=None, is_cnpj=False):

    url = "https://api.plataforma.app.br/user"
    
    niveis = ["Único", "Frotista", "Operador", "Master"]
    data = {
        "sisras_user": {
            "additionalData": {
                k: v for k, v in dados_formulario['dados_adicionais'].items()
            },
            "ativo": dados_formulario['ativo'],
            "financ": 1 if dados_formulario['aviso_inadimplencia'] else 0,
            "nivel": niveis.index(dados_formulario['tipo_usuario']) + 1,
            "admin": 0,
            "pessoa": 2 if is_cnpj else 1,
            "nome": unidecode.unidecode(dados_formulario["nome"]).upper(),
            "respon": dados_formulario['responsavel'].upper(),
            "endereco": dados_formulario['endereco'].upper(),
            "fcel": dados_formulario['tel_celular'],
            "fres": dados_formulario['tel_residencial'],
            "fcom": dados_formulario['tel_comercial'],
            "email": dados_formulario['email'],
            "birthDate": dados_formulario['data_nascimento'].strftime('%Y-%m-%d') if dados_formulario['data_nascimento'] else None,
            "cnpj": ''.join(list(filter(str.isdigit, dados_formulario["cpf_cnpj"]))),
            "login": dados_formulario["login"],
            "senha": dados_formulario["senha"],
            "financMensalidade": dados_formulario['valor_mensalidade'],
            "financDataVencimento": dados_formulario['dia_vencimento'],
            "financObs": dados_formulario["obs_financeiro"],
            "respfr": 2
        }
    }
        
        
    response = requests.post(url, headers=COMMON_API_HEADERS, json=data)
    if response.status_code == 201:
        st.success("Cliente cadastrado com sucesso!")
        st.session_state.populate_form_client_data = True
        return response.json()
    elif response.status_code == 403 and "franchisee" in response.text:
        st.error("Já existe um usuário com esse LOGIN, tente novamente.")
    else:
        st.error("Erro ao cadastrar cliente. Verifique os dados e tente novamente.")
        st.error(response.json())

def add_funcoes():
    if st.session_state.user_to_edit_id:
        features = {
            "electronic-fence": 1 if st.session_state.form_cerca_eletronica else 0,
            "meu-veiculo-app": 1 if st.session_state.form_meu_veiculo_app else 0,
            "maintenances": 1 if st.session_state.form_gestao_manutencao else 0,
            "vbutton/driver-manager": 1 if st.session_state.form_vbutton_gestao_motorista else 0,
            "suntech/i-button": 1 if st.session_state.form_i_button_suntech else 0,
            "security-zone": 1 if st.session_state.form_zona_seguranca else 0,
            "events-and-alerts": 1 if st.session_state.form_listagem_eventos_alertas else 0,
            "signal-failure": 1 if st.session_state.form_listagem_falha_sinal else 0,
            "infringements": 0,
            "commands": 1 if st.session_state.form_comandos else 0,
            "cargo-manager": 1 if st.session_state.form_gestao_controle_carga else 0
        }
        URLS_PUT = [
            f"https://api.plataforma.app.br/manager/user/{st.session_state.user_to_edit_id}/feature/{feature}?enable={features[feature]}"
            for feature in features.keys()
        ]

        # Função para executar a requisição PUT
        def send_put_request(url):
            response = requests.put(url, headers=COMMON_API_HEADERS)
            if response.status_code != 200:
                print(f"Erro ao enviar PUT para {url}: {response.text}")
            return response.status_code, response.text

        # Executa as requisições em paralelo
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(send_put_request, URLS_PUT))

        if all(result[0] == 200 for result in results):
            st.toast("Todas as mudanças de funcionalidades foram concluídas.")
        else:
            st.error("Algumas mudanças de funcionalidades falharam. Por favor, tente novamente.")
    else:
        st.error("O cadastro do cliente atual falhou ao ser criado ou não foi carregado corretamente.")

def save_dados_cobranca():

    if st.session_state.user_to_edit_id and st.session_state.user_to_edit_data:
        url = f"https://api.plataforma.app.br/user/{st.session_state.user_to_edit_id}"
        payload = {"sisras_user": st.session_state.user_to_edit_data.copy()}
    
        if "additional_data" in payload["sisras_user"]:
            payload["sisras_user"]["additionalData"] = payload["sisras_user"].pop("additional_data")

        if "birth_date" in payload["sisras_user"]:
            payload["sisras_user"]["birthDate"] = payload["sisras_user"].pop("birth_date")

        payload_copy = copy.deepcopy(payload)
        for k in payload["sisras_user"].keys():
            if k not in ["additionalData", "birthDate", "nome", "login", "email"]:
                del payload_copy["sisras_user"][k]

        payload = copy.deepcopy(payload_copy)

        nfe_issuance_map = {
            "Emitir NF manualmente": "manual_issuance",
            "Emitir NF no faturamento": "on_billing",
            "Emitir NF na liquidação": "on_settlement",
        }
        payload["sisras_user"]["additionalData"]["billing_info"] = {
            "name": st.session_state.dados_cobranca_nome,
            "cep": st.session_state.dados_cobranca_cep,
            "cpfcnpj": st.session_state.dados_cobranca_documento,
            "phone": st.session_state.dados_cobranca_telefone,
            "address": st.session_state.dados_cobranca_endereco,
            "address_number": st.session_state.dados_cobranca_numero,
            "address_complement": st.session_state.dados_cobranca_complemento if st.session_state.dados_cobranca_complemento else None,
            "email": st.session_state.dados_cobranca_email,
            "neighborhood": st.session_state.dados_cobranca_bairro,
            "city": st.session_state.dados_cobranca_cidade,
            "state": st.session_state.dados_cobranca_estado,
            "birth_date": st.session_state.dados_cobranca_data_nasc.strftime("%Y-%m-%d") if st.session_state.dados_cobranca_data_nasc else None,
            "IBGE_code": st.session_state.dados_cobranca_ibge_code if "dados_cobranca_ibge_code" in st.session_state and st.session_state.dados_cobranca_ibge_code else None,
            "observation": st.session_state.dados_cobranca_obs if st.session_state.dados_cobranca_obs else None,
            "nfe_issuance_automation_type": nfe_issuance_map[st.session_state.dados_cobranca_nfse] if st.session_state.dados_cobranca_nfse else None,
            "nfe_iss_retido": True if st.session_state.dados_cobranca_iss_retido == "Sim" else False,
        }
        
        respose = requests.put(url, json=payload, headers=COMMON_API_HEADERS)

        if respose.status_code == 200:
            st.toast("Dados de cobranças sincronizados!")
        else:
            st.error("Houve um erro ao salvar os dados de cobrança no Nexo. Por favor tente novamente.")
            st.error(respose.text)

    else:
        st.error("O cadastro do cliente atual falhou ao ser criado ou não foi carregado corretamente.")

@st.cache_data(show_spinner=False)
def get_client_data(page=1, search_term="", ativo_filter=None, financ_filter=None):
    """Faz a requisição à API para obter os dados dos clientes."""

    with st.spinner("Carregando dados..."):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Token': 'c0f9e2df-d26b-11ef-9216-0e3d092b76f7',
            'Origin': 'https://globalsystem.plataforma.app.br',
            'Referer': 'https://globalsystem.plataforma.app.br/'
        }
        
        params = {
            'include_managers': 1,
            'items_per_page': 50,
            'paginate': 1,
            'current_page': page,
        }
        
        if search_term:
            params['all'] = search_term

        if ativo_filter:
                params['active'] = ativo_filter
        if financ_filter:
                params['financial_alert'] = financ_filter
        
        url = "https://api.plataforma.app.br/manager/users"
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()  # Lança um erro para códigos de status ruins (4xx ou 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao conectar com a API: {e}")
            return None
        


def get_user_data_by_id(user_id):
    """Faz a requisição à API para obter os dados de um único usuário."""
    if not user_id:
        return None
    
    url = f"https://api.plataforma.app.br/user/{user_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Token': 'c0f9e2df-d26b-11ef-9216-0e3d092b76f7',
        'Origin': 'https://globalsystem.plataforma.app.br',
        'Referer': 'https://globalsystem.plataforma.app.br/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar dados do usuário: {e}")
        return None
    


def format_date_from_api(date_string):
    """Converte 'YYYY-MM-DDTHH:MM:SS+0000' para um objeto date."""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string.split('T')[0], '%Y-%m-%d').date()
    except (ValueError, IndexError):
        return None
    
def validate_dados_cobranca():
    if not st.session_state.dados_cobranca_numero:
        st.error("O campo 'Número' é obrigatório.")
        return False
    if not st.session_state.dados_cobranca_bairro:
        st.error("O campo 'Bairro' é obrigatório.")
        return False
    if not st.session_state.dados_cobranca_cidade:
        st.error("O campo 'Cidade' é obrigatório.")
        return False
    if not st.session_state.dados_cobranca_estado:
        st.error("O campo 'Estado' é obrigatório.")
        return False
    if not st.session_state.dados_cobranca_cep:
        st.error("O campo 'CEP' é obrigatório.")
        return False
    if not st.session_state.dados_cobranca_email:
        st.error("O campo 'E-mail' é obrigatório.")
        return False
    if not st.session_state.dados_cobranca_endereco:
        st.error("O campo 'Endereço' é obrigatório.")
        return False
    if not st.session_state.dados_cobranca_documento:
        st.error("O campo 'CPF/CNPJ' é obrigatório.")
        return False
    if not len(st.session_state.dados_cobranca_nome.split(" ")) > 1:
        st.error("O campo 'Nome' deve conter pelo menos dois nomes.")
        return False
    if not st.session_state.dados_cobranca_telefone:
        st.error("O campo 'Telefone' é obrigatório.")
        return False
    
    if st.session_state.dados_cobranca_tipo_pessoa == "Pessoa Física (CPF)" and not validar_cpf(st.session_state.dados_cobranca_documento):
        st.error("O campo 'CPF' deve ser um CPF válido.")
        return False
    if st.session_state.dados_cobranca_tipo_pessoa == "Pessoa Jurídica (CNPJ)" and not validar_cnpj(st.session_state.dados_cobranca_documento):
        st.error("O campo 'CNPJ' deve ser um CNPJ válido.")
        return False
    if st.session_state.dados_cobranca_telefone.startswith("+"):
        st.error("O campo 'Telefone' não deve começar com '+'.")
        return False
    if st.session_state.dados_cobranca_telefone.startswith("55"):
        st.error("O campo 'Telefone' não deve começar com '55'.")
        return False
    
    tamanho_tel = len(''.join(list(filter(str.isdigit, st.session_state.dados_cobranca_telefone))))
    if tamanho_tel not in [10, 11]:
        st.error("O campo 'Telefone' deve ter 10 ou 11 dígitos.")
        return False
    
    return True

def validate_form_cadastro():
    if not st.session_state.form_nome:
        st.error("O campo 'Nome' é obrigatório!")
        return False
    if not st.session_state.form_responsavel:
        st.error("O campo 'Responsável' é obrigatório!")
        return False
    if not st.session_state.form_cpf_cnpj:
        st.error("O campo 'CPF/CNPJ' é obrigatório!")
        return False
    if not st.session_state.form_email:
        st.error("O campo 'E-mail' é obrigatório!")
        return False
    if not st.session_state.form_tel_celular:
        st.error("O campo 'Telefone' é obrigatório!")
        return False
    if not st.session_state.form_endereco:
        st.error("O campo 'Endereço' é obrigatório!")
        return False
    if not st.session_state.form_login:
        st.error("O campo 'Login' é obrigatório!")
        return False
    if not st.session_state.form_senha:
        st.error("O campo 'Senha' é obrigatório!")
        return False
    if not st.session_state.form_confirmar_senha:
        st.error("O campo 'Confirmar Senha' é obrigatório!")
        return False
    if st.session_state.form_senha != st.session_state.form_confirmar_senha:
        st.error("As senhas não correspondem!")
        return False
    if st.session_state.form_valor_mensalidade == 0.00:
        st.error("O campo 'Valor da Mensalidade' é obrigatório!")
        return False

    return True

@st.cache_data(show_spinner=False)
def get_vehicles_for_client(user_id):
    """Busca os veículos de um cliente específico."""

    with st.spinner(f"Buscando veículos para o cliente {user_id}..."):
        url = f'{API_BASE_URL}/manager/user/{user_id}/vehicles'
        logging.info(f"Buscando veículos para o cliente ID: {user_id} na URL: {url}")
        try:
            response = requests.get(url, headers=COMMON_API_HEADERS, timeout=30)
            response.raise_for_status()
            vehicles = response.json()
            logging.info(f"Veículos encontrados para o cliente {user_id}: {len(vehicles)}")
            return vehicles
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"Erro HTTP ao buscar veículos para o cliente {user_id}: {http_err}. Resposta: {http_err.response.text if http_err.response else 'N/A'}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Erro de conexão ao buscar veículos para o cliente {user_id}: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout ao buscar veículos para o cliente {user_id}: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Erro geral de requisição ao buscar veículos para o cliente {user_id}: {req_err}")
        except json.JSONDecodeError as json_err:
            logging.error(f"Erro ao decodificar JSON da resposta de veículos para o cliente {user_id}: {json_err}. Resposta: {response.text if 'response' in locals() and response else 'N/A'}")
        return []

@st.cache_data(show_spinner=False)
def get_all_vehicle_data(vehicle_id):
    with st.spinner(f"Buscando dados do veículo. {vehicle_id}.."):
        
        """Busca todos os dados de um veículo específico."""
        url = f'{API_BASE_URL}/manager/vehicle/{vehicle_id}'
        logging.info(f"Buscando dados do veículo ID: {vehicle_id} na URL: {url}")
        try:
            response = requests.get(url, headers=COMMON_API_HEADERS, timeout=30)
            response.raise_for_status()
            vehicle_data = response.json()
            logging.info(f"Dados do veículo {vehicle_id} encontrados.")
            return vehicle_data
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"Erro HTTP ao buscar dados do veículo {vehicle_id}: {http_err}. Resposta: {http_err.response.text if http_err.response else 'N/A'}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Erro de conexão ao buscar dados do veículo")
        except json.JSONDecodeError as json_err:
            logging.error(f"Erro ao decodificar JSON da resposta de dados do veículo {vehicle_id}: {json_err}. Resposta: {response.text if 'response' in locals() and response else 'N/A'}")


@st.cache_data(show_spinner=False)
def get_vehicles_for_client(user_id):
    """Busca os veículos de um cliente específico."""

    with st.spinner(f"Buscando veículos para o cliente {user_id}..."):
        url = f'{API_BASE_URL}/manager/user/{user_id}/vehicles'
        logging.info(f"Buscando veículos para o cliente ID: {user_id} na URL: {url}")
        try:
            response = requests.get(url, headers=COMMON_API_HEADERS, timeout=30)
            response.raise_for_status()
            vehicles = response.json()
            logging.info(f"Veículos encontrados para o cliente {user_id}: {len(vehicles)}")
            return vehicles
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"Erro HTTP ao buscar veículos para o cliente {user_id}: {http_err}. Resposta: {http_err.response.text if http_err.response else 'N/A'}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Erro de conexão ao buscar veículos para o cliente {user_id}: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout ao buscar veículos para o cliente {user_id}: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Erro geral de requisição ao buscar veículos para o cliente {user_id}: {req_err}")
        except json.JSONDecodeError as json_err:
            logging.error(f"Erro ao decodificar JSON da resposta de veículos para o cliente {user_id}: {json_err}. Resposta: {response.text if 'response' in locals() and response else 'N/A'}")
        return []



def send_single_telegram_message(message_part: str, chat_id: str) -> bool:
    """Envia uma única parte da mensagem para um chat_id."""
    if not message_part or not message_part.strip():
        logging.debug(f"Ignorando envio de mensagem vazia para {chat_id}")
        return True

    payload = {'message': message_part}
    url = f'https://web-production-493b.up.railway.app/sendMessage?chat_id={chat_id}&parse_mode=HTML'
    max_retries = 2
    delay = 2

    for attempt in range(max_retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=20)

            if response.status_code == 200:
                logging.debug(f"Parte da mensagem enviada com sucesso para {chat_id}.")
                return True
            else:
                logging.error(f"Falha ao enviar parte da mensagem para {chat_id}. Status: {response.status_code}, Resposta: {response.text}. Tentativa {attempt + 1} de {max_retries + 1}.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de requisição ao enviar parte da mensagem para {chat_id}: {e}. Tentativa {attempt + 1} de {max_retries + 1}.")
        
        if attempt < max_retries:
            sleep(delay)
    
    logging.error(f"Falha ao enviar parte da mensagem para {chat_id} após {max_retries + 1} tentativas.")
    return False