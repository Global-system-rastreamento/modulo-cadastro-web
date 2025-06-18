import gspread
import time
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError
import os
import dotenv

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# Definir os escopos necessários
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

def connect_to_sheets():
    creds_dir_path = 'app/config/keys'
    
    if not os.path.exists(creds_dir_path):
        os.makedirs(creds_dir_path)
    
    creds_path = os.path.join(creds_dir_path, 'gcp_service_account.json')

    with open(creds_path, 'w') as f:
        f.write(os.getenv('GOOGLE_SERVICE_ACC_KEY'))

    credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(credentials)

def retry_operation(operation, max_retries=5):
    for attempt in range(max_retries):
        try:
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

def update_servicos_planilha(data, single=True):
    # Conecta ao serviço
    client = connect_to_sheets()
    
    # Abre uma planilha por ID
    def open_sheet():
        return client.open_by_key('1XBkgV--XHugeEk6PiScXpoQBMygj5HJi')
    
    spreadsheet = retry_operation(open_sheet)
    
    # Seleciona uma aba específica
    def get_worksheet():
        return spreadsheet.worksheet('CODIGOS').insert_row
    
    worksheet = retry_operation(get_worksheet)
    
    # Lê todos os dados
    def read_all():
        return worksheet.get_all_records()
    
    dados = retry_operation(read_all)
    # Adiciona uma linha nova
    def append_data():
        if single:
            return worksheet.insert_row(data, index=2)
        
        return worksheet.insert_row(data, index=2)
    
    result = retry_operation(append_data)

    return "Operações concluídas com sucesso!"

def get_data():
    client = connect_to_sheets()

    def get_planilha():
        return client.open_by_key('1jjHgLRZNyTYwBueaEnGgsOYM1JSHrNoa9HUq6JZK9LM')
    
    spreadsheet = retry_operation(get_planilha)

    def get_worksheets():
        return spreadsheet.worksheet('CODIGOS').add
    
    CODIGOS = retry_operation(get_worksheets)

    return CODIGOS.get_all_records()[0]

if __name__ == '__main__':
    # update_servicos_planilha()
    print(get_data())