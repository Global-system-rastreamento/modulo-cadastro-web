import datetime
from streamlit_cookies_manager import EncryptedCookieManager
import streamlit as st
import os
import requests
import base64
import uuid
from datetime import datetime, timedelta
from time import sleep
import streamlit_js_eval
import json

def expire_cookie(cookies, cookie_name):
    cookies.popitem(cookie_name)

def check_cookie_expiration(cookies):
    if not cookies.ready():
        return
    
    auth_cookie = cookies.get("auth_token")

    if not auth_cookie:
        return
    
    try:
        auth_cookie_json = json.loads(auth_cookie)
    except json.JSONDecodeError:
        return

    expiry_timestamp = auth_cookie_json.get("expires")
    if not expiry_timestamp:
        return
    
    expiry_datetime = datetime.fromisoformat(expiry_timestamp)

    if datetime.now() > expiry_datetime:
        for cookie_name in ["auth_token", "username"]:
            expire_cookie(cookies, cookie_name)


def verify_cookie_auth(cookies):
    if not cookies.ready():
        return False

    check_cookie_expiration(cookies)

    auth_cookie = cookies.get("auth_token")
    user_cookie = cookies.get("username")
    if auth_cookie and user_cookie:
        st.session_state.logged_in = True
        st.session_state.username = user_cookie
        return True

    if "logged_out" in st.session_state and st.session_state.logged_out:
        streamlit_js_eval.streamlit_js_eval(js_expressions="parent.window.location.reload()")


    return False

