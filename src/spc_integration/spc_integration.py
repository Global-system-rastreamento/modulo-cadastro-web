from datetime import datetime, timezone, date
import base64
import requests
import json
import pdfkit
import markdown2
import streamlit as st

# --- Funções da Integração SPC ---
def formatar_data_spc(data_timestamp):
    if not data_timestamp:
        return None # Retorna None para st.date_input
    try:
        if isinstance(data_timestamp, int):
            # Converte milissegundos para segundos se necessário
            dt_obj = datetime.fromtimestamp(data_timestamp / 1000.0, tz=timezone.utc)
        elif isinstance(data_timestamp, str):
            try:
                dt_obj = datetime.fromisoformat(data_timestamp.replace('Z', '+00:00'))
            except ValueError:
                dt_obj = datetime.fromtimestamp(int(data_timestamp) / 1000.0, tz=timezone.utc)
        else:
            return None
        return dt_obj.date() # Retorna objeto date
    except Exception:
        return None

def formatar_documento_spc(numero, tipo):
    if isinstance(numero, dict):
        numero = numero.get('numero', '')
    if not numero or numero == 'N/A':
        return ''
    numero_limpo = ''.join(filter(str.isdigit, str(numero)))
    if tipo == 'F' and len(numero_limpo) == 11:
        return f"{numero_limpo[:3]}.{numero_limpo[3:6]}.{numero_limpo[6:9]}-{numero_limpo[9:]}"
    elif tipo == 'J' and len(numero_limpo) == 14:
        return f"{numero_limpo[:2]}.{numero_limpo[2:5]}.{numero_limpo[5:8]}/{numero_limpo[8:12]}-{numero_limpo[12:]}"
    return numero_limpo 

def formatar_telefone_spc(ddd, numero_tel):
    if not ddd or not numero_tel:
        return ""
    ddd_str = str(ddd)
    numero_str = str(numero_tel)
    if len(numero_str) == 8: # Fixo antigo ou celular sem 9
        return f"({ddd_str}) {numero_str[:4]}-{numero_str[4:]}"
    elif len(numero_str) == 9: # Celular com 9
        return f"({ddd_str}) {numero_str[:5]}-{numero_str[5:]}"
    return f"({ddd_str}) {numero_str}" # Outros casos

def calcular_idade_spc(data_nascimento_timestamp):
    data_nasc_obj = formatar_data_spc(data_nascimento_timestamp)
    if not data_nasc_obj:
        return 'N/A'
    try:
        hoje = date.today()
        idade = hoje.year - data_nasc_obj.year - ((hoje.month, hoje.day) < (data_nasc_obj.month, data_nasc_obj.day))
        return str(idade)
    except Exception:
        return 'N/A'

def formatar_valor_spc(valor):
    try:
        valor_float = float(valor or 0)
        return f"R$ {valor_float:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
    except (ValueError, TypeError):
        return 'R$ 0,00'

def extrair_detalhes_spc_api(return_object):
    try:
        detalhes = return_object.get('resultado', {}).get('spc', {}).get('detalheSpc', [])
        return detalhes if isinstance(detalhes, list) else []
    except Exception:
        return []

def extrair_detalhes_protesto_api(return_object):
    try:
        detalhes = return_object.get('resultado', {}).get('protesto', {}).get('detalheProtesto', [])
        return detalhes if isinstance(detalhes, list) else []
    except Exception:
        return []

def consultar_spc_api(documento: str, tipo_documento: str):
    auth = base64.b64encode(b"126834722:GlobalAuto9537@@") 
    headers = {
        "Authorization": f"Basic {auth.decode()}",
        "Content-Type": 'application/json'
    }
    payload = {
        "codigoProduto": "323",
        "tipoConsumidor": tipo_documento, 
        "documentoConsumidor": documento.replace(".", "").replace("-", "").replace("/", ""),
        "codigoInsumoOpcional": []
    }
    try:
        response = requests.post(
            'https://servicos.spc.org.br/spcconsulta/recurso/consulta/padrao',
            json=payload,
            headers=headers,
            timeout=30 
        )
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de comunicação ao consultar SPC: {e}")
        return None
    except json.JSONDecodeError:
        st.error("Erro ao decodificar a resposta do SPC (não é um JSON válido).")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao consultar SPC: {e}")
        return None

