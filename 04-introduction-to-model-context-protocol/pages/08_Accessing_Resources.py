import json

import streamlit as st

from utils.chat import render_lesson_chat
from utils.quiz import render_quiz

st.set_page_config(page_title="Accessing Resources", page_icon="🧩", layout="wide")
st.title("Accessing Resources")
st.caption("Introduction to Model Context Protocol — Section 8 of 11")

LESSON_CONTEXT = """\
Accessing a resource is how the client retrieves data from a server resource.

Client implementation: a read_resource function takes a URI parameter and requests the
resource from the MCP server, using `await self.session.read_resource(AnyUrl(uri))`. It
then accesses `result.contents[0]` — the first resource from the returned contents list.

Response parsing: check the resource's `mime_type` property to determine the data format.
If `mime_type == "application/json"`, return `json.loads(resource.text)`. Otherwise, return
`resource.text` as plain text.

Resource integration: MCP client functions are called by other application components.
This enables document selection via a CLI interface with arrow keys and space, and the
selected resource's contents are automatically included in the LLM prompt — eliminating the
need for a tool to read document contents during the chat.

Key dependencies: the json module, and pydantic's AnyUrl for URI type handling.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Call `read_resource()` correctly from the client
- Parse a resource's contents based on its MIME type
- Explain why resources reduce the need for a "read" tool during chat
- Know which two dependencies this relies on
        """
    )

with st.expander("📖 Reading a resource — concept", expanded=True):
    st.markdown(
        """
Once a resource is registered on the server (Section 7), the client needs a way to
actually fetch it. That's `read_resource()` — it requests the resource by URI and gets back
a `contents` list; you take the first entry, `result.contents[0]`.

**Parsing depends on MIME type:**

```
if resource.mime_type == "application/json":
    return json.loads(resource.text)
else:
    return resource.text
```

**Why this matters:** because resources are fetched by your *application* rather than
requested by Claude as a tool call, you can pull a document's contents in ahead of time —
e.g. a CLI lets the user pick a document with arrow keys + space, and its contents are
folded straight into the prompt. That **eliminates the need for a tool to read document
contents mid-chat** — the data is already there before Claude even sees the request.
        """
    )

with st.expander("📐 Core Code Pattern — read_resource()"):
    st.code(
        '''import json
from pydantic import AnyUrl


async def read_resource(self, uri: str):
    result = await self.session.read_resource(AnyUrl(uri))
    resource = result.contents[0]

    if resource.mime_type == "application/json":
        return json.loads(resource.text)
    return resource.text
''',
        language="python",
    )
    st.markdown(
        """
**Key insight:** the branch on `mime_type` is the entire parsing contract between server and
client — the server just needs to set the right MIME type, and the client already knows how
to deserialize it correctly.
        """
    )

st.markdown("---")
st.markdown("### Try it yourself — MIME-based parser")
st.markdown(
    "Paste raw `resource.text` and pick the MIME type the server tagged it with. This runs "
    "the exact branch shown above."
)

mime_type = st.radio("resource.mime_type", ["application/json", "text/plain"], horizontal=True)
default_text = '["plan.md", "report.pdf"]' if mime_type == "application/json" else "Q3 roadmap: ship the MCP module."
raw_text = st.text_area("resource.text", value=default_text, height=100)

if st.button("Parse", type="primary"):
    if mime_type == "application/json":
        try:
            parsed = json.loads(raw_text)
            st.success("Parsed as JSON:")
            st.json(parsed)
        except json.JSONDecodeError as e:
            st.error(f"json.loads() failed — this text isn't valid JSON: {e}")
    else:
        st.success("Returned as plain text (no parsing needed):")
        st.code(raw_text, language="text")

QUIZ_QUESTIONS = [
    {
        "question": "What does read_resource() call, and what does it access from the result?",
        "options": [
            "await self.session.read_resource(AnyUrl(uri)), then result.contents[0]",
            "await self.session.get_resource(uri), then result.data",
            "A synchronous requests.get(uri) call",
            "self.session.contents[uri] with no await",
        ],
        "answer_index": 0,
        "explanation": "The client awaits read_resource with an AnyUrl, then takes the first entry of result.contents.",
    },
    {
        "question": "How does the client decide whether to JSON-parse a resource's text?",
        "options": [
            "It checks resource.mime_type — 'application/json' triggers json.loads()",
            "It always tries json.loads() and falls back to text on failure",
            "It inspects the URI string for a .json extension",
            "The server tells the client via a separate message",
        ],
        "answer_index": 0,
        "explanation": "The mime_type property is the explicit signal for how to parse resource.text.",
    },
    {
        "question": "Why do resources reduce the need for a 'read' tool during chat?",
        "options": [
            "The application can fetch resource contents ahead of time and fold them into the prompt directly",
            "Resources are faster than tools at the network level",
            "Tools can't read data, only resources can",
            "Resources don't actually reduce anything — they serve a different purpose entirely",
        ],
        "answer_index": 0,
        "explanation": "Because the app controls when a resource is fetched (e.g. via a document picker), the content is already in context before Claude needs to ask for it.",
    },
    {
        "question": "Which two dependencies does this client-side implementation rely on?",
        "options": [
            "json and pydantic's AnyUrl",
            "requests and BeautifulSoup",
            "asyncio and threading only, no external libraries",
            "yaml and pathlib",
        ],
        "answer_index": 0,
        "explanation": "json.loads() handles JSON parsing, and AnyUrl (from pydantic) types the URI passed to read_resource.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_08")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s08")

st.markdown("### What's next")
st.markdown(
    "**Section 9 — Defining Prompts:** the third MCP primitive — pre-written, tested "
    "instructions a server exposes to clients via slash commands."
)
