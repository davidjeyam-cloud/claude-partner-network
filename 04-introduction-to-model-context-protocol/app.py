import streamlit as st

from utils.styles import apply_theme, phase_header

st.set_page_config(page_title="Introduction to Model Context Protocol", page_icon="🧩", layout="wide")
apply_theme()
phase_header("Introduction to Model Context Protocol", "Claude Partner Network Learning Path — Module 04")

st.markdown("---")

with st.expander("About this module", expanded=True):
    st.markdown(
        """
**MCP (Model Context Protocol)** is a communication layer that gives Claude context and
tools without developers having to hand-write tedious integration code. Instead of every
team authoring and maintaining its own tool schemas and functions for each service (GitHub,
Google Drive, internal docs...), an **MCP server** wraps that service's functionality into
pre-built tools once, and any **MCP client** can connect to it.

This module walks through the whole protocol hands-on: the client/server architecture, the
three primitives a server can expose (tools, resources, prompts), building a minimal MCP
server and client from scratch, and the in-browser Inspector for debugging one along the way.

*— built from a set of structured course notes on MCP, provided directly rather than sourced
from the Skilljar page (see [CLAUDE.md](../CLAUDE.md))*
        """
    )

st.markdown("### Sections")

sections = [
    (1, "Introducing MCP", "✅ Complete"),
    (2, "MCP Clients", "✅ Complete"),
    (3, "Project Setup", "✅ Complete"),
    (4, "Defining Tools with MCP", "✅ Complete"),
    (5, "The Server Inspector", "✅ Complete"),
    (6, "Implementing a Client", "✅ Complete"),
    (7, "Defining Resources", "✅ Complete"),
    (8, "Accessing Resources", "✅ Complete"),
    (9, "Defining Prompts", "✅ Complete"),
    (10, "Prompts in the Client", "✅ Complete"),
    (11, "MCP Review", "✅ Complete"),
]

rows = "\n".join(f"| {n} | {title} | {status} |" for n, title, status in sections)
st.markdown(
    f"""
| # | Section | Status |
|---|---|---|
{rows}
"""
)

st.info(
    "Each section is a page in the sidebar. Sections 2, 4, and 9 include a live demo that "
    "calls the real Claude API with tool-use / prompt templating — the same mechanics MCP "
    "wraps, just without the protocol layer running between client and server."
)
