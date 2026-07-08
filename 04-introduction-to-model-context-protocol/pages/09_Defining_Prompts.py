import streamlit as st

from utils.chat import render_lesson_chat
from utils.llm import ask_claude_with_tools
from utils.quiz import render_quiz

st.set_page_config(page_title="Defining Prompts", page_icon="🧩", layout="wide")
st.title("Defining Prompts")
st.caption("Introduction to Model Context Protocol — Section 9 of 11")

LESSON_CONTEXT = """\
Prompts are pre-written, tested instructions that MCP servers expose to clients for
specialized tasks.

MCP prompts feature: servers define high-quality prompts tailored to their domain. Clients
can access these prompts via slash commands (e.g. /format), as an alternative to users
writing their own prompts manually.

Implementation pattern: use the @prompt decorator with a name and description. The function
receives arguments (e.g. a document id) and returns a list of messages (user/assistant
format) that get sent directly to Claude.

Key benefit: server authors create optimized, tested prompts rather than leaving prompt
quality up to end users.

Example structure:
@prompt(name="format", description="rewrites document in markdown")
def format_document(doc_id: str) -> list[messages]:
    return [base.user_message(prompt_text)]

Workflow: the user types /format → selects a document → the server returns its specialized
prompt → the client sends it to Claude → Claude uses tools to read, reformat, and save the
document.

Purpose: encapsulate domain expertise in prompt engineering within specialized MCP servers,
rather than leaving prompt quality to whoever happens to be chatting.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Explain what an MCP "prompt" is and how it differs from tools and resources
- Use the `@prompt` decorator with arguments
- Trace the slash-command workflow from `/format` to Claude's final action
- Understand why server-authored prompts beat ad-hoc user prompts
        """
    )

with st.expander("📖 What a Prompt is — concept", expanded=True):
    st.markdown(
        """
Tools give Claude capabilities; resources give your app data. **Prompts** are the third
primitive — **pre-written, tested instructions** the server author has already optimized
for a specific task, which the client can trigger with a slash command instead of the user
having to write a good prompt themselves.

**Workflow:** user types `/format` → picks a document → the server's prompt function
returns a ready-made instruction (with the document id already interpolated in) → the
client sends that straight to Claude → Claude uses its tools to read, reformat, and save the
document.

**Why this matters:** prompt quality varies wildly when every user writes their own. A
server author who deeply understands the domain can bake in the right structure, tone, and
steps once — and every user of that server benefits from the same tested prompt.
        """
    )

with st.expander("📐 Core Code Pattern — @prompt with arguments"):
    st.code(
        '''@prompt(name="format", description="Rewrites a document in clean markdown")
def format_document(doc_id: str) -> list[Message]:
    prompt_text = (
        f"Please read the document '{doc_id}' and rewrite it in clean, "
        f"well-structured markdown. Preserve all the original information."
    )
    return [base.user_message(prompt_text)]
''',
        language="python",
    )
    st.markdown(
        """
**Key insight:** the function's argument (`doc_id`) gets interpolated straight into the
returned message text — the server is handing the client a fully-formed, ready-to-send
prompt, not a template the client has to fill in itself.
        """
    )

st.markdown("---")
st.markdown("### See a slash command in action")
st.markdown(
    "Pick a slash command and a document — this builds the exact message a server's prompt "
    "function would return, then sends it to Claude. Claude uses the same "
    "`read_doc_contents` tool from Section 4 to actually fetch the document before acting "
    "on it, so this is the full `/command → prompt → tool → answer` chain."
)

if "docs4" not in st.session_state:
    st.session_state.docs4 = {
        "plan.md": "Q3 roadmap: ship the MCP module, ship the Claude API module.",
        "report.pdf": "Quarterly report: revenue up 12%, churn down 3%.",
    }

PROMPTS = {
    "/format": "Please read the document '{doc_id}' and rewrite it in clean, well-structured markdown. Preserve all the original information.",
    "/summarize": "Please read the document '{doc_id}' and summarize it in one concise paragraph, focusing on key facts and decisions.",
}