def gerar_relatorio_spc_markdown(dados_json):
    if not dados_json:
        return "## Erro\nNão foi possível obter os dados para gerar o relatório."
    try:
        resultado = dados_json.get('result', {}).get('return_object', {}).get('resultado', {})
        if not resultado: 
            error_message = dados_json.get('result', {}).get('message', 'Dados de resultado não encontrados ou vazios na resposta da API.')
            return f"## Erro na Geração do Relatório\n{error_message}"

        protocolo = resultado.get('protocolo', {})
        operador = resultado.get('operador', {})
        
        consumidor = resultado.get('consumidor', {})
        consumidor_pf = consumidor.get('consumidorPessoaFisica', {})
        consumidor_pj = consumidor.get('consumidorPessoaJuridica', {})
        
        tipo_documento_relatorio = 'PF' if consumidor_pf else 'PJ'
        
        # Usando formatar_data_spc que retorna objeto date, e depois formatando para string no relatório
        data_consulta_obj = formatar_data_spc(resultado.get('data'))
        data_consulta_str = data_consulta_obj.strftime('%d/%m/%Y') if data_consulta_obj else "N/A"

        protocolo_numero = protocolo.get('protocoloFormatado', 'N/A')
        operador_nome = operador.get('nome', 'N/A')
        
        nome_relatorio = 'N/A'
        doc_relatorio = 'N/A'
        situacao_documento_relatorio = 'N/A'

        if tipo_documento_relatorio == 'PF':
            nome_relatorio = consumidor_pf.get('nome', 'N/A')
            doc_relatorio = formatar_documento_spc(consumidor_pf.get('cpf', {}), 'F')
            situacao_documento_relatorio = consumidor_pf.get('situacaoCpf', {}).get('descricaoSituacao', 'N/A')
        else: 
            nome_relatorio = consumidor_pj.get('razaoSocial', 'N/A')
            doc_relatorio = formatar_documento_spc(consumidor_pj.get('cnpj', {}), 'J')
            situacao_documento_relatorio = consumidor_pj.get('situacaoCnpj', {}).get('descricaoSituacao', 
                                            consumidor_pj.get('situacaoCadastral', {}).get('descricao', 'N/A'))

        restricao = resultado.get('restricao', False)
        spc_resumo = resultado.get('spc', {}).get('resumo', {})
        protesto_resumo = resultado.get('protesto', {}).get('resumo', {})
        
        spc_quantidade = spc_resumo.get('quantidadeTotal', 0)
        spc_valor_total = formatar_valor_spc(spc_resumo.get('valorTotal', 0))
        
        data_ult_ocorr_obj = formatar_data_spc(spc_resumo.get('dataUltimaOcorrencia'))
        spc_ultima_ocorrencia_str = data_ult_ocorr_obj.strftime('%d/%m/%Y') if data_ult_ocorr_obj else "N/A"

        protesto_quantidade = protesto_resumo.get('quantidadeTotal', 0)
        protesto_valor_total = formatar_valor_spc(protesto_resumo.get('valorTotal', 0))
        
        valor_total_devido = formatar_valor_spc(
            (spc_resumo.get('valorTotal', 0) or 0) + 
            (protesto_resumo.get('valorTotal', 0) or 0)
        )
        
        detalhes_spc_list = extrair_detalhes_spc_api(dados_json.get('result', {}).get('return_object', {}))
        detalhes_protesto_list = extrair_detalhes_protesto_api(dados_json.get('result', {}).get('return_object', {}))
        
        relatorio_md = f"""
# RELATÓRIO DE CONSULTA SPC/SERASA

## DADOS DA CONSULTA
- **Protocolo:** {protocolo_numero}
- **Data da Consulta:** {data_consulta_str}
- **Operador:** {operador_nome}

## IDENTIFICAÇÃO
- **Nome/Razão Social:** {nome_relatorio}
- **Documento (CPF/CNPJ):** {doc_relatorio}
- **Situação do Documento:** {situacao_documento_relatorio}

---
## SEÇÃO DE RESTRIÇÕES - ANÁLISE DETALHADA

### Resumo Consolidado de Restrições
- **STATUS GERAL:** **{'RESTRITO' if restricao else 'REGULAR'}**

### Análise Financeira de Restrições
- **REGISTROS SPC:**
  - Quantidade Total: {spc_quantidade}
  - Valor Acumulado: {spc_valor_total}
  - Última Ocorrência: {spc_ultima_ocorrencia_str}

- **PROTESTOS IDENTIFICADOS:**
  - Quantidade de Protestos: {protesto_quantidade}
  - Valor Total de Protestos: {protesto_valor_total}

- **CONSOLIDADO FINANCEIRO:**
  - VALOR TOTAL DEVIDO: {valor_total_devido}

## DETALHES ESPECÍFICOS DE OCORRÊNCIAS SPC
"""
        if detalhes_spc_list:
            for index, detalhe in enumerate(detalhes_spc_list):
                data_incl_obj = formatar_data_spc(detalhe.get('dataInclusao'))
                data_incl_str = data_incl_obj.strftime('%d/%m/%Y') if data_incl_obj else "N/A"
                data_venc_obj = formatar_data_spc(detalhe.get('dataVencimento'))
                data_venc_str = data_venc_obj.strftime('%d/%m/%Y') if data_venc_obj else "N/A"
                relatorio_md += f"""
### OCORRÊNCIA SPC - Registro {index + 1}
- **Credor:** {detalhe.get('nomeAssociado', 'NÃO IDENTIFICADO')}
- **Número Contrato:** {detalhe.get('contrato', 'SEM NÚMERO')}
- **Valor Específico:** {formatar_valor_spc(detalhe.get('valor'))}
- **Data Inclusão:** {data_incl_str}
- **Data Vencimento:** {data_venc_str}
---
"""
        else:
            relatorio_md += "\n**Nenhum Registro SPC Encontrado**\n"

        relatorio_md += "\n## DETALHES COMPLETOS DE PROTESTOS\n"
        if detalhes_protesto_list:
            for index, detalhe in enumerate(detalhes_protesto_list):
                data_prot_obj = formatar_data_spc(detalhe.get('dataProtesto'))
                data_prot_str = data_prot_obj.strftime('%d/%m/%Y') if data_prot_obj else "N/A"
                relatorio_md += f"""
### PROTESTO - Registro {index + 1}
- **Cartório:** {detalhe.get('cartorio', {}).get('nome', 'CARTÓRIO NÃO IDENTIFICADO')}
- **Data Oficial do Protesto:** {data_prot_str}
- **Valor do Protesto:** {formatar_valor_spc(detalhe.get('valor'))}
---
"""
        else:
            relatorio_md += "\n**Nenhum Protesto Registrado**\n"

        relatorio_md += """
## OBSERVAÇÕES CRÍTICAS
- **VALIDAÇÃO OBRIGATÓRIA:**
  1. Verificar autenticidade de TODOS os documentos.
  2. Confirmação PRÉVIA de contatos antes de qualquer aprovação.
  3. Relatório com geração automática - VALIDAÇÃO MANUAL NECESSÁRIA.
"""
        return relatorio_md
    
    except Exception as e:
        st.error(f"Erro ao gerar o conteúdo do relatório: {e}")
        return f"## Erro na Geração do Relatório\nOcorreu um erro interno: {e}"

