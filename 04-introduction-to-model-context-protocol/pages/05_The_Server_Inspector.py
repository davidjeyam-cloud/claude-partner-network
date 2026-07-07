import streamlit as st

from utils.chat import render_lesson_chat
from utils.quiz import render_quiz

st.set_page_config(page_title="The Server Inspector", page_icon="🧩", layout="wide")
st.title("The Server Inspector")
st.caption("Introduction to Model Context Protocol — Section 5 of 11")

LESSON_CONTEXT = """\
The MCP Inspector is an in-browser debugger for testing MCP servers without connecting to
an actual application.

Access: run `mcp dev [server_file.py]` in a terminal with the Python environment activated
— this opens the server on a port, and you visit the localhost address it prints.

Interface: a left sidebar has a Connect button. The top navigation bar shows
Resources/Prompts/Tools sections. The Tools section lists available tools; clicking one
opens a right panel for manual testing.

Testing process: select a tool, input its required parameters (like a document id), click
Run Tool, and verify the output or success message.

Key features: live development testing, tool invocation simulation, parameter input
fields, and success/failure feedback.

Status: the Inspector is in active development — the UI may change, but the core
functionality remains similar.

Usage pattern: it's essential for MCP server development and debugging before production
deployment.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Launch the MCP Inspector against a local server file
- Navigate its Resources / Prompts / Tools sections
- Manually test a tool by supplying parameters and running it
- Know when to reach for the Inspector instead of building a full client
        """
    )

with st.expander("📖 Debugging with the Inspector — concept", expanded=True):
    st.markdown(
        """
Before wiring up a full client application, you want to check that your MCP server's tools
actually work. The **MCP Inspector** is an in-browser debugger built for exactly that — no
client required.

**Launching it:**

```bash
mcp dev server_file.py
```

This starts your server and opens an Inspector UI in the browser at the localhost address
it prints. The interface has a **Connect** button in the sidebar, and a top nav with
**Resources / Prompts / Tools** sections — the same three primitives an MCP server exposes.

**Testing a tool:** open the Tools section, click the tool you want to test, fill in its
required parameters in the panel that opens, click **Run Tool**, and check the output or
success/failure message.

The Inspector is still in active development, so the exact UI may shift over time — but the
core loop (connect → pick a tool → fill parameters → run → verify) stays the same. It's the
tool you reach for *during development*, before you've built (or need) a full client.
        """
    )

st.markdown("---")
st.markdown("### A simulated Inspector panel")
st.markdown(
    "The real Inspector runs in your browser against a live server process — it can't run "
    "inside this page. What's below mimics its interaction pattern (pick a tool → fill "
    "parameters → Run Tool → see the result) using the same `read_doc_contents` tool from "
    "Section 4, so you can get a feel for the workflow."
)

MOCK_DOCS = {
    "plan.md": "Q3 roadmap: ship the MCP module, ship the Claude API module.",
    "report.pdf": "Quarterly report: revenue up 12%, churn down 3%.",
}

col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("**Tools**")
    st.button("📄 read_doc_contents", disabled=True, key="inspector_tool_btn")
with col2:
    st.markdown("**Run Tool**")
    doc_id = st.selectbox("doc_id", list(MOCK_DOCS.keys()) + ["missing.md"])
    if st.button("Run Tool", type="primary", key="inspector_run"):
        if doc_id in MOCK_DOCS:
            st.success(f"Success — returned:\n\n{MOCK_DOCS[doc_id]}")
        else:
            st.error(f"Error — ValueError: Document '{doc_id}' not found")

QUIZ_QUESTIONS = [
    {
        "question": "How do you launch the MCP Inspector against a server file?",
        "options": [
            "mcp dev server_file.py",
            "mcp inspect server_file.py",
            "python -m mcp.inspector",
            "npm run inspector",
        ],
        "answer_index": 0,
        "explanation": "`mcp dev [server_file.py]` starts the server and opens the Inspector UI at a localhost address.",
    },
    {
        "question": "What three sections appear in the Inspector's top navigation?",
        "options": [
            "Resources, Prompts, Tools",
            "Logs, Metrics, Settings",
            "Client, Server, Transport",
            "Read, Write, Delete",
        ],
        "answer_index": 0,
        "explanation": "These mirror the three MCP server primitives — Resources, Prompts, and Tools.",
    },
    {
        "question": "What's the main benefit of using the Inspector during development?",
        "options": [
            "You can test tools manually without building a full client application first",
            "It automatically writes your tool's code for you",
            "It's required before you can deploy an MCP server",
            "It replaces the need for a document store",
        ],
        "answer_index": 0,
        "explanation": "The Inspector lets you verify a server's tools work correctly before investing in a full client integration.",
    },
    {
        "question": "What's the correct testing process in the Inspector?",
        "options": [
            "Select a tool, input its parameters, click Run Tool, check the output",
            "Type a natural-language request and let it auto-select a tool",
            "Upload a config file describing the test case",
            "Write a unit test in the browser console",
        ],
        "answer_index": 0,
        "explanation": "This manual select → fill → run → verify loop is exactly how the Inspector is used.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_05")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s05")

st.markdown("### What's next")
st.markdown(
    "**Section 6 — Implementing a Client:** the `MCPClient` wrapper class, `list_tools()` "
    "and `call_tool()`, and how resource cleanup is handled when the connection closes."
)
