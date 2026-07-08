import streamlit as st
from google.genai import types

from utils.chat import render_lesson_chat
from utils.llm import get_client
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
- Watch tools, resources, and prompts fire as live protocol messages while you chat
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

st.markdown("---")
st.markdown("### Build the CLI project yourself — as a live chat")
st.markdown(
    """
The real project runs in a terminal: pick a document, then chat with Claude while it reads
and edits documents (**tools**), pulls document content in ahead of time (**resources**),
and runs pre-written commands like `/format` (**prompts**). This is that same project,
rebuilt as a chat right here — with a **live protocol trace** on the right so you can watch
every MCP message type fire as you talk to it.
    """
)

TOOLS = [
    {
        "name": "read_doc_contents",
        "description": "Reads the contents of a document, given its doc_id.",
        "input_schema": {
            "type": "object",
            "properties": {"doc_id": {"type": "string", "description": "The document id, e.g. plan.md"}},
            "required": ["doc_id"],
        },
    },
    {
        "name": "edit_document",
        "description": "Finds old_string in the given document and replaces it with new_string.",
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "The document id, e.g. plan.md"},
                "old_string": {"type": "string", "description": "Exact text to find"},
                "new_string": {"type": "string", "description": "Text to replace it with"},
            },
            "required": ["doc_id", "old_string", "new_string"],
        },
    },
]

PROMPTS = {
    "/format": "Please read the document '{doc_id}' and rewrite it in clean, well-structured markdown. Preserve all the original information.",
    "/summarize": "Please read the document '{doc_id}' and summarize it in one concise paragraph, focusing on key facts and decisions.",
}

KIND_LABEL = {
    "list_tools": "🔧 list tools",
    "call_tool": "🛠️ call tool",
    "read_resource": "📄 read resource",
    "get_prompt": "⚡ get prompt",
}

SYSTEM_PROMPT = (
    "You are a CLI assistant with access to a document store via the read_doc_contents "
    "and edit_document tools. Use them as needed."
)

if "cli_docs" not in st.session_state:
    st.session_state.cli_docs = {
        "plan.md": "Q3 roadmap: ship the MCP module, ship the Claude API module.",
        "report.pdf": "Quarterly report: revenue up 12%, churn down 3%.",
    }
if "cli_messages" not in st.session_state:
    st.session_state.cli_messages = []
if "cli_chat" not in st.session_state:
    st.session_state.cli_chat = None
if "cli_trace" not in st.session_state:
    st.session_state.cli_trace = []
if "cli_attached_doc" not in st.session_state:
    st.session_state.cli_attached_doc = None


def log_trace(kind: str, detail: dict) -> None:
    st.session_state.cli_trace.append({"kind": kind, "detail": detail})


def execute_tool(name: str, tool_input: dict) -> str:
    docs = st.session_state.cli_docs
    doc_id = tool_input.get("doc_id", "")
    if doc_id not in docs:
        result = f"Error: document '{doc_id}' not found"
    elif name == "read_doc_contents":
        result = docs[doc_id]
    elif name == "edit_document":
        old, new = tool_input.get("old_string", ""), tool_input.get("new_string", "")
        if old not in docs[doc_id]:
            result = f"Error: '{old}' not found in {doc_id}"
        else:
            docs[doc_id] = docs[doc_id].replace(old, new)
            result = f"Updated {doc_id}"
    else:
        result = "Unknown tool"
    log_trace("call_tool", {"name": name, "input": tool_input, "result": result})
    return result


def get_or_create_chat():
    if st.session_state.cli_chat is None:
        declarations = [
            types.FunctionDeclaration(
                name=t["name"], description=t["description"], parameters=t["input_schema"]
            )
            for t in TOOLS
        ]
        st.session_state.cli_chat = get_client().chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[types.Tool(function_declarations=declarations)],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )
        log_trace("list_tools", {"tools": [t["name"] for t in TOOLS]})
    return st.session_state.cli_chat


