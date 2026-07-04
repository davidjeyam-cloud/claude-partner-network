import streamlit as st

ACCENT = "#CC785C"


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { padding-top: 0.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def phase_header(title: str, caption: str) -> None:
    st.title(title)
    st.caption(caption)