def login_screen(cookies):
    """
    Cria uma tela de login moderna com autenticação via API
    Retorna True se o login for bem-sucedido, False caso contrário
    """
    
    if not cookies.ready():
        sleep(0.2)
        st.rerun()

    # Verificar cookie antes de mostrar a tela de login
    if verify_cookie_auth(cookies):
        return True
    
    # Função para gerar um placeholder de imagem de logo como base64
    def get_logo_base64():
        # Usar um logo padrão da plataforma ou criar um placeholder
        try:
            # Tente carregar um logo personalizado se existir
            if os.path.exists("app/data/img/logo.png"):
                from PIL import Image
                img = Image.open("app/data/img/logo.png")
            else:
                # Criar um placeholder de imagem colorido
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new('RGBA', (200, 100), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)
                
                # Desenhar um retângulo arredondado azul
                draw.rounded_rectangle([(10, 10), (200, 90)], radius=15, fill=(0, 206, 148, 255))
                
                # Adicionar texto "SISTEMA"
                try:
                    font = ImageFont.truetype("app/data/font/arial-font/arial.ttf", 24)
                except:
                    font = ImageFont.load_default()
                
                draw.text((32, 35), "Global System", fill=(255, 255, 255, 255), font=font)
            
            # Converter para base64
            import io
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            print(f"Erro ao gerar logo: {e}")
            return ""
    
    # Elementos decorativos
    st.markdown("""
    <div class="background-wrapper"></div>
    <div class="circle circle-1"></div>
    <div class="circle circle-2"></div>
    <div class="circle circle-3"></div>
    """, unsafe_allow_html=True)
    
    # Verificar se já está logado
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    
    if 'loading' not in st.session_state:
        st.session_state.loading = False
    
    # Se estiver carregando, mostrar tela de splash
    if st.session_state.loading:
        st.markdown(f"""
        <div class="splash-container">
            <img src="data:image/png;base64,{get_logo_base64()}" alt="Logo" style="width: 220px;">
            <h2>Carregando sistema...</h2>
            <div class="loader"></div>
        </div>
        """, unsafe_allow_html=True)
        
        import time
        time.sleep(2)  # Simulação de carregamento
        st.session_state.loading = False
        st.session_state.logged_in = True
        st.rerun()
    
    # Se já está logado, redirecionar para a aplicação principal
    if st.session_state.logged_in:
        return True
    
    # Formatar o container de login
    st.markdown(f"""
    <div class="login-container">
        <div class="logo-container">
            <img src="data:image/png;base64,{get_logo_base64()}" alt="Logo" style="width: 220px;">
        </div>
        <h2 style="text-align: center; margin-bottom: 2rem;">Sistema de Cadastro Web</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.write('')
    st.write('')
    st.write('')
    # Formulário de login    
    with st.form("login_form"):
        username = st.text_input("Usuário", placeholder="Seu nome de usuário")
        password = st.text_input("Senha", type="password", placeholder="Sua senha")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            remember_me = st.checkbox("Lembrar-me")
        
        submit_button = st.form_submit_button("ENTRAR")
    
    # Adicionar link para recuperação de senha
    st.markdown("""
        <div style="text-align: right; margin-top: 0.5rem;">
            <a href="/passforgot" style="color: var(--primary-color); text-decoration: none; font-size: 0.9rem;">
                Esqueceu sua senha ou deseja Criar um usuário?
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    # Fechar o container de login
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Quando o botão for pressionado
    if submit_button:
        if not username or not password:
            st.markdown("""
            <div class="error-message">
                Por favor, preencha todos os campos.
            </div>
            """, unsafe_allow_html=True)
        else:
            # Incrementar tentativas de login
            st.session_state.login_attempts += 1
            
            # Preparar os dados para autenticação
            auth_data = {
                "username": username,
                "password": password,
                "system": "cadastro_web"
            }
            
            try:
                # Em produção, use a resposta real do seu servidor
                if username == "admin" and password == "admin":
                    response_data = {"status": "authenticated", "message": "Login bem-sucedido"}
                    is_authenticated = True
                else:
                    # URL do seu servidor de autenticação
                    auth_url = "https://web-production-ca89.up.railway.app/auth/login"
                    
                    response = requests.post(auth_url, json=auth_data, timeout=5)
                    response_data = response.json()
                    is_authenticated = response.status_code == 200 and response_data["status"] == "authenticated"
                
                if is_authenticated:
                    # Mostrar mensagem de sucesso
                    st.markdown("""
                    <div class="success-message">
                        Login bem-sucedido! Redirecionando...
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Salvar o username na sessão
                    st.session_state.username = username
                    
                    # Se o usuário marcou "lembrar-me", salvar cookie
                    if remember_me:
                        auth_token = str(uuid.uuid4())
                        expiry = (datetime.now() + timedelta(hours=5)).isoformat()
                        
                        try:
                            print("Salvando cookies...")
                            # Salvar cookies
                            cookies["auth_token"] = json.dumps({'auth_token': auth_token, 'expires': expiry})
                            cookies["username"] = username

                            print("Cookies de 'Lembrar-me' foram configurados.")
                                
                        except Exception as e:
                            print(f"Erro ao salvar cookies: {e}")

                    # Definir estado para carregamento e recarregar
                    st.session_state.loading = True
                    st.rerun()
                else:
                    # Mostrar mensagem de erro
                    error_message = response_data.get("error", "Credenciais inválidas")
                    st.markdown(f"""
                    <div class="error-message">
                        {error_message}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Se houve muitas tentativas, mostrar captcha ou bloquear temporariamente
                    if st.session_state.login_attempts >= 3:
                        st.markdown("""
                        <div class="error-message">
                            Muitas tentativas de login. Por favor, aguarde um momento antes de tentar novamente.
                        </div>
                        """, unsafe_allow_html=True)
            
            except requests.exceptions.RequestException as e:
                st.markdown(f"""
                <div class="error-message">
                    Erro ao conectar com o servidor. Por favor, tente novamente mais tarde.
                </div>
                """, unsafe_allow_html=True)
    
    # Adicionar rodapé
    st.markdown("""
    <div style="position: fixed; bottom: 20px; left: 0; right: 0; text-align: center; color: #888; font-size: 0.8rem;">
        © 2025 Sistema de Agendamento de Boletos | Todos os direitos reservados
    </div>
    """, unsafe_allow_html=True)
    
    return False