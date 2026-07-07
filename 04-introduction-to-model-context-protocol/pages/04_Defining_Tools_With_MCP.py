import streamlit as st

from utils.chat import render_lesson_chat
from utils.llm import ask_claude_with_tools
from utils.quiz import render_quiz

st.set_page_config(page_title="Defining Tools with MCP", page_icon="🧩", layout="wide")
st.title("Defining Tools with MCP")
st.caption("Introduction to Model Context Protocol — Section 4 of 11")

LESSON_CONTEXT = """\
The MCP Python SDK simplifies tool creation versus writing manual JSON schemas.

Tool definition syntax: the @mcp.tool decorator, applied to a function with typed
parameters and Field descriptions.

Document storage: an in-memory dictionary with doc_id keys and content values.

Tool 1 - read_doc_contents: takes a doc_id string parameter, returns the document's content
from the docs dictionary, and raises a ValueError if the document isn't found.

Tool 2 - edit_document: takes doc_id, old_string, and new_string parameters, and performs a
find/replace on the document's content, including existence validation first.

Benefits of the MCP Python SDK: it auto-generates JSON schemas from the decorated
functions, allows single-line server creation, and eliminates manual schema writing.

Parameter definition uses Field() with a description for tool arguments, imported from
pydantic.

Error handling: validate a document's existence before operating on it, and raise a
ValueError for missing documents.

Implementation pattern: decorator → function definition → parameter typing → validation →
core logic.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Use the `@mcp.tool` decorator to turn a function into an MCP tool
- Use `Field()` to give Claude a description of each parameter
- Follow the validate-then-act error handling pattern for tools
- See the difference between a read tool and a write tool in practice
        """
    )

with st.expander("📖 Defining tools — concept", expanded=True):
    st.markdown(
        """
Writing raw JSON tool schemas by hand is tedious and easy to get out of sync with your
actual function signature. The **MCP Python SDK** fixes this: decorate a normal typed
Python function with `@mcp.tool`, and the SDK auto-generates the JSON schema from it —
no schema maintenance, no drift.

**Storage:** the example project keeps documents in a simple in-memory dictionary, keyed
by `doc_id`.

**Two tools:**

| Tool | Parameters | Behavior |
|---|---|---|
| `read_doc_contents` | `doc_id` | Returns the document's content; raises `ValueError` if not found |
| `edit_document` | `doc_id`, `old_string`, `new_string` | Validates the doc exists, then find/replaces its content |

**The implementation pattern is always the same:** decorator → function definition →
typed parameters → existence validation → core logic. Validate *before* you act, and raise
`ValueError` rather than silently doing nothing when a document is missing.
        """
    )

with st.expander("📐 Core Code Pattern — @mcp.tool with Field()"):
    st.code(
        '''from pydantic import Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("docs-server")
docs = {
    "plan.md": "Q3 roadmap: ship the MCP module...",
    "report.pdf": "Quarterly report: revenue up 12%...",
}


@mcp.tool()
def read_doc_contents(
    doc_id: str = Field(description="The id of the document to read"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    return docs[doc_id]


@mcp.tool()
def edit_document(
    doc_id: str = Field(description="The id of the document to edit"),
    old_string: str = Field(description="Text to find"),
    new_string: str = Field(description="Text to replace it with"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    docs[doc_id] = docs[doc_id].replace(old_string, new_string)
    return f"Updated {doc_id}"
''',
        language="python",
    )
    st.markdown(
        """
**Key insight:** the SDK reads the type hints and `Field()` descriptions to build the JSON
schema Claude sees — you never write that schema by hand, and it can never drift out of
sync with the function's real signature.
        """
    )

st.markdown("---")
st.markdown("### See both tools in action")
st.markdown(
    "This runs the real tools above against the live document store below — ask Claude to "
    "**read** a document or **edit** one, and watch it pick the right tool and call it with "
    "real arguments. Edits actually mutate the store for the rest of this session."
)

if "docs4" not in st.session_state:
    st.session_state.docs4 = {
        "plan.md": "Q3 roadmap: ship the MCP module, ship the Claude API module.",
        "report.pdf": "Quarterly report: revenue up 12%, churn down 3%.",
    }

