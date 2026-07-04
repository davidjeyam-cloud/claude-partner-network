import streamlit as st

from utils.llm import ask_claude_messages


def render_lesson_chat(lesson_context: str, key: str) -> None:
    st.markdown("#### Ask about this lesson")
    st.caption(
        "Grounded only in this section's content — good for probing anything you're "
        "still unsure about, or testing whether you can trip it up."
    )

    history_key = f"chat_history_{key}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a question about this section...", key=f"chat_input_{key}")
    if question:
        st.session_state[history_key].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        system_prompt = (
            "You are a tutor helping a learner deepen their understanding of a Claude Code "
            "lesson. Answer strictly using the lesson content provided below — if a question "
            "goes beyond it, say so plainly rather than inventing an answer. Keep answers "
            "concise, and end with a short follow-up question when it would help check "
            "understanding.\n\nLesson content:\n" + lesson_context
        )
        try:
            with st.spinner("Thinking..."):
                answer = ask_claude_messages(system_prompt, st.session_state[history_key])
        except Exception as e:
            answer = f"Couldn't reach the Claude API — check ANTHROPIC_API_KEY in .env. ({e})"

        st.session_state[history_key].append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

        with st.expander("Execution trace — last exchange"):
            st.markdown("**System prompt:**")
            st.code(system_prompt, language="text")
            st.markdown("**Conversation sent:**")
            st.code(str(st.session_state[history_key]), language="text")
            st.markdown("**Raw response:**")
            st.code(answer, language="text")
