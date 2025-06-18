import re

def validar_cpf(cpf):
    """
    Valida um CPF conforme o algoritmo oficial brasileiro.
    
    Args:
        cpf (str): String do CPF com ou sem formatação
        
    Returns:
        bool: True se o CPF for válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais (casos inválidos conhecidos)
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    
    resto = soma % 11
    primeiro_digito = 0 if resto < 2 else 11 - resto
    
    # Verifica o primeiro dígito
    if int(cpf[9]) != primeiro_digito:
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    
    resto = soma % 11
    segundo_digito = 0 if resto < 2 else 11 - resto
    
    # Verifica o segundo dígito
    return int(cpf[10]) == segundo_digito


def validar_cnpj(cnpj):
    """
    Valida um CNPJ conforme o algoritmo oficial brasileiro.
    
    Args:
        cnpj (str): String do CNPJ com ou sem formatação
        
    Returns:
        bool: True se o CNPJ for válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'\D', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais (casos inválidos conhecidos)
    if cnpj == cnpj[0] * 14:
        return False
    
    # Sequências de pesos para o cálculo dos dígitos verificadores
    pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_segundo = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(12):
        soma += int(cnpj[i]) * pesos_primeiro[i]
    
    resto = soma % 11
    primeiro_digito = 0 if resto < 2 else 11 - resto
    
    # Verifica o primeiro dígito
    if int(cnpj[12]) != primeiro_digito:
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(13):
        soma += int(cnpj[i]) * pesos_segundo[i]
    
    resto = soma % 11
    segundo_digito = 0 if resto < 2 else 11 - resto
    
    # Verifica o segundo dígito
    return int(cnpj[13]) == segundo_digito
