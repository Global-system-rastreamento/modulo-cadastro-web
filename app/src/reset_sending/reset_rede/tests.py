def remover_linhas_report_append(arquivo_origem, arquivo_destino=None):
    """
    Remove linhas que contêm report_lines.append(...qualquer_coisa...)
    
    Args:
        arquivo_origem (str): Caminho do arquivo original
        arquivo_destino (str): Caminho do arquivo de destino (opcional)
    """
    
    # Se não especificar destino, sobrescreve o arquivo original
    if arquivo_destino is None:
        arquivo_destino = arquivo_origem
    
    try:
        # Ler o arquivo
        with open(arquivo_origem, 'r', encoding='utf-8') as file:
            linhas = file.readlines()
        
        # Filtrar linhas que NÃO contêm report_lines.append
        linhas_filtradas = []
        linhas_removidas = 0
        
        for linha in linhas:
            # Verifica se a linha contém report_lines.append(
            if 'report_lines.append(' not in linha:
                linhas_filtradas.append(linha)
            else:
                linhas_removidas += 1
                print(f"Removida: {linha.strip()}")
        
        # Escrever o arquivo filtrado
        with open(arquivo_destino, 'w', encoding='utf-8') as file:
            file.writelines(linhas_filtradas)
        
        print(f"\nProcesso concluído!")
        print(f"Linhas removidas: {linhas_removidas}")
        print(f"Arquivo salvo em: {arquivo_destino}")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_origem}' não encontrado.")
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    remover_linhas_report_append('app/utils/funcs/reset_rede/plataforma_VS.py')