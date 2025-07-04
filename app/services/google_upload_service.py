import os
import requests
import json
import io
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import ApiRequestError
from dotenv import load_dotenv

# Carrega as variáveis de ambiente de um arquivo .env (ótimo para desenvolvimento e produção)
load_dotenv()

def upload_to_drive(file_path: bytes, file_name: str, file_type: str, folder_id: str = os.getenv("GCP_FOLDER_ID_CONTRACT")) -> str | None:
    """
    Realiza o upload de um arquivo em formato de bytes para uma pasta específica no Google Drive.

    Esta função gerencia todo o ciclo de vida da credencial:
    1. Verifica se os arquivos de credenciais existem localmente.
    2. Se não existirem, tenta baixá-los de uma URL segura definida em variáveis de ambiente.
    3. Usa o método de autenticação OAuth 2.0 com refresh_token, ideal para produção.
    4. Faz o upload do conteúdo em bytes para a pasta de destino.

    Args:
        file_bytes (bytes): O conteúdo do arquivo a ser enviado.
        file_name (str): O nome que o arquivo terá no Google Drive.
        folder_id (str): O ID da pasta de destino no Google Drive.

    Returns:
        str | None: A URL pública do arquivo no Google Drive em caso de sucesso, ou None em caso de falha.
    """
    print(f"Iniciando processo de upload para o arquivo: {file_name}")

    # --- 1. GERENCIAMENTO DE CREDENCIAIS (integrando seu código) ---
    try:
        if not os.path.exists("app/config/keys"):
            os.makedirs("app/config/keys")
            
        client_secrets_path = "app/config/keys/client_secret_upload_contract.json"
        with open(client_secrets_path, "w") as f:
            f.write(os.getenv("CLIENT_SECRET_OAUTH"))
        
        prod_creds_path = "app/config/keys/prodclient_secret_upload_contract.json"

        if not os.path.exists(prod_creds_path):
            with open(prod_creds_path, "w") as f:
                f.write(os.getenv("CLIENT_SECRET_OAUTH_PROD"))
        else:
            os.environ["CLIENT_SECRET_OAUTH_PROD"] = open(prod_creds_path, "r").read()
        
    except (requests.exceptions.RequestException, ValueError, FileNotFoundError, TypeError) as e:
        print(f"❌ ERRO CRÍTICO na gestão de credenciais: {e}")
        return None

    # --- 2. AUTENTICAÇÃO ROBUSTA (nosso método final) ---
    try:
        settings = {
            "client_config_file": client_secrets_path,
            "save_credentials_file": prod_creds_path,
        }
        gauth = GoogleAuth(settings=settings)

        gauth.LoadCredentialsFile(prod_creds_path)

        if gauth.credentials is None:
            raise Exception("Não foi possível carregar as credenciais do arquivo. Execute o script de geração de token.")
        elif gauth.access_token_expired:
            print("Token expirado. Renovando...")
            gauth.Refresh()
        else:
            print("Token ainda válido. Autorizando...")
            gauth.Authorize()
        
        print("✔️  Autenticação no Google Drive bem-sucedida!")
        drive = GoogleDrive(gauth)

    except Exception as e:
        print(f"❌ ERRO CRÍTICO na autenticação: {e}")
        return None

    # --- 3. UPLOAD DO ARQUIVO EM BYTES ---
    try:
        print(f"Realizando upload para a pasta de ID: {folder_id}")
        
        file_drive = drive.CreateFile({
            'title': file_name,
            'parents': [{'id': folder_id}],
            'mimeType': file_type,
        })

        file_drive.SetContentFile(file_path)
        file_drive.Upload() 

        print(f"🚀 SUCESSO! O arquivo foi enviado.")
        return file_drive.get('alternateLink')

    except ApiRequestError as e:
        print(f"❌ ERRO na API do Google Drive durante o upload: {e}")
        return None
    except Exception as e:
        print(f"❌ ERRO inesperado durante o upload: {e}")
        return None


if __name__ == "__main__":
    DESTINATION_FOLDER_ID = os.getenv("GCP_FOLDER_ID_CONTRACT")

    if not DESTINATION_FOLDER_ID:
        print("A variável de ambiente 'GCP_FOLDER_ID_CONTRACT' não está definida.")
        print("Pulando o exemplo de upload.")
    else:
        file_url = upload_to_drive(
            file_path="tests/template_contrato_GSM.docx",
            file_name="contrato_teste_producao.txt",
            folder_id=DESTINATION_FOLDER_ID,
            file_type="docx"
        )

        if file_url:
            print(f"\nUpload concluído com sucesso! Link do arquivo: {file_url}")
        else:
            print("\nO upload falhou. Verifique os logs de erro acima.")

