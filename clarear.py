import streamlit as st

# Estado para controlar o nível de dificuldade
if "level" not in st.session_state:
    st.session_state.level = 1
if "score" not in st.session_state:
    st.session_state.score = 0

st.title("ClareAR - Assistente de Reabilitação Cognitiva")

st.write("Vamos iniciar um exercício cognitivo personalizado para você.")

def get_task(level):
    tasks = {
        1: {"question": "Repita essa sequência: 3, 7, 1", "answer": "3 7 1"},
        2: {"question": "Repita essa sequência: 9, 4, 8, 2", "answer": "9 4 8 2"},
        3: {"question": "Qual o próximo número da sequência? 2, 4, 6, ?", "answer": "8"},
        4: {"question": "Quantas letras tem a palavra 'hospital'?", "answer": "8"},
        5: {"question": "Complete a frase: O céu é ____", "answer": "azul"},
    }
    return tasks.get(level, tasks[5])

task = get_task(st.session_state.level)

user_answer = st.text_input(task["question"])

if st.button("Enviar resposta"):
    if user_answer.strip().lower() == task["answer"]:
        st.session_state.score += 1
        st.success("Resposta correta! Vamos aumentar a dificuldade.")
        if st.session_state.level < 5:
            st.session_state.level += 1
    else:
        st.error("Resposta incorreta. Vamos tentar um pouco mais fácil.")
        if st.session_state.level > 1:
            st.session_state.level -= 1

    st.write(f"Seu nível atual: {st.session_state.level}")
    st.write(f"Pontos acumulados: {st.session_state.score}")
