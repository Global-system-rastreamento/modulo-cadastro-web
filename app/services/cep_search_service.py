import requests


def search_cep(CEP):
    CEP = CEP.replace('.', '').replace('-', '')

    try:
        tries = 0
        data = None
        while True:
            if tries > 5:
                break
            
            response = requests.get(f'https://viacep.com.br/ws/{CEP}/json')
            tries += 1
            if response.status_code == 200:
                data = response.json()
                break
        
        if data is None:
            return None
        
        if not "erro" in data.keys():
            return data
        
        else:
            return None
    
    except requests.exceptions.JSONDecodeError:
        return
    except Exception as e:
        print(f"Erro ao buscar CEP: {e}")