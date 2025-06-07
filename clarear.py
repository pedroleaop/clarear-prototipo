import streamlit as st
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="ClareAR - Assistente Cognitivo", layout="centered")

st.title("ClareAR - Assistente de Reabilitação Cognitiva")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "Você é um assistente virtual de reabilitação cognitiva para pacientes com encefalopatia hepática. "
            "Seu objetivo é propor exercícios cognitivos adaptativos, avaliar as respostas do paciente, "
            "dar feedback motivacional e explicar a importância dos exercícios para a saúde cognitiva. "
            "Seja claro, amigável e paciente."
        )}
    ]
    st.session_state.level = 1
    st.session_state.score = 0

def get_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=250,
        n=1,
        stop=None,
    )
    return response.choices[0].message["content"]

def add_user_message(text):
    st.session_state.messages.append({"role": "user", "content": text})

def add_assistant_message(text):
    st.session_state.messages.append({"role": "assistant", "content": text})

def build_prompt_for_exercise(level):
    prompt = (
        f"Proponha um exercício cognitivo simples para um paciente com encefalopatia hepática "
        f"de nível {level} (1 fácil, 5 difícil). O exercício deve focar em memória, atenção ou raciocínio lógico. "
        f"Peça para o paciente responder de forma breve e depois aguarde a resposta."
    )
    return prompt

# Início da interação
if len(st.session_state.messages) == 1:
    # Gerar exercício inicial
    prompt = build_prompt_for_exercise(st.session_state.level)
    add_assistant_message(prompt)

# Mostra toda a conversa
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(f"**ClareAR:** {msg['content']}")
    else:
        st.markdown(f"**Você:** {msg['content']}")

# Input do usuário
user_input = st.text_input("Sua resposta:", key="input_text")

if st.button("Enviar"):
    if user_input.strip() == "":
        st.warning("Por favor, digite sua resposta antes de enviar.")
    else:
        add_user_message(user_input)

        # Avaliar resposta e gerar feedback + próximo exercício
        evaluation_prompt = (
            "Você é um assistente de reabilitação cognitiva. Avalie se a resposta do paciente está correta "
            "ou adequada ao exercício proposto anteriormente. Dê feedback positivo se correto, "
            "ou dicas para melhorar se incorreto, mantendo um tom motivacional e encorajador. "
            "Depois, proponha um novo exercício cognitivo, um pouco mais difícil se o paciente acertou, "
            "ou um pouco mais fácil se errou, focando em memória, atenção ou raciocínio lógico."
        )

        # Monta o contexto para a IA com a conversa toda + instruções
        context_messages = st.session_state.messages.copy()
        context_messages.append({"role": "system", "content": evaluation_prompt})

        response_text = get_response(context_messages)
        add_assistant_message(response_text)

        # Atualiza o nível baseado no texto de feedback (simplificação)
        if "correto" in response_text.lower() or "muito bem" in response_text.lower():
            if st.session_state.level < 5:
                st.session_state.level += 1
            st.session_state.score += 1
        elif "tente" in response_text.lower() or "dica" in response_text.lower():
            if st.session_state.level > 1:
                st.session_state.level -= 1

        # Limpa input
        st.session_state.input_text = ""

# Mostrar status e progresso
st.markdown(f"### Nível atual: {st.session_state.level}")
st.markdown(f"### Pontos acumulados: {st.session_state.score}")

st.markdown("---")
st.markdown("ClareAR foi desenvolvido para ajudar pacientes com dificuldades cognitivas a melhorar sua memória, atenção e raciocínio por meio de exercícios adaptativos gerados por IA.")