st.markdown("**Current document store:**")
st.json(st.session_state.docs4)

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


def execute_tool(name: str, tool_input: dict) -> str:
    docs = st.session_state.docs4
    doc_id = tool_input.get("doc_id", "")
    if doc_id not in docs:
        return f"Error: document '{doc_id}' not found"
    if name == "read_doc_contents":
        return docs[doc_id]
    if name == "edit_document":
        old, new = tool_input.get("old_string", ""), tool_input.get("new_string", "")
        if old not in docs[doc_id]:
            return f"Error: '{old}' not found in {doc_id}"
        docs[doc_id] = docs[doc_id].replace(old, new)
        return f"Updated {doc_id}"
    return "Unknown tool"


query = st.text_input(
    "Your request",
    value="In plan.md, replace 'churn down 3%' with nothing — wait, change 'revenue up 12%' to 'revenue up 15%' in report.pdf",
    key="tool_query_04",
)

if st.button("Send to Claude", type="primary", key="run_04"):
    if not query.strip():
        st.warning("Type a request first.")
    else:
        system_prompt = (
            "You are an assistant with access to a document store via read_doc_contents "
            "and edit_document tools. Use them as needed to satisfy the user's request."
        )
        try:
            with st.spinner("Running the tool-use exchange..."):
                result = ask_claude_with_tools(system_prompt, query, TOOLS, execute_tool)

            if result["tool_call"] is None:
                st.info("Claude answered without needing a tool:")
                st.markdown(result["final_text"])
            else:
                st.markdown(f"**Tool called:** `{result['tool_call'].name}`")
                st.json(result["tool_call"].input)
                st.markdown("**Tool result:**")
                st.code(result["tool_result"], language="text")
                st.markdown("**Claude's final response:**")
                st.success(result["final_text"])
                st.markdown("**Document store after this call:**")
                st.json(st.session_state.docs4)

            with st.expander("Execution trace — raw API responses"):
                st.markdown("**System prompt:**")
                st.code(system_prompt, language="text")
                st.markdown("**Raw first response:**")
                st.code(str(result["raw_first"]), language="text")
                if "raw_final" in result:
                    st.markdown("**Raw final response:**")
                    st.code(str(result["raw_final"]), language="text")
        except Exception as e:
            st.error(f"Couldn't reach the Claude API — check ANTHROPIC_API_KEY in .env. ({e})")

if st.button("Reset document store", key="reset_04"):
    del st.session_state["docs4"]
    st.rerun()

QUIZ_QUESTIONS = [
    {
        "question": "What does the MCP Python SDK auto-generate from a decorated function?",
        "options": [
            "The JSON tool schema Claude sees",
            "The Streamlit UI",
            "A unit test suite",
            "The .env file",
        ],
        "answer_index": 0,
        "explanation": "The SDK reads type hints and Field() descriptions to build the schema, so you never hand-write or maintain it.",
    },
    {
        "question": "What should read_doc_contents do if the doc_id doesn't exist?",
        "options": [
            "Raise a ValueError",
            "Return an empty string silently",
            "Create a new empty document with that id",
            "Retry with a default doc_id",
        ],
        "answer_index": 0,
        "explanation": "The lesson's error handling pattern is to validate existence and raise ValueError for missing documents.",
    },
    {
        "question": "What library provides Field() for parameter descriptions?",
        "options": [
            "pydantic",
            "dataclasses",
            "typing",
            "streamlit",
        ],
        "answer_index": 0,
        "explanation": "Field() is imported from pydantic and attaches a description to each typed parameter.",
    },
    {
        "question": "What's the correct implementation order for a tool function?",
        "options": [
            "Decorator, function definition, typed parameters, validation, core logic",
            "Core logic, then validation, then decorator",
            "Validation first, then decorator, then parameters",
            "Order doesn't matter as long as @mcp.tool is present",
        ],
        "answer_index": 0,
        "explanation": "This is the consistent implementation pattern the lesson describes for every tool.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_04")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s04")

st.markdown("### What's next")
st.markdown(
    "**Section 5 — The Server Inspector:** the in-browser debugger for testing an MCP "
    "server's tools directly, without wiring up a full client application first."
)
