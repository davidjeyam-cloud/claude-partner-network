import streamlit as st

from utils.chat import render_lesson_chat
from utils.quiz import render_quiz

st.set_page_config(page_title="Prompts in the Client", page_icon="🧩", layout="wide")
st.title("Prompts in the Client")
st.caption("Introduction to Model Context Protocol — Section 10 of 11")

LESSON_CONTEXT = """\
On the client side, list_prompts() calls await self.session.list_prompts() and returns
result.props. get_prompt() calls await self.session.get_prompt(prompt_name, arguments) and
returns result.messages.

Prompt workflow: the client requests a prompt by name → passes arguments as keyword
parameters → the MCP server interpolates those arguments into the prompt template →
returns the formatted messages for the AI model.

Arguments flow: client arguments → the prompt function's keyword arguments → interpolated
into the prompt text (e.g. a document_id parameter gets inserted into the prompt template).

Return format: a messages array that forms the conversation input for the AI model.

CLI usage: the user types /format → selects a document → the prompt (with the document id)
is sent to Claude → Claude uses tools to fetch the document → returns the formatted
result.

Key concept: prompts are server-defined templates that clients can invoke with parameters,
enabling reusable AI instructions with dynamic content insertion.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Use `list_prompts()` and `get_prompt()` on the client
- Trace how arguments flow from the client call into the interpolated prompt text
- Explain the return format both functions produce
- Walk through the full `/format` CLI usage end to end
        """
    )

with st.expander("📖 Client-side prompts — concept", expanded=True):
    st.markdown(
        """
Section 9 covered how a server *defines* a prompt. This section is the other half — how the
**client** discovers and invokes one.

| Function | Calls | Returns |
|---|---|---|
| `list_prompts()` | `await self.session.list_prompts()` | `result.props` — the available prompts |
| `get_prompt()` | `await self.session.get_prompt(prompt_name, arguments)` | `result.messages` — ready to send to Claude |

**Argument flow:** whatever the client passes as `arguments` to `get_prompt()` becomes the
prompt function's keyword arguments on the server, which get interpolated straight into the
prompt text — a `document_id` argument from the client ends up inside the returned message.

**Full CLI usage, end to end:** the user types `/format` → picks a document → the client
calls `get_prompt("format", {"doc_id": "plan.md"})` → gets back a `messages` array → sends
that to Claude → Claude uses its tools to fetch the document and act on it → the formatted
result comes back to the user.
        """
    )

with st.expander("📐 Core Code Pattern — list_prompts() and get_prompt()"):
    st.code(
        '''async def list_prompts(self):
    result = await self.session.list_prompts()
    return result.props


async def get_prompt(self, prompt_name: str, arguments: dict):
    result = await self.session.get_prompt(prompt_name, arguments)
    return result.messages


# CLI usage:
# /format  →  user picks "plan.md"
messages = await client.get_prompt("format", {"doc_id": "plan.md"})
# messages is now ready to send straight to Claude
''',
        language="python",
    )
    st.markdown(
        """
**Key insight:** the client never constructs prompt text itself — it only passes a prompt
*name* and *arguments*, and trusts the server to hand back fully-formed messages. All the
prompt engineering lives on the server side, exactly where Section 9 put it.
        """
    )

st.markdown("---")
st.markdown("### Trace the argument flow yourself")
st.markdown(
    "Enter a `doc_id` the way a CLI user would after typing `/format`, and see how it flows "
    "from the client's `get_prompt()` call through to the interpolated message the server "
    "hands back."
)

doc_id_input = st.text_input("doc_id argument (as if selected via /format)", value="plan.md")

st.markdown("**① Client call:**")
st.code(f'client.get_prompt("format", {{"doc_id": "{doc_id_input}"}})', language="python")

st.markdown("**② Server interpolates it into the prompt function's argument:**")
st.code(f'def format_document(doc_id="{doc_id_input}"): ...', language="python")

st.markdown("**③ result.messages returned to the client:**")
st.json(
    [
        {
            "role": "user",
            "content": (
                f"Please read the document '{doc_id_input}' and rewrite it in clean, "
                "well-structured markdown. Preserve all the original information."
            ),
        }
    ]
)

QUIZ_QUESTIONS = [
    {
        "question": "What does list_prompts() return?",
        "options": [
            "result.props — the available prompts",
            "result.messages — ready-to-send messages",
            "A raw JSON schema for each prompt",
            "Nothing — it's a fire-and-forget call",
        ],
        "answer_index": 0,
        "explanation": "list_prompts() awaits the session call and returns result.props, the list of available prompts.",
    },
    {
        "question": "What does get_prompt() return?",
        "options": [
            "result.messages — ready to send to Claude",
            "result.props — the list of prompts",
            "A single string with no structure",
            "The tool schema for the prompt's arguments",
        ],
        "answer_index": 0,
        "explanation": "get_prompt() returns result.messages, the fully-formed conversation input for the model.",
    },
    {
        "question": "How do client-side arguments end up in the final prompt text?",
        "options": [
            "They're passed as keyword arguments to the server's prompt function, which interpolates them into the template",
            "The client interpolates them locally before sending",
            "They're ignored — prompts never take arguments",
            "They're stored in a database and fetched by doc_id later",
        ],
        "answer_index": 0,
        "explanation": "The client just passes arguments; the server's prompt function does the actual interpolation.",
    },
    {
        "question": "In the /format CLI flow, what does Claude do once it receives the prompt's messages?",
        "options": [
            "Uses its tools to fetch the document and act on it",
            "Immediately returns the raw messages unchanged",
            "Requests the user to type the document contents manually",
            "Calls get_prompt() again for confirmation",
        ],
        "answer_index": 0,
        "explanation": "The prompt hands Claude an instruction; it then uses tools like read_doc_contents to actually complete the task.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_10")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s10")

st.markdown("### What's next")
st.markdown(
    "**Section 11 — MCP Review:** the three server primitives — tools, resources, and "
    "prompts — side by side, and how to decide which one a given feature needs."
)
