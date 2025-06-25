import streamlit as st
from datetime import datetime

def apply_design():
    st.set_page_config(layout="wide", page_title="Cadastro de Clientes", page_icon=":house:")
    custom_css = """
        <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    :root {
        --franchisee-main-color: #006535;
        --header-bg-color: #0b3747;
        --button-text-color: white; /* Alterado para branco para melhor contraste */
        --input-bg-color: #f4f4f4;
        --input-border-color: #ced4da;
        --input-text-color: #555;
        --label-text-color: #666;
        --body-text-color: #212529;
        --section-title-color: #333;
        --table-header-bg: #f8f9fa;
        --table-border-color: #e9ecef;
        --streamlit-font-family: 'Roboto', Arial, sans-serif;
    }

    body, .stApp {
        font-family: var(--streamlit-font-family) !important;
        background-color: #EBEBEB !important;
        color: var(--body-text-color) !important;
    }

    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* --- INÍCIO: ESTILO PADRÃO PARA st.container --- */
    /* Baseado na sua sugestão, estamos estilizando a classe .stVerticalBlock
       que o Streamlit usa para containers. Isso evita a necessidade de wrappers de markdown. */
    .stVerticalBlock {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 25px;
        box-shadow: 0 18px 8px rgba(0,0,0,0.2);
        border: 2px solid #bababa;
        margin-bottom: 2rem;
    }
    .st-bb .stVerticalBlock {
        background-color: transparent;
        border: none;
        box-shadow: none;
        padding: 0;
        margin-bottom: 0;
    }
    /* Principalmente o container geral da página e os que estão dentro de colunas */
    .main .stVerticalBlock, .stColumn .stVerticalBlock {
        background-color: transparent;
        border: none;
        box-shadow: none;
        padding: 0;
        margin-bottom: 0; /* Ajuste para não adicionar margem extra */
    }
    /* Garante que o container de nível mais alto (depois do header) não tenha a margem padrão */
    .main > div > .stVerticalBlock {
        margin-bottom: 0;
    }
    .stVerticalBlockBorderWrapper > div {
        border: 0px solid #e9ecef;
        border-radius: 0px;
        padding: 0px;
        background-color: #f8f9fa;
    }
    /* Fim do estilo padrão para st.container */
    .main .block-container h1 {
        font-family: var(--streamlit-font-family) !important;
        color: var(--section-title-color) !important;
        font-weight: bold !important;
        font-size: 2.2em !important;
        margin-bottom: 1.5rem !important;
    }
    .stMainBlockContainer {
        background-color: #daeaf0 !important;
    }
    .client-management-header {
        display: flex; justify-content: space-between; align-items: flex-end; padding: 0 1rem; flex-wrap: wrap;
    }
    .client-management-header .left-side {
        display: flex; align-items: flex-end; gap: 15px; flex-wrap: wrap;
    }
    .client-management-header .title-block {
        display: flex; align-items: center; gap: 15px;
    }
    .client-management-header h2 {
        font-size: 1.8rem; font-weight: bold; color: var(--section-title-color); margin-bottom: 0;
    }
    .client-management-header .stSelectbox {
        min-width: 180px;
    }
    .pagination-container {
        display: flex; justify-content: center; align-items: center; padding: 15px 0; font-size: 1rem; gap: 10px;
    }
    .total-clients {
        font-size: 1rem; color: #555; text-align: right; padding-right: 1rem;
    }
    .client-table {
        width: 100%; border-collapse: collapse; font-size: 0.9em; color: #555; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .client-table th, .client-table td {
        padding: 12px 15px; text-align: left; vertical-align: middle;
    }
    .client-table thead tr {
        background-color: var(--franchisee-main-color); color: white; font-size: 1.1em; font-weight: bold;
    }
    .client-table tbody tr {
        border-bottom: 1px solid var(--table-border-color);
    }
    .client-table tbody tr:nth-of-type(even) {
        background-color: #f8f9fa;
    }
    .client-table tbody tr:last-of-type {
        border-bottom: 2px solid var(--franchisee-main-color);
    }
    .client-table tbody tr a {
        color: #0056b3; font-weight: 500; text-decoration: none;
    }
    .client-table tbody tr a:hover { text-decoration: underline; }
    .client-table .action-icons img { width: 25px; height: 25px; margin: 0 5px; cursor: pointer; transition: transform 0.2s; }
    .client-table .action-icons img:hover { transform: scale(1.1); }
    .client-table .material-icons { vertical-align: middle; font-size: 1.5rem; }
    .client-table .active-icon { color: #28a745; }
    .client-table .inactive-icon { color: #dc3545; }

    .section-title {
        font-family: var(--streamlit-font-family) !important; font-size: 1.6em !important; font-weight: 700 !important; color: var(--section-title-color) !important; margin-top: 30px !important; margin-bottom: 20px !important; display: flex; align-items: center;
    }
    .tooltip-icon {
        font-family: 'Material Icons'; font-size: 1.5rem !important; color: var(--label-text-color); margin-left: 10px !important; cursor: help; vertical-align: middle;
    }
    .tooltip-icon:hover { color: var(--franchisee-main-color); }
    
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stDateInput > div > div > input, .stTextArea > div > div > textarea, div[data-baseweb="select"] > div {
        font-family: var(--streamlit-font-family) !important; font-size: 1em !important; font-weight: 400 !important; color: var(--input-text-color) !important; background-color: var(--input-bg-color) !important; border: 1px solid var(--input-border-color) !important; border-radius: 5px !important; box-shadow: 0 1px 1px rgba(0,0,0,0.075) inset !important; height: 42px !important; box-sizing: border-box;
    }
    .stTextArea > div > div > textarea { height: auto !important; min-height: 84px !important; }
    div[data-baseweb="select"] input { font-size: 1em !important; }
    div[data-baseweb="select"] svg { fill: var(--input-text-color) !important; }

    .stTextInput > label, .stNumberInput > label, .stDateInput > label, .stTextArea > label, .stSelectbox > label, .stCheckbox > label {
        font-family: var(--streamlit-font-family) !important; font-size: 1.05em !important; font-weight: 700 !important; color: var(--label-text-color) !important; margin-bottom: 6px !important; display: block !important; padding-left: 0px !important;
    }
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p {
        font-weight: 400 !important; color: var(--input-text-color) !important; font-size: 1.05em !important;
    }
    
    /* --- INÍCIO: NOVOS ESTILOS PARA BOTÕES PADRÃO --- */
    div[data-testid="stButton"] > button {
        background-color: var(--franchisee-main-color);
        color: var(--button-text-color);
        border: 2px solid var(--franchisee-main-color);
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s ease-in-out;
    }

    div[data-testid="stButton"] > button:hover {
        background-color: white;
        color: var(--franchisee-main-color);
        border: 2px solid var(--franchisee-main-color);
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    /* --- FIM: NOVOS ESTILOS PARA BOTÕES PADRÃO --- */

    /* Estilo para botão primário dentro de formulários (seu estilo original) */
    .stForm .stButton button[kind="primary"] {
        font-family: var(--streamlit-font-family) !important;
        background-color: var(--franchisee-main-color) !important;
        color: var(--button-text-color) !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 1.1em !important;
    }
    
    hr {
        border: none; border-top: 1px solid #ddd; margin-top: 2rem !important; margin-bottom: 2rem !important;
    }

    details > summary {
      list-style: none;
    }
    details > summary::-webkit-details-marker {
      display: none;
    }
    
    details > summary {
        cursor: pointer;
        padding: 8px 15px;
        background-color: #f0f2f6;
        border-radius: 5px;
        font-weight: 500;
        color: #262730;
        margin: 5px;
        display: inline-block;
        transition: background-color 0.2s;
    }

    details > summary:hover {
        background-color: #e6e8eb;
    }

    .details-cell {
        padding: 0 !important;
        background-color: #fafafa;
    }
    
    .details-cell > div {
        padding-left: 15px !important;
    }
    
    .vehicle-table {
        width: 100%; border-collapse: collapse; margin: 0; border: none;
    }
    .vehicle-table th, .vehicle-table td {
        border: none; border-top: 1px solid #ddd; padding: 10px 25px; text-align: left;
    }
    .vehicle-table th {
        background-color: #e9ecef; font-weight: bold; color: #495057;
    }

    .tooltip-container {
        position: relative; display: inline-block;
    }
    .tooltip {
        visibility: hidden; width: 200px; background-color: #333; color: white; text-align: center; border-radius: 6px; padding: 8px; position: absolute; z-index: 999999; bottom: 125%; left: 50%; margin-left: -100px; opacity: 0; transition: opacity 0.3s; font-size: 14px; pointer-events: none; box-shadow: 0 4px 15px rgba(0,0,0,0.4); white-space: normal; word-wrap: break-word; line-height: 1.3; transform: translateZ(0); will-change: opacity;
    }
    .tooltip::after {
        content: ""; position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #333 transparent transparent transparent;
    }
    .tooltip-container:hover .tooltip {
        visibility: visible; opacity: 1; transform: translateZ(0) scale(1);
    }
    </style>
"""
    st.markdown(custom_css, unsafe_allow_html=True)


