import requests
import logging

def obter_token_acesso(auth_url="https://apicorp.algartelecom.com.br/oauth-portal/access-token", session=None):
    """
    Executa a criação de um token de acesso (login).
    """
    payload = {
        "grant_type": 'client_credentials'
    }

    headers = {
        'authorization': 'Basic Mzg5MjgzODEtNDA5ZC0zZWFjLWE3OTEtY2E4ZjExZDdkZGU2OmMwMTZhZDEyLTQ4MWUtM2FlYS04YWU2LWU4YTFhNjI4NDU5Ng==',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'realm': '0d5a3954',
        'username': 'api_global',
        'password': '98375656@plmN',
        'Cookie': 'TS013760f7=0117335212ef439c0598d782717985b889dc2c64b30a2003f6b3cfa96aa7391d35114a3245ef15c09b406955920f2ec80e4259a55f'
    }

    try:
        response = session.post(auth_url, headers=headers, json=payload)
        logging.info(f"URL: {auth_url}")
        logging.info(f"Headers: {headers}")
        logging.info(f"Payload: {payload}")

        response.raise_for_status()

        token_data = response.json()
        logging.info('Resposta do servidor: ' + str(response.json()))
        logging.info("Token obtido com sucesso!")
        return token_data.get('access_token')

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao obter token de acesso: {e}")
        if 'response' in locals():
            logging.error(f"Resposta do servidor: {response.status_code} - {response.text}")
        return None

def solicitar_reset_rede(access_token, msisdn, reset_url="https://apicorp.algartelecom.com.br/telecom/product-Inventory-management/management/v1/broker/reset-network", session=None):
    """
    Solicita o reset de rede para um determinado MSISDN.
    """
    headers = {
        "client_id": "38928381-409d-3eac-a791-ca8f11d7dde6",
        'access_token': access_token,
    }

    payload = {
        "msisdns": [msisdn]
    }

    try:
        response = session.post(reset_url, headers=headers, json=payload)
        logging.info(f"Tentando resetar rede para {msisdn}...")
        logging.info(f"URL: {reset_url}")
        logging.info(f"Headers: {headers}")
        logging.info(f"Payload: {payload}")

        if response.status_code == 201:
            logging.info("Solicitação de reset de rede enviada com sucesso!")
            logging.info(f"Resposta do servidor (Status {response.status_code}): {response.text}")
            return True
        else:
            logging.error(f"Erro ao solicitar reset de rede. Status: {response.status_code}")
            logging.error(f"Resposta do servidor: {response.text}")
            response.raise_for_status()
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição de reset de rede: {e}")
        if 'response' in locals():
            logging.error(f"Resposta do servidor: {response.status_code} - {response.text}")
        return False

def main(recipient, session):
    """
    Função principal para obter token de acesso e solicitar reset de rede.
    """
    MSISDN_PARA_RESETAR = recipient

    try:
        token = obter_token_acesso(session=session)

        if token:
            logging.info(f"\nToken recebido: {token[:10]}...")

            sucesso_reset = solicitar_reset_rede(
                access_token=token,
                msisdn=MSISDN_PARA_RESETAR,
                session=session,
            )

            if sucesso_reset:
                logging.info("\nFluxo concluído: Token obtido e reset de rede solicitado.")
            else:
                logging.error("\nFluxo falhou na etapa de reset de rede.")
        else:
            logging.error("\nFluxo falhou: Não foi possível obter o token de acesso.")

    except Exception as e:
        logging.error(f'Ocorreu um erro não tratado durante a execução do reset de rede para {recipient}')

if __name__ == "__main__":
    main("5511972297953", requests.Session())