def markdown_para_pdf_streamlit(texto_markdown, nome_arquivo_sugerido="relatorio_spc.pdf"):
    try:
        config = pdfkit.configuration() 
    except OSError:
        st.warning("wkhtmltopdf não foi detectado automaticamente. Tentando caminho padrão para Windows...")
        try:
            path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        except OSError:
            st.error("Erro Crítico: wkhtmltopdf não encontrado.")
            return None, None

    html_completo = f"""
        <html><head><meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; font-size: 10pt; }}
            h1 {{ font-size: 16pt; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px;}}
            h2 {{ font-size: 14pt; color: #444; margin-top: 1.5em; margin-bottom: 0.5em;}}
            h3 {{ font-size: 12pt; color: #555; margin-top: 1em; margin-bottom: 0.3em;}}
            ul {{ margin-bottom: 0.5em;}} li {{ margin-bottom: 0.2em; }}
            strong {{ font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 1em; font-size: 9pt; }}
            th, td {{ border: 1px solid #ddd; padding: 6px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            hr {{ border: 0; border-top: 1px solid #eee; margin: 1em 0; }}
        </style></head><body>
        {markdown2.markdown(texto_markdown, extras=["tables", "fenced-code-blocks", "nofollow", "cuddled-lists"])}
        </body></html>"""
    try:
        options = {
            'page-size': 'A4', 'margin-top': '0.75in', 'margin-right': '0.75in',
            'margin-bottom': '0.75in', 'margin-left': '0.75in',
            'encoding': "UTF-8", 'no-outline': None, 'enable-local-file-access': None
        }
        pdf_bytes = pdfkit.from_string(html_completo, False, configuration=config, options=options)
        return pdf_bytes, nome_arquivo_sugerido
    except Exception as e:
        st.error(f"Erro ao gerar PDF com pdfkit: {e}")
        return None, None