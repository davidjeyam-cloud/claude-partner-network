import streamlit as st

from utils.chat import render_lesson_chat
from utils.quiz import render_quiz

st.set_page_config(page_title="Introducing MCP", page_icon="🧩", layout="wide")
st.title("Introducing MCP")
st.caption("Introduction to Model Context Protocol — Section 1 of 11")

LESSON_CONTEXT = """\
MCP (Model Context Protocol) is a communication layer providing Claude with context and
tools without requiring developers to write tedious code.

Core architecture: an MCP client connects to an MCP server. The MCP server contains tools,
resources, and prompts as its internal components.

Problem solved: the traditional approach requires developers to manually author tool
schemas and functions for every service integration (e.g. GitHub API tools). This creates a
maintenance burden for complex services with many features.

MCP's solution: it shifts tool definition and execution from the developer's own server to
a dedicated MCP server. The MCP server is the interface to the outside service, wrapping its
functionality into pre-built tools. This eliminates the need for developers to write and
maintain tool schemas and function implementations themselves — someone else authors the
tools and packages them in an MCP server.

Common questions: Who authors MCP servers? Anyone, but often the service provider creates
the official implementation. How is this different from calling the API directly? It saves
developer time by providing pre-built tool schemas/functions instead of manual authoring.
How does this relate to tool use? MCP and tool use are complementary, not identical — MCP is
about who does the work of creating the tools; tool use is how Claude actually calls them.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Define what MCP is and the problem it solves
- Describe the core client/server architecture
- Explain how MCP relates to tool use — complementary, not identical
- Identify who typically authors an MCP server
        """
    )

with st.expander("📖 What is MCP — concept", expanded=True):
    st.markdown(
        """
Every service you want Claude to use — GitHub, a docs system, a database — normally needs
someone to hand-write a tool schema and a function that calls its API. For a complex service
with dozens of endpoints, that's a lot of code to write and keep in sync as the API evolves.

**MCP shifts that burden.** Instead of your own server authoring and maintaining every tool,
a dedicated **MCP server** wraps the service's functionality into pre-built tools, resources,
and prompts. Your **MCP client** just connects to it and gets that functionality for free —
someone else (often the service provider) has already done the work of building and
maintaining the tools.

**MCP vs. tool use:** these are complementary, not the same thing. Tool use is *how* Claude
calls a function once it's given one. MCP is about *who does the work* of building that
function and its schema in the first place — an MCP server instead of you.
        """
    )

st.markdown("### MCP vs. hand-rolled API integration")
st.markdown(
    """
| # | Hand-rolled integration | MCP |
|---|---|---|
| 1 | You author a JSON tool schema for every endpoint you want to expose | The MCP server already defines the schema — you just connect to it |
| 2 | You write and maintain the function that calls the service's API | The MCP server owns that function; you consume it via the protocol |
| 3 | Every team integrating the same service repeats this work | One MCP server (often built by the provider) is reused by every client |
| 4 | Keeping schemas in sync with API changes is your responsibility | The server author keeps it in sync — you just reconnect |
"""
)

QUIZ_QUESTIONS = [
    {
        "question": "What problem does MCP primarily solve?",
        "options": [
            "The maintenance burden of manually authoring tool schemas/functions for every service integration",
            "Claude's inability to use tools at all without MCP",
            "Slow network speeds between client and server",
            "The need to fine-tune Claude on your own data",
        ],
        "answer_index": 0,
        "explanation": "Without MCP, developers hand-write and maintain a schema and function per endpoint — MCP outsources that work to a dedicated server.",
    },
    {
        "question": "In the core architecture, what does an MCP server contain?",
        "options": [
            "Tools, resources, and prompts",
            "Only tools — resources and prompts are client-side",
            "A copy of Claude's weights",
            "Just a list of API keys",
        ],
        "answer_index": 0,
        "explanation": "Tools, resources, and prompts are the three primitives an MCP server exposes internally.",
    },
    {
        "question": "How does MCP relate to \"tool use\"?",
        "options": [
            "Complementary — MCP is about who builds the tools, tool use is how Claude calls them",
            "They're the same feature with two different names",
            "MCP replaces tool use entirely",
            "Tool use is a subset of MCP with no independent meaning",
        ],
        "answer_index": 0,
        "explanation": "MCP and tool use solve different parts of the problem — tool authorship/distribution vs. the calling mechanism.",
    },
    {
        "question": "Who typically authors an MCP server for a given service?",
        "options": [
            "Anyone can, but the service provider often builds the official one",
            "Only Anthropic is allowed to author MCP servers",
            "Only the end user of the AI application",
            "MCP servers are auto-generated with no human author",
        ],
        "answer_index": 0,
        "explanation": "MCP servers are open to anyone to build, though official ones are frequently maintained by the service provider itself.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_01")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s01")

st.markdown("### What's next")
st.markdown(
    "**Section 2 — MCP Clients:** how the client mediates between your application and an "
    "MCP server, and the exact message types (`list tools`, `call tool`) that make the "
    "protocol work — with a live demo of the real tool-use exchange underneath it."
)
