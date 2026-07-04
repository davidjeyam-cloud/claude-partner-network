import streamlit as st

from utils.styles import apply_theme, phase_header

st.set_page_config(page_title="Claude Code in Action", page_icon="🧩", layout="wide")
apply_theme()
phase_header("Claude Code in Action", "Claude Partner Network Learning Path — Module")

st.markdown("---")
st.info(
    "Lesson content for this module hasn't been added yet. "
    "Paste in the real Skilljar lesson content and it'll be built out here, one lesson at a time."
)