TOOLS = [
    {
        "name": "read_doc_contents",
        "description": "Reads the contents of a document, given its doc_id.",
        "input_schema": {
            "type": "object",
            "properties": {"doc_id": {"type": "string", "description": "The document id, e.g. plan.md"}},
            "required": ["doc_id"],
        },
    }
]


def execute_tool(name: str, tool_input: dict) -> str:
    docs = st.session_state.docs4
    doc_id = tool_input.get("doc_id", "")
    if name == "read_doc_contents":
        return docs.get(doc_id, f"Error: document '{doc_id}' not found")
    return "Unknown tool"


col1, col2 = st.columns(2)
with col1:
    command = st.selectbox("Slash command", list(PROMPTS.keys()))
with col2:
    doc_id = st.selectbox("Document", list(st.session_state.docs4.keys()))

interpolated = PROMPTS[command].format(doc_id=doc_id)
st.markdown("**Messages the server's prompt function returns:**")
st.json([{"role": "user", "content": interpolated}])

if st.button("Send this prompt to Claude", type="primary"):
    system_prompt = (
        "You are an assistant with access to a document store via the read_doc_contents "
        "tool. Use it to fetch a document before acting on it."
    )
    try:
        with st.spinner("Running the prompt through the tool-use chain..."):
            result = ask_claude_with_tools(system_prompt, interpolated, TOOLS, execute_tool)

        if result["tool_call"] is not None:
            st.markdown(f"**Tool called:** `{result['tool_call'].name}({result['tool_call'].input})`")
            st.markdown("**Claude's final response:**")
        st.success(result["final_text"])

        with st.expander("Execution trace — raw API responses"):
            st.markdown("**System prompt:**")
            st.code(system_prompt, language="text")
            st.markdown("**Interpolated prompt message:**")
            st.code(interpolated, language="text")
            st.markdown("**Raw first response:**")
            st.code(str(result["raw_first"]), language="text")
            if "raw_final" in result:
                st.markdown("**Raw final response:**")
                st.code(str(result["raw_final"]), language="text")
    except Exception as e:
        st.error(f"Couldn't reach the Gemini API — check GEMINI_API_KEY in .env. ({e})")

QUIZ_QUESTIONS = [
    {
        "question": "What does an MCP prompt function return?",
        "options": [
            "A list of messages (user/assistant format) ready to send to Claude",
            "A raw string with no structure",
            "A JSON schema, like a tool",
            "A URI, like a resource",
        ],
        "answer_index": 0,
        "explanation": "@prompt-decorated functions return a list of messages that get sent directly to Claude.",
    },
    {
        "question": "How does a client typically trigger a server-defined prompt?",
        "options": [
            "A slash command, e.g. /format",
            "By calling call_tool() with the prompt's name",
            "Automatically, on every message",
            "Only through the Inspector UI",
        ],
        "answer_index": 0,
        "explanation": "Slash commands like /format are the client-side trigger for a server's prompt.",
    },
    {
        "question": "What's the main benefit of server-authored prompts over ad-hoc user prompts?",
        "options": [
            "The server author can bake in tested structure and domain expertise once, for every user",
            "They run faster than user-typed prompts",
            "They don't require any arguments",
            "They bypass the need for tools entirely",
        ],
        "answer_index": 0,
        "explanation": "Prompt quality varies when every user writes their own — a tested, server-authored prompt fixes that.",
    },
    {
        "question": "In the /format workflow, what does Claude do after receiving the prompt?",
        "options": [
            "Uses tools to read, reformat, and save the document",
            "Immediately returns the prompt text unchanged",
            "Ignores the prompt and asks the user for more detail",
            "Deletes the document and recreates it",
        ],
        "answer_index": 0,
        "explanation": "The prompt hands Claude an instruction, and it uses its available tools to actually carry out the task.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_09")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s09")

st.markdown("### What's next")
st.markdown(
    "**Section 10 — Prompts in the Client:** the client-side `list_prompts()` and "
    "`get_prompt()` functions that make slash commands work."
)