def get_cabecalho(user_name):
    greeting = "Bom dia" if datetime.now().hour < 12 else "Boa tarde" if datetime.now().hour < 18 else "Boa noite"
    return f"""
<style>
/* Importa a fonte de ícones do Google (Material Icons) */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

/* Estilos gerais do container do cabeçalho */
.header-container {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #0b3747; /* Cor de fundo azul escuro do original */
    padding: 10px 25px;
    border-radius: 10px;
    color: white;
    font-family: Arial, sans-serif;
    margin-bottom: 2rem;
    height: 150px; /* Altura fixa para corresponder ao exemplo */
}}
/* Seção do logo, saudação e menu (lado esquerdo) */
.logo-section {{
    display: flex;
    align-items: center;
    gap: 15px; /* Espaçamento entre os elementos */
}}
.greeting-logo-wrapper {{
    display: flex;
    flex-direction: column; /* Coloca a saudação acima do logo */
    align-items: flex-start; /* Alinha à esquerda */
    gap: 5px;
}}
.greeting-text {{
    font-size: 16px;
    font-weight: 700;
    text-shadow: 1px 1px 1px #333;
}}
.logo-box {{
    background-color: #ececec;
    border-radius: 12px;
    padding: 10px;
    width: 150px; /* Largura ajustada */
    height: 75px; /* Altura ajustada */
    display: flex;
    align-items: center;
    justify-content: center;
}}
.logo-box img {{
    max-width: 100%;
    max-height: 100%;
}}
.divider {{
    height: 80px;
    border-left: 1px solid white;
}}
a.home-btn {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    color: white;
    border: 2px solid white;
    border-radius: 10px;
    padding: 4px;
    background-color: #7a7b43;
    text-decoration: none;
    width: 65px;
    height: 65px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
a.home-btn:hover {{
    background-color: #5a5b33;
    transform: translateY(-6px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}}
a.home-btn .material-icons {{ font-size: 30px; }}
a.home-btn span {{ font-size: 13px; font-weight: 700; }}
/* Seção dos botões de navegação (lado direito) */
.nav-buttons {{
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    flex-grow: 1; /* Permite que o container ocupe o espaço restante */
}}
/* Estilo base para cada botão de navegação */
a.nav-btn {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 18px; /* Padding aumentado para botões maiores */
    border: 3px solid black;
    border-radius: 15px; /* Bordas mais arredondadas */
    color: black;
    text-decoration: none;
    font-weight: 700;
    font-size: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
a.nav-btn:hover {{
    transform: translateY(-6px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    color: white;
    border: 3px solid white;
}}
/* Ícones dentro dos botões */
a.nav-btn .material-icons {{
    font-size: 32px;
}}
/* Cores específicas para cada botão, como no original */
.btn-maintenance {{ background-color: #a77a24; }}
.btn-panel {{ background-color: #2f073b; }}
.btn-financial {{ background-color: #2344a4; }}
.btn-financial-ag {{ background-color: #2344a4; }}
.btn-communication {{ background-color: #206e8c; }}
.btn-web {{ background-color: #583e23; }}
.btn-logout {{ background-color: red; }}
.btn-logout .material-icons {{ font-size: 24px; }}
.btn-falha-sinal {{ background-color: #8B0000; }}

</style>
<header class="header-container">
    <!-- Lado Esquerdo: Logo, Saudação e Menu -->
    <div class="logo-section">
        <div class="greeting-logo-wrapper">
            <p class="greeting-text">{greeting}, {user_name}!</p>
            <div class="logo-box">
                <img src="https://sisras-logos.s3.sa-east-1.amazonaws.com/globalsystem3.jpg" alt="Logo Global System">
            </div>
        </div>
        <div class="divider"></div>
        <a href="/?go_home=true" target="_self" class="home-btn">
            <span class="material-icons">home</span>
            <span>Menu</span>
        </a>
    </div>
    <nav class="nav-buttons">
        <a href="https://sistemafalhasinal-production.up.railway.app" class="nav-btn btn-falha-sinal">
            <span class="material-icons">signal_cellular_connected_no_internet_0_bar</span>
            <span>Falha de Sinal</span>
        </a>
        <a href="https://globalsystem.plataforma.app.br/maintenance-management" class="nav-btn btn-maintenance">
            <span class="material-icons">build</span>
            <span>Manutenções</span>
        </a>
        <a href="https://globalsystem.plataforma.app.br/financeiro" class="nav-btn btn-financial">
            <span class="material-icons">account_balance</span>
            <span>Financeiro Nexo</span>
        </a>
        <a href="https://agendamento-boletos.up.railway.app" class="nav-btn btn-financial-ag">
            <span class="material-icons">event_available</span>
            <span>Financeiro AG</span>
        </a>
        <a href="https://globalsystem.plataforma.app.br/web/franqueado" class="nav-btn btn-web">
            <span class="material-icons">person</span>
            <span>Web</span>
        </a>
        <a href="https://globalsystem.plataforma.app.br/panel" class="nav-btn btn-panel">
            <span class="material-icons">apps</span>
            <span>Painel</span>
        </a>
        <a href="/?logout=true" target="_self" class="nav-btn btn-logout">
            <span>Sair</span>
            <span class="material-icons">exit_to_app</span>
        </a>
    </nav>
</header>
"""