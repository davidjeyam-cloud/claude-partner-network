import streamlit as st

from utils.chat import render_lesson_chat
from utils.quiz import render_quiz

st.set_page_config(page_title="Project Setup", page_icon="🧩", layout="wide")
st.title("Project Setup")
st.caption("Introduction to Model Context Protocol — Section 3 of 11")

LESSON_CONTEXT = """\
The MCP learning project used throughout this course is a CLI-based chatbot implementing
both client and server components, for educational purposes.

Project structure: a custom MCP client connects to a custom MCP server, both built in the
same project.

Document system: fake documents stored in memory only, with no persistence.

Server tools: two tools are implemented — read document contents, and update document
contents.

Real-world context: normally a project implements either the client OR the server, not
both. This project does both purely for learning purposes.

Setup requirements: download CLI_project.zip, extract it, configure a .env file with an API
key, and install dependencies.

Running the project: `uv run main.py` (with UV) or `python main.py` (without UV).

Verification: a chat prompt appears and responds correctly to basic queries like "what's
one plus one".
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Describe the shape of the hands-on learning project used in this course
- Explain why this project implements both a client and a server (unusual in practice)
- Know the two document tools the server exposes
- Verify a fresh setup is working correctly
        """
    )

with st.expander("📖 The learning project — concept", expanded=True):
    st.markdown(
        """
The project used throughout this course is a **CLI-based chatbot** that implements *both*
an MCP client and an MCP server in the same codebase.

**That's unusual** — in a real deployment, a team typically builds one side or the other:
either you're building an MCP server to expose your service's functionality, or you're
building a client to consume someone else's server. This project does both purely so you
can see the full round trip without depending on an external server.

**What the server exposes:** two tools, operating on fake, in-memory-only documents (no
persistence — restart, and they reset):

| Tool | Purpose |
|---|---|
| Read document contents | Look up a document by id and return its text |
| Update document contents | Modify a document's stored text |

**Setup:** download `CLI_project.zip`, extract it, configure `.env` with an API key, install
dependencies, then run it with `uv run main.py` (or `python main.py` without `uv`).

**Verify it's working:** a chat prompt should appear and answer a basic sanity-check query
like *"what's one plus one"* correctly before you move on to wiring up real tools.
        """
    )

QUIZ_QUESTIONS = [
    {
        "question": "Why does this learning project implement both an MCP client and server, when real projects usually build only one?",
        "options": [
            "So learners can see the full round trip without depending on an external server",
            "Because MCP requires both to be in the same codebase",
            "It's a limitation of the Python SDK",
            "Because the documents need both sides to persist",
        ],
        "answer_index": 0,
        "explanation": "In practice you typically build the client OR the server — this project does both purely for hands-on learning.",
    },
    {
        "question": "How are the project's documents stored?",
        "options": [
            "In memory only — no persistence",
            "In a SQLite database file",
            "In a cloud document store",
            "As individual .md files on disk",
        ],
        "answer_index": 0,
        "explanation": "The documents are fake, in-memory data with no persistence — they reset on restart.",
    },
    {
        "question": "Which two tools does the server implement?",
        "options": [
            "Read document contents, and update document contents",
            "Create document and delete document",
            "List documents and search documents",
            "Upload document and download document",
        ],
        "answer_index": 0,
        "explanation": "The two implemented tools are reading a document's contents and updating them.",
    },
    {
        "question": "What confirms the project is set up correctly?",
        "options": [
            "The chat prompt appears and answers a basic query like \"what's one plus one\" correctly",
            "The .env file contains no errors when opened in a text editor",
            "The zip file extracts without a warning",
            "uv --version returns a number",
        ],
        "answer_index": 0,
        "explanation": "A working basic query confirms the chat loop, API key, and dependencies are all correctly wired up.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_03")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s03")

st.markdown("### What's next")
st.markdown(
    "**Section 4 — Defining Tools with MCP:** implement the `read_doc_contents` and "
    "`edit_document` tools using the MCP Python SDK's `@mcp.tool` decorator."
)
