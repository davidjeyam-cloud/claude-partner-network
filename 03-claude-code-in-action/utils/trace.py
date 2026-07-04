import streamlit as st


def render_trace(system_prompt: str, user_message: str, raw_response: str) -> None:
    with st.expander("Execution Trace — exact prompts and raw responses"):
        st.markdown("**System prompt:**")
        st.code(system_prompt, language="text")
        st.markdown("**User message:**")
        st.code(user_message, language="text")
        st.markdown("**Raw response:**")
        st.code(raw_response, language="text")
