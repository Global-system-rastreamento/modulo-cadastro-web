import requests


def search_cep(CEP):
    CEP = CEP.replace('.', '').replace('-', '')

    try:
        response = requests.get(f'https://viacep.com.br/ws/{CEP}/json').json()

    except requests.exceptions.JSONDecodeError:
        return

    if not 'erro' in response.keys():
        return response