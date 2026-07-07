import streamlit as st

from utils.chat import render_lesson_chat
from utils.llm import ask_claude_with_tools
from utils.quiz import render_quiz

st.set_page_config(page_title="MCP Clients", page_icon="🧩", layout="wide")
st.title("MCP Clients")
st.caption("Introduction to Model Context Protocol — Section 2 of 11")

LESSON_CONTEXT = """\
An MCP Client is the communication interface between your server and an MCP server — it
provides access to the MCP server's tools.

MCP is transport agnostic: client and server can communicate via multiple protocols
(stdin/stdout, HTTP, WebSockets, etc). A common setup runs both on the same machine over
stdin/stdout.

Communication is a message exchange defined by the MCP spec. Key message types:
- list tools request/result — the client asks the server for its available tools, the
  server responds with the tool list.
- call tool request/result — the client asks the server to run a specific tool with
  arguments, the server returns the execution result.

Typical flow: a user query comes in → your server asks its MCP client for tools → the
client sends a list-tools request to the MCP server → the server returns the tool list →
your server sends the query plus that tool list to Claude → Claude requests a tool
execution → your server asks the MCP client to run it → the client sends a call-tool
request to the MCP server → the MCP server executes the tool (e.g. a GitHub API call) →
the result flows back through the same chain → Claude formulates its final response → the
user gets an answer.

The MCP client is only an intermediary — it never executes tools itself. It just relays
messages between your application and the MCP server that actually runs them.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Explain what an MCP client does — and doesn't do
- Name the two key message types: list tools and call tool
- Describe the full request/response flow from user query to final answer
- Understand "transport agnostic" and why it matters
        """
    )

with st.expander("📖 What an MCP Client does — concept", expanded=True):
    st.markdown(
        """
The **MCP client** sits between your application and an **MCP server**. It never runs a
tool itself — it just relays two kinds of messages, defined by the MCP spec:

| Message | Direction | Purpose |
|---|---|---|
| `list tools` request/result | Client → Server → Client | "What tools do you have?" → a list back |
| `call tool` request/result | Client → Server → Client | "Run this tool with these arguments" → the result back |

Because MCP is **transport agnostic**, that exchange can run over stdin/stdout (common when
client and server are on the same machine), HTTP, WebSockets, or anything else the spec
supports — the message *shape* stays the same regardless of transport.
        """
    )

st.markdown("### The full request/response flow")
st.markdown(
    """
1. A user query comes in.
2. Your server asks its MCP client for the available tools.
3. The client sends a **list tools request** to the MCP server → gets a **list tools result** back.
4. Your server sends the user's query *and* that tool list to Claude.
5. Claude decides a tool is needed and requests its execution.
6. Your server asks the MCP client to run it — the client sends a **call tool request**.
7. The MCP server executes the tool (e.g. hitting a GitHub API) and returns a **call tool result**.
8. The result flows back to Claude, which formulates its final response.
9. The user gets the answer.
    """
)

st.markdown("---")
st.markdown("### See the exchange in action")
st.markdown(
    "This demo runs the real `tool_use` / `tool_result` exchange with the Claude API — the "
    "same mechanic an MCP client mediates in steps 5-8 above, just without the protocol "
    "layer between here and a separate MCP server. The **list tools result** below is fixed, "
    "standing in for what a real MCP server would return."
)

DOCS = {
    "plan.md": "Q3 roadmap: ship the MCP module, ship the Claude API module, finalize the troubleshooting guide.",
    "report.pdf": "Quarterly report: revenue up 12%, churn down 3%.",
}

TOOLS = [
    {
        "name": "read_doc_contents",
        "description": "Reads the contents of a document, given its doc_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "The document id, e.g. plan.md"}
            },
            "required": ["doc_id"],
        },
    }
]

st.markdown("**① list tools result** (what a real MCP server would return):")
st.json(TOOLS)


def execute_tool(name: str, tool_input: dict) -> str:
    if name == "read_doc_contents":
        doc_id = tool_input.get("doc_id", "")
        return DOCS.get(doc_id, f"No document named '{doc_id}' found.")
    return "Unknown tool"


query = st.text_input(
    "Your query",
    placeholder="e.g. What's in plan.md?",
    value="What's in plan.md?",
)

if st.button("Send to Claude", type="primary"):
    if not query.strip():
        st.warning("Type a query first.")
    else:
        system_prompt = (
            "You are an assistant with access to a document store via the "
            "read_doc_contents tool. Use it whenever the user asks about a document's "
            "contents."
        )
        try:
            with st.spinner("Running the tool-use exchange..."):
                result = ask_claude_with_tools(system_prompt, query, TOOLS, execute_tool)

            if result["tool_call"] is None:
                st.info("Claude answered without needing a tool:")
                st.markdown(result["final_text"])
            else:
                st.markdown("**② call tool request** — Claude's tool call:")
                st.json({"name": result["tool_call"].name, "input": result["tool_call"].input})

                st.markdown("**③ call tool result** — executed (simulating the MCP server):")
                st.code(result["tool_result"], language="text")

                st.markdown("**④ Claude's final response:**")
                st.success(result["final_text"])

            with st.expander("Execution trace — raw API responses"):
                st.markdown("**System prompt:**")
                st.code(system_prompt, language="text")
                st.markdown("**Tools sent:**")
                st.json(TOOLS)
                st.markdown("**Raw first response:**")
                st.code(str(result["raw_first"]), language="text")
                if "raw_final" in result:
                    st.markdown("**Raw final response:**")
                    st.code(str(result["raw_final"]), language="text")
        except Exception as e:
            st.error(f"Couldn't reach the Claude API — check ANTHROPIC_API_KEY in .env. ({e})")

QUIZ_QUESTIONS = [
    {
        "question": "What are the two key MCP message types in the client/server exchange?",
        "options": [
            "list tools and call tool (each with a request and a result)",
            "connect and disconnect",
            "read and write",
            "authenticate and authorize",
        ],
        "answer_index": 0,
        "explanation": "list tools (what's available) and call tool (run this with these arguments) are the two core message types.",
    },
    {
        "question": "Does the MCP client execute tools itself?",
        "options": [
            "No — it's only an intermediary that relays messages to the MCP server, which executes them",
            "Yes, that's its entire job",
            "Only for read-only tools",
            "Only if the server is unreachable",
        ],
        "answer_index": 0,
        "explanation": "The client never runs a tool itself; it relays requests to the MCP server, which does the actual execution.",
    },
    {
        "question": "What does \"transport agnostic\" mean for MCP?",
        "options": [
            "Client and server can communicate over stdin/stdout, HTTP, WebSockets, etc. — the message shape stays the same",
            "MCP only works over HTTP",
            "The client can talk to any AI model, not just Claude",
            "Tools can be written in any programming language",
        ],
        "answer_index": 0,
        "explanation": "The protocol's messages are the same regardless of which transport carries them.",
    },
    {
        "question": "In the typical flow, who actually decides that a tool needs to be called?",
        "options": [
            "Claude, after being given the query and the tool list",
            "The MCP client, before contacting Claude",
            "The MCP server, without any input from Claude",
            "The end user, by typing a special command",
        ],
        "answer_index": 0,
        "explanation": "Claude receives the query plus the available tools and decides for itself whether and which tool to call.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_02")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s02")

st.markdown("### What's next")
st.markdown(
    "**Section 3 — Project Setup:** the CLI-based learning project this course builds — a "
    "single project implementing both an MCP client and server, with two document tools, "
    "for hands-on learning."
)
