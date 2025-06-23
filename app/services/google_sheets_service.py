import gspread
import time
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError
from gspread.worksheet import Worksheet
import os
import shutil

import streamlit as st
import dotenv
import json
import requests

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# Definir os escopos necessários
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

def connect_to_sheets():
    creds_dir_path = os.getenv("GCP_ACC_KEY_PATH")
    
    if not os.path.exists(creds_dir_path):
        os.makedirs(creds_dir_path)

    creds_path = os.path.join(creds_dir_path, os.getenv("GCP_KEY_FILENAME"))

    if not os.path.exists(creds_path):
        url_secret = os.getenv("SERVER_LOAD_GCP_KEY")
        if not url_secret:
            raise ValueError("URL_SECRET não está definida no arquivo .env")
        
        response = requests.get(os.getenv("SERVER_LOAD_GCP_KEY"))

        response_json = None
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            pass

        if response_json:
            with open(creds_path, 'w') as f:
                f.write(json.dumps(response_json.get("data", {})))
                
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Arquivo de credenciais não encontrado em {creds_path}")

    credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)

    return gspread.authorize(credentials)

def retry_operation(operation, *args, **kwargs):
    if "max_retries" not in kwargs:
        max_retries = 3
    else:
        max_retries = kwargs["max_retries"]
        del kwargs["max_retries"]

    for attempt in range(max_retries):
        try:
            if args and kwargs:
                return operation(*args, **kwargs)
            elif args:
                return operation(*args)
            elif kwargs:
                return operation(**kwargs)
            else:
                return operation()
        
        except APIError as e:
            if e.response.status_code == 429:
                wait_time = (2 ** attempt) + 1
                print(f"Limite de taxa excedido. Tentativa {attempt+1}/{max_retries}. Aguardando {wait_time} segundos...")
                time.sleep(wait_time)
            else:
                if attempt < max_retries - 1:
                    print(f"Erro na API: {e}. Tentativa {attempt+1}/{max_retries}.")
                    time.sleep(1)
                else:
                    raise
        except Exception as e:
            raise

def get_planilha(client, planilha_id):
    return client.open_by_key(planilha_id)

def inserir_linha(planilha, data):
    def insert_row(planilha, data):
        return planilha.insert_row(data, index=2)
    
    return retry_operation(insert_row, planilha, data)

def get_worksheets(spreadsheet, nome):
    def get_worksheet(spreadsheet, nome):
        return spreadsheet.worksheet(nome)

    return retry_operation(get_worksheet, spreadsheet, nome)

def update_planilha(data, nome):
    try:
        client = connect_to_sheets()

        spreadsheet = get_planilha(client, os.getenv("PLAN_ID_KEY"))

        CODIGOS = get_worksheets(spreadsheet, nome)

        inserir_linha(CODIGOS, data)

    except Exception as e:
        st.error(f"Erro ao atualizar planilha: {e}")

    else:
        st.success("Planilha atualizada com sucesso!")

def get_data_from_sheet(name_sheet):
    try:
        client = connect_to_sheets()
        spreadsheet = get_planilha(client, os.getenv("PLAN_ID_KEY"))
        worksheet = spreadsheet.worksheet(name_sheet)
        data = worksheet.get_all_records()
        return data
    except Exception as e:
        st.error(f"Erro ao obter dados da planilha: {e}")
        return None

def delete_row_from_sheet(name_sheet, row_index):
    try:
        client = connect_to_sheets()
        spreadsheet = get_planilha(client, os.getenv("PLAN_ID_KEY"))
        worksheet: Worksheet = spreadsheet.worksheet(name_sheet)
        worksheet.delete_rows(row_index)
    except Exception as e:
        st.error(f"Erro ao excluir linha da planilha: {e}")
if __name__ == '__main__':
    pass