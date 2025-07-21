import streamlit as st
import random
import time
import os
import google.generativeai as genai
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

# --- CSS para Estilo Pastel (Azul e Laranja), Ajustes de Texto/Caixas e Centralização ---
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
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h6 { /* CORRIGIDO: Removido 'st.' */
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

# --- Configuração da API do Gemini ---
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("Chave de API do Google Gemini não encontrada! Por favor, defina a variável de ambiente GOOGLE_API_KEY no seu terminal Codespaces.")
    st.stop() 

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest') 

# --- Inicialização do Estado da Sessão (Crucial para Streamlit!) ---
if "messages" not in st.session_state:
    st.session_state.messages = [] 

if "user_info_collected" not in st.session_state:
    st.session_state.user_info_collected = False 

if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "nome": "",
        "idade": "",
        "dificuldades": [], 
        "current_stage": "greeting", 
        "active_exercise": None,     
        "exercise_data": {},         
        "performance_history": {}    
    }
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
    

# --- Funções do Chatbot e Integração com Gemini ---

def generate_gemini_exercise(difficulty_area, user_age, user_difficulties):
    """
    Gera um exercício usando a API do Google Gemini.
    """
    # NOVO: Adicionado exemplos específicos de exercícios para variar o conteúdo
    exercise_examples = {
        "memória": [
            "Sequência de Palavras (ex: 'mesa, casa, livro, carro')",
            "Lembre-se de uma lista de itens do dia a dia",
            "Memorização de uma pequena história ou fato"
        ],
        "atenção": [
            "Contagem de Letras em uma frase (ex: 'quantas letras A existem na frase X')",
            "Encontre a palavra diferente em uma lista",
            "Tarefa de Stroop (cores e palavras)" # Embora complexo sem UI, a IA pode descrever
        ],
        "raciocínio": [
            "Charadas lógicas (ex: 'O que é, o que é: Tem olhos, mas não vê? Resposta: Agulha')",
            "Series numéricas ou de palavras (ex: 'continue a sequência: 2, 4, 8, __')",
            "Problemas de lógica simples"
        ],
        "orientação": [
            "Perguntas sobre tempo (dia da semana, mês, ano)",
            "Perguntas sobre localização (cidade, estado, país)",
            "Perguntas sobre rotinas diárias"
        ]
    }
    
    # Selecionar um exemplo aleatório para a área específica
    selected_example = random.choice(exercise_examples.get(difficulty_area, ["Perguntas gerais."]))

    prompt = f"""
    Crie um exercício de reabilitação cognitiva para um paciente com encefalopatia hepática leve a moderada.
    O foco principal deve ser em: **{difficulty_area}**.
    O paciente tem {user_age} anos e relatou dificuldades em: {', '.join(user_difficulties)}.
    
    Gere um exercício do tipo: "{selected_example}".
    
    O exercício DEVE SER APENAS TEXTO. NÃO INCLUA NENHUMA REFERÊNCIA A IMAGENS, OBJETOS VISUAIS, OU LISTAS DE ITENS PARA SEREM OBSERVADAS VISUALMENTE.
    O exercício deve ser adequado para interação via chat, fácil de entender e responder.
    A "Resposta Esperada" deve ser precisa para validação.
    
    Formato da saída esperada (estritamente, SEM NENHUM TEXTO ADICIONAL NO INÍCIO OU FIM. Use apenas os campos abaixo):
    Nome do Exercício: [Nome do Exercício]
    Instruções: [Instruções claras e concisas para o paciente]
    Conteúdo do Exercício: [Aqui coloque o texto principal do exercício, como a sequência de números/palavras, a pergunta, a charada, etc. Este é o que o usuário vai responder. Mantenha-o conciso e direto.]
    Tipo de Exercício: [Memória/Atenção/Raciocínio/Orientação]
    Resposta Esperada: [Resposta ou lógica para validar o exercício (SEMPRE FORNEÇA A RESPOSTA FINAL AQUI. Para sequências, a sequência correta. Para perguntas, a resposta correta.)]
    """
    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip() 
        
        text_response = text_response.split("Formato da saída esperada (estritamente, SEM NENHUM TEXTO ADICIONAL NO INÍCIO OU FIM. Use apenas os campos abaixo):")[-1].strip()
        
        name_start = text_response.find("Nome do Exercício:")
        instructions_start = text_response.find("Instruções:")
        content_start = text_response.find("Conteúdo do Exercício:") 
        type_start = text_response.find("Tipo de Exercício:")
        answer_start = text_response.find("Resposta Esperada:")

        name = "Exercício Gerado"
        instructions = "Siga as instruções."
        exercise_content = "" 
        exercise_type = difficulty_area
        expected_answer = ""

        if name_start != -1:
            end_idx = instructions_start if instructions_start != -1 else len(text_response)
            name = text_response[name_start + len("Nome do Exercício:"):end_idx].strip()

        if instructions_start != -1:
            end_idx = content_start if content_start != -1 else type_start if type_start != -1 else len(text_response)
            instructions = text_response[instructions_start + len("Instruções:"):end_idx].strip()
        
        if content_start != -1: 
            end_idx = type_start if type_start != -1 else answer_start if answer_start != -1 else len(text_response)
            exercise_content = text_response[content_start + len("Conteúdo do Exercício:"):end_idx].strip()

        if type_start != -1:
            end_idx = answer_start if answer_start != -1 else len(text_response)
            exercise_type = text_response[type_start + len("Tipo de Exercício:"):end_idx].strip().lower()

        if answer_start != -1:
            expected_answer = text_response[answer_start + len("Resposta Esperada:"):].strip()

        return {
            "name": name, 
            "instructions": instructions, 
            "content": exercise_content, 
            "domain": exercise_type,
            "expected_answer": expected_answer 
        }
    except Exception as e:
        st.error(f"Erro ao gerar exercício com Gemini: {e}. Isso pode acontecer se a resposta do Gemini não estiver no formato esperado. Por favor, tente novamente.")
        return None

