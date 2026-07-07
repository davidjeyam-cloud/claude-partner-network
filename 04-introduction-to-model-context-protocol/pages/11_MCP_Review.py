import streamlit as st

from utils.chat import render_lesson_chat
from utils.quiz import render_quiz

st.set_page_config(page_title="MCP Review", page_icon="🧩", layout="wide")
st.title("MCP Review")
st.caption("Introduction to Model Context Protocol — Section 11 of 11")

LESSON_CONTEXT = """\
MCP server primitives: there are 3 types — tools, resources, and prompts.

Tools are model-controlled primitives, where Claude decides when to execute them. They're
used to add capabilities to Claude (e.g. JavaScript execution for calculations). Tools
serve the model.

Resources are app-controlled primitives, where application code decides when to fetch
data. They're used to get data into apps for UI display or prompt augmentation (e.g.
autocomplete options, document listings from Google Drive). Resources serve the app.

Prompts are user-controlled primitives, triggered by user actions like button clicks or
slash commands. They're used for predefined workflows (e.g. chat starter buttons in the
Claude interface). Prompts serve users.

Control patterns determine purpose: need Claude capabilities → implement tools. Need app
data → use resources. Need user workflows → create prompts.

Real examples: Claude's chat starter buttons use prompts, Google Drive document selection
uses resources, code execution uses tools.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Name all three MCP server primitives and who controls each one
- Match a feature requirement to the right primitive
- Recall a real example of each primitive in production
        """
    )

with st.expander("📖 The three primitives, side by side — concept", expanded=True):
    st.markdown(
        """
Across this whole module, every feature an MCP server exposes falls into exactly one of
three primitives — and the thing that tells them apart isn't *what* they do, it's **who
decides when they run**.
        """
    )

st.markdown("### Tools vs. Resources vs. Prompts")
st.markdown(
    """
| # | Tools | Resources | Prompts |
|---|---|---|---|
| 1 | Model-controlled — Claude decides when to execute | App-controlled — application code decides when to fetch | User-controlled — triggered by a button click or slash command |
| 2 | Serve the model | Serve the app | Serve the user |
| 3 | Adds a capability (e.g. running JavaScript to calculate something) | Gets data into the app (e.g. autocomplete options, a document listing) | Runs a predefined workflow (e.g. a chat starter button) |
| 4 | Real example: code execution | Real example: Google Drive document selection | Real example: Claude's chat starter buttons |
| 5 | You reach for this when you need **Claude to gain a capability** | You reach for this when you need **data in the app** | You reach for this when you need a **user-triggered workflow** |
"""
)

st.markdown("---")
st.markdown("### Try it yourself — classify the primitive")
st.markdown(
    "For each scenario, decide which primitive it is — based on **who decides when it runs**, "
    "not what it does."
)

QUIZ_QUESTIONS = [
    {
        "question": "Claude decides on its own to run a calculation via a JavaScript execution capability.",
        "options": ["Tool", "Resource", "Prompt"],
        "answer_index": 0,
        "explanation": "Claude — the model — decided to use this capability. Model-controlled = Tool.",
    },
    {
        "question": "Your app fetches a list of documents from Google Drive to populate a picker UI, before the user asks anything.",
        "options": ["Tool", "Resource", "Prompt"],
        "answer_index": 1,
        "explanation": "Application code decided to fetch this data for the UI. App-controlled = Resource.",
    },
    {
        "question": "A user clicks a chat-starter button in the Claude interface to kick off a pre-set workflow.",
        "options": ["Tool", "Resource", "Prompt"],
        "answer_index": 2,
        "explanation": "A user action triggered this. User-controlled = Prompt.",
    },
    {
        "question": "A user types /format, picks a document, and a ready-made instruction is sent to Claude.",
        "options": ["Tool", "Resource", "Prompt"],
        "answer_index": 2,
        "explanation": "Triggered by a slash command — a user action. User-controlled = Prompt.",
    },
    {
        "question": "Claude, mid-conversation, decides to call read_doc_contents to answer a question about a file.",
        "options": ["Tool", "Resource", "Prompt"],
        "answer_index": 0,
        "explanation": "Claude itself chose to call this — model-controlled = Tool, even though it's reading data.",
    },
    {
        "question": "The app pre-loads a document's contents into the prompt before the user even asks about it, based on what they clicked in a picker.",
        "options": ["Tool", "Resource", "Prompt"],
        "answer_index": 1,
        "explanation": "The application decided to fetch and include this data ahead of time. App-controlled = Resource.",
    },
]

render_quiz(QUIZ_QUESTIONS, key="quiz_11")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s11")

st.markdown("### Module complete")
st.markdown(
    """
That's all 11 sections of Introduction to Model Context Protocol — from the problem MCP
solves, through building both a server (tools, resources, prompts) and a client
(`list_tools`/`call_tool`, `read_resource`, `list_prompts`/`get_prompt`), to the Inspector
for debugging it all. Head back to the **Course Overview** in the sidebar to revisit any
section, or jump to another module from the sidebar navigation.
    """
)