col_chat, col_trace = st.columns([2, 1])

with col_chat:
    st.markdown("**📎 Document picker** (simulates selecting a resource via arrow keys + space)")
    doc_choice = st.selectbox(
        "Attach a document as context for your next message",
        ["(none)"] + list(st.session_state.cli_docs.keys()),
        key="cli_doc_picker",
    )
    pick_col, detach_col = st.columns(2)
    with pick_col:
        if doc_choice != "(none)" and st.button("Attach", key="cli_attach"):
            content = st.session_state.cli_docs[doc_choice]
            log_trace("read_resource", {"uri": f"docs://documents/{doc_choice}", "content": content})
            st.session_state.cli_attached_doc = doc_choice
    with detach_col:
        if st.session_state.cli_attached_doc and st.button("Detach", key="cli_detach"):
            st.session_state.cli_attached_doc = None
    if st.session_state.cli_attached_doc:
        st.caption(f"📎 Attached: `{st.session_state.cli_attached_doc}`")

    st.markdown("**💬 Chat**")
    for msg in st.session_state.cli_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Message, or a slash command like /format or /summarize")
    if user_input:
        stripped = user_input.strip()
        command = stripped.split()[0] if stripped.startswith("/") else None

        if command in PROMPTS:
            doc_for_prompt = st.session_state.cli_attached_doc or next(iter(st.session_state.cli_docs))
            effective_input = PROMPTS[command].format(doc_id=doc_for_prompt)
            log_trace(
                "get_prompt",
                {
                    "prompt_name": command.lstrip("/"),
                    "arguments": {"doc_id": doc_for_prompt},
                    "messages": [{"role": "user", "content": effective_input}],
                },
            )
            display_input = f"{user_input}\n\n*(expanded to: \"{effective_input}\")*"
        else:
            effective_input = user_input
            display_input = user_input

        st.session_state.cli_messages.append({"role": "user", "content": display_input})
        with st.chat_message("user"):
            st.markdown(display_input)

        message_to_send = effective_input
        if st.session_state.cli_attached_doc and command is None:
            doc_id = st.session_state.cli_attached_doc
            message_to_send = (
                f"[Attached resource {doc_id}]:\n{st.session_state.cli_docs[doc_id]}\n\n"
                f"User message: {effective_input}"
            )

        try:
            chat = get_or_create_chat()
            with st.spinner("Thinking..."):
                response = chat.send_message(message_to_send)

                while response.function_calls:
                    fc = response.function_calls[0]
                    result = execute_tool(fc.name, dict(fc.args))
                    response = chat.send_message(
                        types.Part.from_function_response(name=fc.name, response={"result": result})
                    )

            final_text = response.text
            st.session_state.cli_messages.append({"role": "assistant", "content": final_text})
            with st.chat_message("assistant"):
                st.markdown(final_text)
        except Exception as e:
            st.error(f"Couldn't reach the Gemini API — check GEMINI_API_KEY in .env. ({e})")

    if st.button("Reset conversation", key="cli_reset"):
        for k in ("cli_messages", "cli_chat", "cli_trace", "cli_attached_doc", "cli_docs"):
            st.session_state.pop(k, None)
        st.rerun()

with col_trace:
    st.markdown("**🔍 Live protocol trace**")
    st.caption("Every MCP-style message fired this session, most recent first.")
    if not st.session_state.cli_trace:
        st.info("Send a message, attach a document, or try /format to see messages appear here.")
    for entry in reversed(st.session_state.cli_trace):
        with st.expander(KIND_LABEL.get(entry["kind"], entry["kind"]), expanded=False):
            st.json(entry["detail"])

st.markdown("---")

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

render_quiz(QUIZ_QUESTIONS, key="quiz_03")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s03")

st.markdown("### What's next")
st.markdown(
    "**Section 4 — Defining Tools with MCP:** implement the `read_doc_contents` and "
    "`edit_document` tools using the MCP Python SDK's `@mcp.tool` decorator."
)