def generate_gemini_feedback(performance, exercise_name, user_response, expected_answer):
    """
    Gera feedback motivacional e construtivo usando a API do Google Gemini.
    """
    prompt = f"""
        O paciente acabou de {'acertar' if performance == 'correct' else 'errar'} o exercício '{exercise_name}'.
        A resposta dele foi '{user_response}'.
        A resposta esperada era '{expected_answer}'.
        Crie uma mensagem curta (1-3 frases), {'motivacional e encorajadora para ele, reforçando o bom desempenho e incentivando a continuar.' if performance == 'correct' else 'encorajadora, explicando que errar faz parte do aprendizado e sugerindo que tente novamente ou continue. Mantenha um tone otimista e de apoio.'}
        """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro ao gerar feedback com Gemini: {e}")
        if performance == "correct":
            return f"Parabéns! Você mandou muito bem no exercício '{exercise_name}'!"
        else:
            return f"Não se preocupe! O exercício '{exercise_name}' pode ser um pouco desafiador. Que tal tentar de novo ou um diferente?"


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

# EXIBIR O PAINEL DE PROGESSO PRIMEIRO (na barra lateral)
display_progress_panel()

# Exibir mensagens anteriores do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Primeiro contato ou continuação do fluxo
if st.session_state.user_data["current_stage"] == "greeting":
    send_message_to_clarear("Olá! Sou o ClareAR, seu assistente de reabilitação cognitiva. Para começarmos, qual é o seu nome?", with_audio_button=True)
    st.session_state.user_data["current_stage"] = "ask_name"

