import streamlit as st
import random
import time
import os
# import google.generativeai as genai # COMENTADO: Não precisamos do Gemini API por enquanto
from gtts import gTTS 
import io 
import pandas as pd
import base64 

# --- Configurações Iniciais do Aplicativo ---
st.set_page_config(
    page_title="ClareAR: Reabilitação Cognitiva Personalizada",
    page_icon="🧠",
    layout="centered"
)

# --- URL da Imagem do Cabeçalho ---
HEADER_IMAGE_URL = "https://iili.io/F3E96dP.png"

# --- CSS para Estilo Pastel (Copiar do inicial.py para consistência) ---
# Este bloco de estilo deve ser IDÊNTICO ao do inicial.py.

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
        color: var(--text-color-dark); /* Texto dos balões em preto suave */
    }

    /* Mensagens do ClareAR (Role "ClareAR") */
    .stChatMessage [data-testid="stChatMessageContent"]:first-child {
        background-color: var(--pastel-blue-medium); /* Azul suave para o bot */
        border-bottom-left-radius: 5px; 
    }

    /* Mensagens do Usuário (Role "user") */
    .stChatMessage [data-testid="stChatMessageContent"]:last-child {
        background-color: var(--pastel-gray-light); /* Cinza claro para o usuário */
        color: var(--text-color-dark); /* Letra preta para o usuário */
        font-weight: bold; /* Negrito para mensagens do usuário */
        border-bottom-right-radius: 5px; 
    }
    
    /* Input de Chat */
    [data-testid="stChatInput"] {
        background-color: white; 
        border-radius: 20px;
        padding: 5px 10px;
        box-shadow: 0px 0px 8px rgba(0,0,0,0.15);
    }
    [data-testid="stChatInput"] input {
        color: var(--text-color-dark); /* Texto digitado em preto suave */
        font-weight: bold; /* Negrito para o que o usuário digita */
    }
    [data-testid="stChatInput"] button {
        background-color: var(--pastel-orange-medium); 
        color: white;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 20px;
        border: none;
    }
    [data-testid="stChatInput"] button:hover {
        background-color: #FF8A65; 
    }

    /* Sidebar */
    .stSidebar {
        background-color: var(--sidebar-bg);
        color: var(--text-color-dark);
        padding: 20px;
        border-right: 1px solid rgba(0,0,0,0.05);
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h6 { 
        color: var(--text-color-dark);
    }
    .stSidebar .stDataFrame {
        background-color: rgba(255,255,255,0.7);
        border-radius: 10px;
        color: var(--text-color-dark);
    }
    .stSidebar .stDataFrame .header {
        background-color: var(--pastel-blue-medium); 
        color: white;
    }
    .stSidebar .stDataFrame td {
        color: var(--text-color-dark);
    }

    /* Cores das barras de progresso (hack de CSS para a div interna) */
    .stProgress > div > div > div > div[data-testid^="stProgressAnimatedBackground"] {
        background-color: transparent !important; 
    }

    /* Cores da barra de progresso personalizada */
    .stProgress[data-testid^="stProgress"] > div > div > div > div {
        background-color: #eee; 
    }

    /* Centralizar imagem do cabeçalho */
    .stImage {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-left: auto;
        margin-right: auto;
        padding-top: 20px; 
        padding-bottom: 20px; 
    }

    /* Estilo para o botão de áudio personalizado */
    .audio-button-container {
        text-align: right; 
        margin-top: 5px;
    }
    .audio-button {
        background-color: var(--pastel-orange-medium);
        color: white;
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        font-size: 16px;
        cursor: pointer;
        display: inline-flex; 
        justify-content: center;
        align-items: center;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .audio-button:hover {
        background-color: #FF8A65;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Configuração da API do Gemini (COMENTADO PARA DESATIVAR) ---
# api_key = os.getenv("GOOGLE_API_KEY")
# if not api_key:
#     st.error("Chave de API do Google Gemini não encontrada! (INTEGRAÇÃO DA IA DESATIVADA TEMPORARIAMENTE)")
#     st.stop() 
# genai.configure(api_key=api_key)
# model = genai.GenerativeModel('gemini-1.5-flash-latest') 

# --- Inicialização do Estado da Sessão (Crucial para Streamlit!) ---
# A página clarear.py (dashboard) só é acessada se o login_user_name já estiver definido.
# Se não estiver, redireciona de volta para a página inicial (inicial.py).
if "logged_in_user_name" not in st.session_state or not st.session_state.logged_in_user_name:
    st.warning("Por favor, faça o login na página inicial para acessar o dashboard.")
    if st.button("Ir para Página Inicial"):
        st.session_state.go_to_dashboard = False # Sinaliza para inicial.py que deve ser a próxima
        st.rerun() # Força o rerun para inicial.py
    st.stop() # Interrompe a execução desta página se não estiver logado

# Se chegou até aqui, o usuário está logado.
# Inicializa user_data APENAS SE AINDA NÃO FOI INICIALIZADO para esta sessão.
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "nome": st.session_state.logged_in_user_name, # Usa o nome do login
        "idade": "",
        "dificuldades": [], 
        "current_page": "main_dashboard", # Define a página atual como dashboard
        "current_stage": "ask_age", # Começa o fluxo do chat a partir da idade
        "active_exercise": None,     
        "exercise_data": {},         
        "performance_history": {}    
    }
# Mantenha esta checagem para pending_exercise_area separada da inicialização principal
if "pending_exercise_area" not in st.session_state:
    st.session_state.pending_exercise_area = None


# --- Funções de Áudio ---
def play_text_as_audio_button(text_to_speak, message_id):
    """
    Converte texto em fala e gera um botão de play.
    Associa o áudio a um ID único para reprodução via JavaScript.
    """
    try:
        tts = gTTS(text=text_to_speak, lang='pt', slow=False) 
        fp = io.BytesIO() 
        tts.write_to_fp(fp)
        fp.seek(0) 
        
        audio_data_base64 = base64.b64encode(fp.read()).decode('utf-8')
        audio_data_url = f"data:audio/mp3;base64,{audio_data_base64}"

        st.markdown(
            f"""
            <div class="audio-button-container">
                <button class="audio-button" onclick="document.getElementById('audio_player_{message_id}').play()">
                    ▶️
                </button>
            </div>
            <audio id="audio_player_{message_id}" src="{audio_data_url}" style="display:none;"></audio>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        print(f"Erro ao gerar/reproduzir áudio para botão: {e}. Texto: '{text_to_speak}'")
        st.error(f"Erro ao gerar áudio para esta mensagem. Por favor, leia o texto.") 

def send_message_to_clarear(message_content, role="ClareAR", with_audio_button=True):
    """
    Adiciona uma mensagem ao histórico, exibe-a.
    Se for do ClareAR e with_audio_button for True, adiciona um botão de áudio.
    """
    with st.chat_message(role):
        st.markdown(message_content)
        if role == "ClareAR" and with_audio_button:
            message_id = hash(message_content + str(time.time())) 
            play_text_as_audio_button(message_content, message_id)
            time.sleep(0.1) 

    st.session_state.messages.append({"role": role, "content": message_content})
    

# --- Funções de Simulação de IA (para testes sem API) ---
def generate_simulated_exercise(difficulty_area):
    """
    Simula a geração de um exercício por IA, sem chamar a API.
    Retorna exercícios fixos para fins de demonstração.
    """
    exercises_by_domain = {
        "memória": [
            {"name": "Sequência de Palavras Simples", "instructions": "Memorize a sequência de palavras.", "content": "Sol, Céu, Flor, Rio", "domain": "memória", "expected_answer": "sol, céu, flor, rio"},
            {"name": "Lembre-se da Lista de Compras", "instructions": "Memorize a lista e depois digite-a.", "content": "Pão, Leite, Ovos, Café, Frutas", "domain": "memória", "expected_answer": "pão, leite, ovos, café, frutas"},
        ],
        "atenção": [
            {"name": "Contagem de Vogais", "instructions": "Quantas vogais (a, e, i, o, u) existem na frase a seguir?", "content": "A águia voa alto sobre a montanha.", "domain": "atenção", "expected_answer": "12"},
            {"name": "Encontre o Número Faltante", "instructions": "Qual número está faltando na sequência: 1, 2, 3, __, 5, 6?", "content": "1, 2, 3, 4, 5, 6", "domain": "atenção", "expected_answer": "4"}, 
        ],
        "raciocínio": [
            {"name": "Charada Básica", "instructions": "O que é, o que é: Anda e não tem pés, voa e não tem asas?", "content": "O que é, o que é: Anda e não tem pés, voa e não tem asas?", "domain": "raciocínio", "expected_answer": "fumaça"},
            {"name": "Padrão Numérico Simples", "instructions": "Continue a sequência lógica: 3, 6, 9, 12, __?", "content": "3, 6, 9, 12", "domain": "raciocínio", "expected_answer": "15"}, 
        ],
        "orientação": [
            {"name": "Orientação Temporal", "instructions": "Qual é o dia da semana hoje?", "content": "Qual é o dia da semana hoje?", "domain": "orientação", "expected_answer": time.strftime("%A").lower()}, # Resposta dinâmica
            {"name": "Orientação Espacial", "instructions": "Em que cidade você está agora?", "content": "Em que cidade você está agora?", "domain": "orientação", "expected_answer": "recife"} 
        ]
    }
    return random.choice(exercises_by_domain.get(difficulty_area.lower(), exercises_by_domain["memória"])) 

def generate_simulated_feedback(performance, exercise_name, user_response, expected_answer):
    """
    Simula feedback, sem chamar a API.
    """
    if performance == "correct":
        return f"Parabéns! Você acertou o exercício '{exercise_name}'. Excelente desempenho! Sua resposta '{user_response}' está correta."
    else:
        return f"Tudo bem, às vezes erramos! Você respondeu '{user_response}', mas a resposta esperada era '{expected_answer}'. A prática leva à perfeição. Que tal tentar outro?"

def generate_gemini_exercise(difficulty_area, user_age, user_difficulties):
    return generate_simulated_exercise(difficulty_area) 

def generate_gemini_feedback(performance, exercise_name, user_response, expected_answer):
    return generate_simulated_feedback(performance, exercise_name, user_response, expected_answer) 


def update_performance_history(exercise_name, domain, result):
    """Atualiza o histórico de desempenho do usuário."""
    if domain not in st.session_state.user_data["performance_history"]:
        st.session_state.user_data["performance_history"][domain] = {"attempts": 0, "correct": 0}
    
    st.session_state.user_data["performance_history"][domain]["attempts"] += 1
    if result == "correct":
        st.session_state.user_data["performance_history"][domain]["correct"] += 1
    
    print(f"Performance history updated: {st.session_state.user_data['performance_history']}")


# --- Nova Função para Exibir o Painel de Progresso ---
def display_progress_panel():
    st.sidebar.markdown("---")
    st.sidebar.header("📈 Seu Progresso no ClareAR")

    print(f"Displaying progress. Current history: {st.session_state.user_data.get('performance_history', 'Not initialized')}")

    if not st.session_state.user_data.get("performance_history"): 
        st.sidebar.info("Comece a resolver exercícios para ver seu progresso aqui!")
    else:
        progress_data = []
        for domain, data in st.session_state.user_data["performance_history"].items():
            if data["attempts"] > 0:
                accuracy = (data["correct"] / data["attempts"]) * 100
                progress_data.append({"Domínio": domain.capitalize(), "Acerto (%)": accuracy, "Tentativas": data["attempts"]})
        
        if progress_data:
            df_progress = pd.DataFrame(progress_data)
            
            st.sidebar.markdown("#### Acertos por Domínio")
            st.sidebar.dataframe(df_progress.set_index("Domínio"))

            st.sidebar.markdown("#### Visualização da Performance")
            for index, row in df_progress.iterrows():
                domain = row["Domínio"]
                accuracy = row["Acerto (%)"]
                attempts = row["Tentativas"]

                color_bg = "#eee" 
                color_fill = ""
                if accuracy >= 70:
                    color_fill = "#8BC34A" # Verde pastel
                elif accuracy >= 40:
                    color_fill = "#FFC107" # Laranja/Amarelo pastel
                else:
                    color_fill = "#FF5722" # Vermelho/Laranja mais forte pastel
                
                st.sidebar.markdown(
                    f"**{domain}**: {accuracy:.1f}% de acerto em {attempts} tentativas"
                )
                
                st.sidebar.markdown(f"""
                <div style="width: 100%; background-color: {color_bg}; border-radius: 5px;">
                    <div style="width: {accuracy}%; background-color: {color_fill}; height: 10px; border-radius: 5px;"></div>
                </div>
                """, unsafe_allow_html=True)
                st.sidebar.write("\n") 

        st.sidebar.markdown("---")
        st.sidebar.success("Continue treinando para melhorar ainda mais!")
    
    st.sidebar.markdown("---")


# --- Lógica Principal do Aplicativo ---

# Exibir a imagem do cabeçalho com largura menor e CENTRALIZADA
with st.container():
    st.markdown(
        f"""
        <style>
            .header-image-container {{
                display: flex;
                justify-content: center; 
                padding-top: 20px; 
                padding-bottom: 20px; 
            }}
            .header-image {{
                max-width: 50% !important; /* Força a largura máxima para 50% do container */
                height: auto; 
                display: block; 
            }}
        </style>
        <div class="header-image-container">
            <img src="{HEADER_IMAGE_URL}" class="header-image">
        </div>
        """, unsafe_allow_html=True
    )

# Este bloco verifica se o usuário está logado para exibir o dashboard.
# Ele substitui o antigo "if current_page == main_dashboard"
if "logged_in_user_name" not in st.session_state or not st.session_state.logged_in_user_name:
    st.warning("Por favor, faça o login na página inicial para acessar o dashboard.")
    if st.button("Ir para Página Inicial"):
        # st.session_state.go_to_dashboard = False (já manipulado pela estrutura multi-page)
        st.stop() # Interrompe a execução aqui. O Streamlit vai para a home automaticamente.
    st.stop() # Interrompe a execução desta página se não estiver logado.

# Se chegou até aqui, o usuário está logado.
# Inicializa user_data APENAS SE AINDA NÃO FOI INICIALIZADO para esta sessão.
# Isso garante que o nome do usuário vindo da inicial.py seja usado.
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "nome": st.session_state.logged_in_user_name, # Usa o nome do login
        "idade": "",
        "dificuldades": [], 
        "current_stage": "ask_age", # Começa o fluxo do chat a partir da idade
        "active_exercise": None,     
        "exercise_data": {},         
        "performance_history": {}    
    }
# Mantenha esta checagem para pending_exercise_area separada da inicialização principal
if "pending_exercise_area" not in st.session_state:
    st.session_state.pending_exercise_area = None

# EXIBIR O PAINEL DE PROGESSO PRIMEIRO (na barra lateral)
display_progress_panel()

# Exibir mensagens anteriores do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Lógica do chat principal do dashboard
# A partir daqui, as mensagens são processadas como um chat contínuo
# A primeira mensagem dependerá do current_stage
if st.session_state.user_data["current_stage"] == "ask_age" and not st.session_state.user_data["idade"]:
    send_message_to_clarear(f"Olá, {st.session_state.user_data['nome']}! Bem-vindo(a) ao seu dashboard. Qual é a sua idade?", with_audio_button=True)
    # st.session_state.user_data["current_stage"] permanece "ask_age" até que a idade seja digitada

# Campo de entrada do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Lógica de processamento da entrada do usuário
    if st.session_state.user_data["current_stage"] == "ask_age":
        try:
            age = int(prompt.strip())
            st.session_state.user_data["idade"] = age
            send_message_to_clarear("Excelente! Agora, para personalizar seus exercícios, quais áreas cognitivas você sente mais dificuldade? (Ex: memória, atenção, raciocínio, orientação)", with_audio_button=True)
            st.session_state.user_data["current_stage"] = "ask_difficulties"
        except ValueError:
            send_message_to_clarear("Por favor, digite uma idade válida (apenas números).", with_audio_button=True)

    elif st.session_state.user_data["current_stage"] == "ask_difficulties":
        difficulties_input = [d.strip().lower() for d in prompt.split(',') if d.strip()]
        st.session_state.user_data["dificuldades"] = difficulties_input
        st.session_state.user_info_collected = True # Define que a info inicial foi coletada
        
        if difficulties_input:
            first_difficulty = difficulties_input[0]
            st.session_state.pending_exercise_area = first_difficulty 
            
            # Ajuste de fluxo: se já disser 'sim' ou o tipo no input de dificuldades, avança
            if "sim" in prompt.lower() or any(area in prompt.lower() for area in ["memória", "atenção", "raciocínio", "orientação"]):
                st.session_state.user_data["current_stage"] = "confirm_initial_exercise" 
                st.rerun() 
            else:
                send_message_to_clarear(f"Ótimo! Entendi que você quer focar em **{', '.join(difficulties_input)}**.", with_audio_button=True)
                time.sleep(1)
                send_message_to_clarear(f"Que tal começarmos com um exercício de **{first_difficulty.capitalize()}**? Digite 'sim' para começar!", with_audio_button=True)
                st.session_state.user_data["current_stage"] = "confirm_initial_exercise"
        else:
            send_message_to_clarear("Por favor, me diga pelo menos uma área de dificuldade para eu poder ajudar.", with_audio_button=True)
            st.session_state.user_data["current_stage"] = "ask_difficulties" 

    elif st.session_state.user_data["current_stage"] == "confirm_initial_exercise":
        if "sim" in prompt.lower() and st.session_state.pending_exercise_area: 
            area_to_focus = st.session_state.pending_exercise_area 
            st.session_state.pending_exercise_area = None 
            
            with st.spinner(f"Gerando um exercício de {area_to_focus.capitalize()}..."):
                exercise_details = generate_simulated_exercise(area_to_focus)
            
            if exercise_details:
                st.session_state.user_data["active_exercise"] = exercise_details["name"]
                st.session_state.user_data["exercise_data"] = exercise_details
                send_message_to_clarear(f"Certo! Vamos lá para o exercício de **{exercise_details['domain'].capitalize()}**: '{exercise_details['name']}'.", with_audio_button=True)
                time.sleep(0.5)
                send_message_to_clarear(exercise_details["instructions"], with_audio_button=True)
                
                if exercise_details["content"]:
                    send_message_to_clarear(exercise_details["content"], with_audio_button=True)
                
                send_message_to_clarear(f"Por favor, digite sua resposta no campo abaixo.", with_audio_button=True)

                st.session_state.user_data["current_stage"] = "in_exercise"
            else:
                send_message_to_clarear("Desculpe, não consegui gerar um exercício para essa área no momento. Que tal tentarmos outra coisa?", with_audio_button=True)
                st.session_state.user_data["current_stage"] = "menu" 
        else:
            send_message_to_clarear("Ok. Se precisar de ajuda ou quiser tentar um exercício, me diga.", with_audio_button=True)
            st.session_state.user_data["current_stage"] = "menu" 
            st.session_state.pending_exercise_area = None 
        
    elif st.session_state.user_data["current_stage"] == "in_exercise":
        exercise_name = st.session_state.user_data["active_exercise"]
        exercise_data = st.session_state.user_data["exercise_data"]
        user_response = prompt.strip() 
        
        expected_answer_raw = exercise_data.get("expected_answer", "").strip().lower()
        user_response_lower = user_response.lower()

        is_correct = False
        if expected_answer_raw: 
            if expected_answer_raw in user_response_lower:
                is_correct = True
            if expected_answer_raw.isdigit() and user_response_lower.isdigit():
                is_correct = (int(expected_answer_raw) == int(user_response_lower))
            if exercise_data["domain"] in ["memória", "atenção", "raciocínio"] and ("sequência" in exercise_name.lower() or "contagem" in exercise_name.lower() or "sequência" in exercise_data["instructions"].lower() or "lógica" in exercise_name.lower() or "série" in exercise_name.lower()): 
                expected_seq = [s.strip().lower() for s in expected_answer_raw.replace(',', ' ').replace('.', ' ').split() if s.strip()]
                user_seq = [s.strip().lower() for s in user_response_lower.replace(',', ' ').replace('.', ' ').split() if s.strip()]
                
                is_correct = (expected_seq == user_seq)


        domain = exercise_data.get("domain", "desconhecido")
        
        with st.spinner("Analisando sua resposta e gerando feedback..."):
            feedback = generate_simulated_feedback( # ALTERADO: Chamar função simulada
                "correct" if is_correct else "incorrect",
                exercise_name,
                user_response,
                exercise_data.get("expected_answer", "não disponível")
            )

        send_message_to_clarear(feedback, with_audio_button=True)
        update_performance_history(exercise_name, domain, "correct" if is_correct else "incorrect")
        
        send_message_to_clarear("O que você gostaria de fazer a seguir? Podemos tentar outro exercício ou finalizar a sessão.", with_audio_button=True)
        st.session_state.user_data["current_stage"] = "menu"
        st.session_state.user_data["active_exercise"] = None 

    elif st.session_state.user_data["current_stage"] == "menu":
        user_input_lower = prompt.lower()
        
        if "exercício" in user_input_lower or "treinar" in user_input_lower or "quero mais" in user_input_lower:
            send_message_to_clarear("Que tipo de exercício você gostaria de fazer? (Ex: memória, atenção, raciocínio, orientação)", with_audio_button=True)
            st.session_state.user_data["current_stage"] = "ask_specific_exercise_type" 
            
        elif "progresso" in user_input_lower or "como estou" in user_input_lower or "desempenho" in user_input_lower:
            send_message_to_clarear("Seu progresso detalhado está sempre visível na barra lateral à esquerda! Continue praticando para ver mais melhorias!", with_audio_button=True)
            st.session_state.user_data["current_stage"] = "menu" 

        elif "finalizar" in user_input_lower or "sair" in user_input_lower or "encerrar" in user_input_lower:
            st.session_state.user_data["current_stage"] = "end_session"
            st.rerun() 
            
        elif any(area in user_input_lower for area in ["memória", "atenção", "raciocínio", "orientação"]):
            area_to_focus = next((area for area in ["memória", "atenção", "raciocínio", "orientação"] if area in user_input_lower), None)
            if area_to_focus:
                with st.spinner(f"Gerando um exercício de {area_to_focus.capitalize()}..."):
                    exercise_details = generate_simulated_exercise(area_to_focus) # ALTERADO: Chamar função simulada
                if exercise_details:
                    st.session_state.user_data["active_exercise"] = exercise_details["name"]
                    st.session_state.user_data["exercise_data"] = exercise_details
                    send_message_to_clarear(f"Certo! Vamos lá para o exercício de **{exercise_details['domain'].capitalize()}**: '{exercise_details['name']}'.", with_audio_button=True)
                    time.sleep(0.5)
                    send_message_to_clarear(exercise_details["instructions"], with_audio_button=True)
                    if exercise_details["content"]:
                        send_message_to_clarear(exercise_details["content"], with_audio_button=True)

                    send_message_to_clarear(f"Por favor, digite sua resposta no campo abaixo.", with_audio_button=True)

                    st.session_state.user_data["current_stage"] = "in_exercise"
                else:
                    send_message_to_clarear("Desculpe, não consegui gerar um exercício para essa área no momento. Que tal tentarmos outra coisa?", with_audio_button=True)
                    st.session_state.user_data["current_stage"] = "menu" 
            else: 
                send_message_to_clarear("Desculpe, não entendi o tipo de exercício. Posso te ajudar com exercícios de memória, atenção, raciocínio ou orientação.", with_audio_button=True)
                st.session_state.user_data["current_stage"] = "menu"

        else:
            send_message_to_clarear("Desculpe, não entendi. Posso te ajudar com **exercícios** (diga 'exercício' ou o tipo como 'memória') ou verificar seu **progresso**.", with_audio_button=True)
            st.session_state.user_data["current_stage"] = "menu"
        
    elif st.session_state.user_data["current_stage"] == "ask_specific_exercise_type":
        user_input_lower = prompt.lower()
        if any(area in user_input_lower for area in ["memória", "atenção", "raciocínio", "orientação"]):
            area_to_focus = next((area for area in ["memória", "atenção", "raciocínio", "orientação"] if area in user_input_lower), None)
            if area_to_focus:
                with st.spinner(f"Gerando um exercício de {area_to_focus.capitalize()}..."):
                    exercise_details = generate_simulated_exercise(area_to_focus) # ALTERADO: Chamar função simulada
                if exercise_details:
                    st.session_state.user_data["active_exercise"] = exercise_details["name"]
                    st.session_state.user_data["exercise_data"] = exercise_details
                    send_message_to_clarear(f"Certo! Vamos lá para o exercício de **{exercise_details['domain'].capitalize()}**: '{exercise_details['name']}'.", with_audio_button=True)
                    time.sleep(0.5)
                    send_message_to_clarear(exercise_details["instructions"], with_audio_button=True)
                    if exercise_details["content"]:
                        send_message_to_clarear(exercise_details["content"], with_audio_button=True)

                    send_message_to_clarear(f"Por favor, digite sua resposta no campo abaixo.", with_audio_button=True)

                    st.session_state.user_data["current_stage"] = "in_exercise"
                else:
                    send_message_to_clarear("Desculpe, não consegui gerar um exercício para essa área no momento. Que tal tentarmos outra coisa?", with_audio_button=True)
                    st.session_state.user_data["current_stage"] = "menu" 
            else:
                send_message_to_clarear("Desculpe, não entendi o tipo de exercício. Por favor, diga 'memória', 'atenção', 'raciocínio' ou 'orientação'.", with_audio_button=True)
                st.session_state.user_data["current_stage"] = "ask_specific_exercise_type" 
        else:
            send_message_to_clarear("Desculpe, não entendi o tipo de exercício. Por favor, diga 'memória', 'atenção', 'raciocínio' ou 'orientação'.", with_audio_button=True)
            st.session_state.user_data["current_stage"] = "ask_specific_exercise_type"

# --- Estágio de Finalização de Sessão ---
elif st.session_state.user_data["current_stage"] == "end_session":
    st.markdown("---")
    st.header(f"👋 Sessão Finalizada, {st.session_state.user_data['nome']}!")
    send_message_to_clarear(f"Obrigado por utilizar o ClareAR hoje, {st.session_state.user_data['nome']}!", with_audio_button=True)
    
    total_attempts = 0
    total_correct = 0
    
    if st.session_state.user_data["performance_history"]:
        for domain, data in st.session_state.user_data["performance_history"].items():
            total_attempts += data["attempts"]
            total_correct += data["correct"]
    
    overall_accuracy = (total_correct / total_attempts) * 100 if total_attempts > 0 else 0

    st.subheader("📊 Seu Resumo de Performance")
    st.write(f"Você completou um total de **{total_attempts} exercícios**.")
    st.write(f"Sua taxa geral de acerto foi de **{overall_accuracy:.1f}%**.")

    if st.session_state.user_data["performance_history"]:
        df_progress = pd.DataFrame([
            {"Domínio": d.capitalize(), "Acerto (%)": (data["correct"] / data["attempts"]) * 100, "Tentativas": data["attempts"]}
            for d, data in st.session_state.user_data["performance_history"].items() if data["attempts"] > 0
        ])
        st.dataframe(df_progress.set_index("Domínio"))

    st.subheader("✨ Próximos Passos e Orientações")
    if overall_accuracy >= 80:
        send_message_to_clarear("Excelente desempenho! Sua concentração e memória estão ótimas. Continue com a prática regular para manter seus resultados e desafiar-se com novos exercícios!", with_audio_button=True)
    elif overall_accuracy >= 50:
        send_message_to_clarear("Você está no caminho certo! Continue praticando regularmente para fortalecer suas habilidades. Pequenos avanços diários fazem uma grande diferença. Lembre-se de focar nas áreas que você sente mais dificuldade.", with_audio_button=True)
    else:
        send_message_to_clarear("Tudo bem! O importante é a sua dedicação e o esforço. A reabilitação cognitiva é um processo. Sugiro focar mais nos exercícios das áreas que você teve menor acerto e tentar sessões mais curtas, mas frequentes. Não hesite em procurar seu médico ou neuropsicólogo para mais orientações.", with_audio_button=True)

    st.info("Para iniciar uma nova sessão, por favor, recarregue a página no seu navegador.")

    # Limpar o estado para uma nova sessão ao recarregar a página
    # st.session_state.clear()