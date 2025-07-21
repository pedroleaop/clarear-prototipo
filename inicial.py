import streamlit as st
import time

# --- Configurações Iniciais da Página ---
st.set_page_config(
    page_title="ClareAR: Bem-vindo(a)!",
    page_icon="🧠",
    layout="centered"
)

# --- URL da Imagem do Cabeçalho (a mesma do clarear.py) ---
HEADER_IMAGE_URL = "https://iili.io/F3E96dP.png"

# --- CSS para Estilo Pastel (Copiar do clarear.py para consistência) ---
# É crucial que as cores e estilos visuais sejam consistentes em ambas as páginas.
# Este bloco de estilo deve ser IDÊNTICO ao do clarear.py.

st.markdown(
    """
    <style>
    /* Cores Pastéis (Azul e Laranja) */
    :root {
        --pastel-blue-light: #D4EEF2; /* Fundo geral: Azul bem clarinho */
        --pastel-blue-medium: #A2D9EE; /* Balões do ClareAR / Destaques: Azul um pouco mais forte */
        --pastel-orange-light: #FFECB3; /* Laranja suave */
        --pastel-orange-medium: #FFB74D; /* Botões / Acentos: Laranja um pouco mais forte */
        --pastel-gray-light: #F0F0F0; /* Fundo dos balões do usuário: Cinza claro */
        --text-color-dark: #333333; /* Cor do texto principal (quase preto) */
        --text-color-light: #555555; /* Cor do texto secundário / placeholder */
        --sidebar-bg: #E3F2FD; /* Fundo da sidebar: Azul mais clarinho que o fundo geral */
    }

    /* Fundo da Página Principal */
    .stApp {
        background-color: var(--pastel-blue-light);
        color: var(--text-color-dark);
    }

    /* Estilo dos Balões de Conversa */
    /* Estas regras podem não ser totalmente aplicáveis aqui, mas mantemos para consistência */
    .stChatMessage {
        background-color: transparent; 
    }
    .stChatMessage [data-testid="stChatMessageContent"] {
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
        font-size: 16px;
        line-height: 1.5;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        color: var(--text-color-dark);
    }
    .stChatMessage [data-testid="stChatMessageContent"]:first-child {
        background-color: var(--pastel-blue-medium);
        border-bottom-left-radius: 5px; 
    }
    .stChatMessage [data-testid="stChatMessageContent"]:last-child {
        background-color: var(--pastel-gray-light);
        color: var(--text-color-dark);
        font-weight: bold;
        border-bottom-right-radius: 5px; 
    }
    
    /* Input de Texto Genérico (para esta página inicial) */
    .stTextInput>div>div>input {
        background-color: white; 
        border-radius: 20px;
        padding: 10px 15px;
        box-shadow: 0px 0px 8px rgba(0,0,0,0.15);
        color: var(--text-color-dark);
        font-weight: bold;
        border: 1px solid rgba(0,0,0,0.1); /* Borda sutil */
    }
    .stButton>button {
        background-color: var(--pastel-orange-medium); 
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #FF8A65; 
    }


    /* Sidebar - Pode não ser exibido aqui, mas para consistência */
    .stSidebar {
        background-color: var(--sidebar-bg);
        color: var(--text-color-dark);
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h6 { 
        color: var(--text-color-dark);
    }
    
    /* Centralizar imagem do cabeçalho */
    .header-image-container {
        display: flex;
        justify-content: center; 
        padding-top: 20px; 
        padding-bottom: 20px; 
        width: 100%; 
    }
    .header-image {
        max-width: 50% !important; 
        height: auto; 
        display: block; 
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Lógica da Página Inicial ---

# Exibir a imagem do cabeçalho
with st.container():
    st.markdown(
        f"""
        <div class="header-image-container">
            <img src="{HEADER_IMAGE_URL}" class="header-image">
        </div>
        """, unsafe_allow_html=True
    )

st.title("Bem-vindo(a) ao ClareAR!")
st.markdown("Seu assistente de reabilitação cognitiva personalizada.")

# Inicialização do estado da sessão para esta página
# Esta variável dirá se o usuário "logou"
if "logged_in_user_name" not in st.session_state:
    st.session_state.logged_in_user_name = None

# Se não estiver logado, pede o nome
if not st.session_state.logged_in_user_name:
    st.write("Para começar sua jornada de clareza mental, por favor, digite seu nome.")
    
    # Campo para o usuário digitar o nome
    user_name = st.text_input("Qual é o seu nome?", key="initial_name_input_field", label_visibility="collapsed")
    
    if st.button("Iniciar ClareAR"):
        if user_name.strip():
            st.session_state.logged_in_user_name = user_name.strip()
            # Ao definir logged_in_user_name e recarregar,
            # Streamlit irá para a próxima página no menu (clarear.py)
            st.rerun() # Força o Streamlit a recarregar para a próxima página
        else:
            st.error("Por favor, digite um nome para iniciar.")
else:
    # Se o usuário já "logou" (ou seja, logged_in_user_name já está definido),
    # mas a página inicial recarregou, força o redirecionamento para o dashboard.
    # Isso evita que o usuário fique preso aqui.
    st.rerun()