# Campo de entrada do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Lógica de processamento da entrada do usuário
    if st.session_state.user_data["current_stage"] == "ask_name":
        st.session_state.user_data["nome"] = prompt.strip()
        send_message_to_clarear(f"Muito prazer, {st.session_state.user_data['nome']}! Qual é a sua idade?", with_audio_button=True)
        st.session_state.user_data["current_stage"] = "ask_age"

    elif st.session_state.user_data["current_stage"] == "ask_age":
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
        st.session_state.user_info_collected = True
        
        if difficulties_input:
            first_difficulty = difficulties_input[0]
            st.session_state.pending_exercise_area = first_difficulty 
            
            # NOVO: Transição direta para gerar exercício se já disser 'sim' ou tipo de exercício
            if "sim" in prompt.lower() or any(area in prompt.lower() for area in ["memória", "atenção", "raciocínio", "orientação"]):
                st.session_state.user_data["current_stage"] = "confirm_initial_exercise" # Reusa o estágio
                st.rerun() # Força o rerun para processar a confirmação/tipo imediatamente
            else:
                send_message_to_clarear(f"Ótimo! Entendi que você quer focar em **{', '.join(difficulties_input)}**.", with_audio_button=True)
                time.sleep(1)
                send_message_to_clarear(f"Que tal começarmos com um exercício de **{first_difficulty.capitalize()}**? Digite 'sim' para começar!", with_audio_button=True)
                st.session_state.user_data["current_stage"] = "confirm_initial_exercise"
        else:
            send_message_to_clarear("Por favor, me diga pelo menos uma área de dificuldade para eu poder ajudar.", with_audio_button=True)
            st.session_state.user_data["current_stage"] = "ask_difficulties" 

    elif st.session_state.user_data["current_stage"] == "confirm_initial_exercise":
        if "sim" in prompt.lower() and st.session_state.pending_exercise_area: # Garante que pending_exercise_area está preenchido
            area_to_focus = st.session_state.pending_exercise_area 
            st.session_state.pending_exercise_area = None # Limpa a área pendente
            
            with st.spinner(f"Gerando um exercício de {area_to_focus.capitalize()}..."):
                exercise_details = generate_gemini_exercise(
                    area_to_focus, 
                    st.session_state.user_data["idade"], 
                    st.session_state.user_data["dificuldades"]
                )
            
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
            if exercise_data["domain"] in ["memória", "atenção", "raciocínio"] and ("sequência" in exercise_name.lower() or "contagem" in exercise_name.lower() or "sequência" in exercise_data["instructions"].lower() or "lógica" in exercise_name.lower()): 
                expected_seq = [s.strip().lower() for s in expected_answer_raw.replace(',', ' ').replace('.', ' ').split() if s.strip()]
                user_seq = [s.strip().lower() for s in user_response_lower.replace(',', ' ').replace('.', ' ').split() if s.strip()]
                
                is_correct = (expected_seq == user_seq)


        domain = exercise_data.get("domain", "desconhecido")
        
        with st.spinner("Analisando sua resposta e gerando feedback..."):
            feedback = generate_gemini_feedback(
                "correct" if is_correct else "incorrect",
                exercise_name,
                user_response,
                exercise_data.get("expected_answer", "não disponível")
            )

        send_message_to_clarear(feedback, with_audio_button=True)
        update_performance_history(exercise_name, domain, "correct" if is_correct else "incorrect")
        
        # Oferecer opção de finalizar sessão aqui
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
            st.rerun() # Usando st.rerun()
            
        elif any(area in user_input_lower for area in ["memória", "atenção", "raciocínio", "orientação"]):
            area_to_focus = next((area for area in ["memória", "atenção", "raciocínio", "orientação"] if area in user_input_lower), None)
            if area_to_focus:
                with st.spinner(f"Gerando um exercício de {area_to_focus.capitalize()}..."):
                    exercise_details = generate_gemini_exercise(
                        area_to_focus, 
                        st.session_state.user_data["idade"], 
                        st.session_state.user_data["dificuldades"]
                    )
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
                    exercise_details = generate_gemini_exercise(
                        area_to_focus, 
                        st.session_state.user_data["idade"], 
                        st.session_state.user_data["dificuldades"]
                    )
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