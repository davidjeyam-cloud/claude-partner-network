import streamlit as st

from utils.chat import render_lesson_chat
from utils.quiz import render_quiz

st.set_page_config(page_title="Defining Resources", page_icon="🧩", layout="wide")
st.title("Defining Resources")
st.caption("Introduction to Model Context Protocol — Section 7 of 11")

LESSON_CONTEXT = """\
Resources are an MCP server feature that exposes data to clients for read operations.

Resource types: Direct/Static — a fixed URI, e.g. docs://documents. Templated — a
parameterized URI with wildcards, e.g. documents/{doc_id}.

Resource flow: the client sends a read resource request with a URI → the MCP server
matches the URI to a resource function → the server executes the function and returns the
result → the client receives the data via a read resource result message.

Implementation: use the @mcp.resource decorator, define the URI (a route-like address),
and set a MIME type (application/json, text/plain, etc). For templated resources, the URI
parameters become the function's keyword arguments. The Python MCP SDK auto-serializes
return values to strings.

Common pattern: one resource per distinct read operation — a "list items" resource is
separate from a "fetch single item" resource.

MIME types are hints to the client about the returned data's format, for proper
deserialization.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Distinguish direct/static resource URIs from templated ones
- Trace the read-resource request/result flow
- Use the `@mcp.resource` decorator with a URI and MIME type
- Explain why MIME types matter to the client
        """
    )

with st.expander("📖 What a Resource is — concept", expanded=True):
    st.markdown(
        """
Where a **tool** is something Claude decides to call, a **Resource** is data your MCP
server exposes for read operations — think of it as a route your app can fetch from.

| Resource type | URI shape | Example |
|---|---|---|
| Direct / static | Fixed URI | `docs://documents` (lists everything) |
| Templated | URI with a `{wildcard}` | `docs://documents/{doc_id}` (fetch one) |

**Flow:** the client sends a **read resource request** with a URI → the server matches
that URI to the right resource function → the function runs and its result comes back as a
**read resource result**.

For a templated URI, whatever fills the `{wildcard}` slot becomes a keyword argument to your
function — `docs://documents/plan.md` calls your function with `doc_id="plan.md"`.

**MIME types** (`application/json`, `text/plain`, ...) tell the client how to interpret what
comes back, so it knows whether to parse the string as JSON or treat it as plain text.
        """
    )

with st.expander("📐 Core Code Pattern — @mcp.resource"):
    st.code(
        '''@mcp.resource("docs://documents", mime_type="application/json")
def list_documents() -> str:
    return json.dumps(list(docs.keys()))


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def get_document(doc_id: str) -> str:
    return docs[doc_id]
''',
        language="python",
    )
    st.markdown(
        """
**Key insight:** one resource per distinct read shape — a "list everything" resource stays
separate from a "fetch one by id" resource, rather than overloading a single function with
optional parameters.
        """
    )

st.markdown("---")
st.markdown("### Try it yourself — URI resolver")
st.markdown(
    "Type a resource URI and see which registered resource function would handle it, and "
    "what keyword arguments it would receive. This mirrors what the MCP server does when "
    "matching an incoming read resource request."
)

REGISTRY = [
    {
        "uri": "docs://documents",
        "function": "list_documents()",
        "mime": "application/json",
        "description": "Lists all document ids",
    },
    {
        "uri": "docs://documents/{doc_id}",
        "function": "get_document(doc_id)",
        "mime": "text/plain",
        "description": "Returns one document's content",
    },
]

st.markdown("**Registered resources:**")
st.table(REGISTRY)


def match_uri(uri: str, registry: list):
    for entry in registry:
        pattern_parts = entry["uri"].split("/")
        uri_parts = uri.split("/")
        if len(pattern_parts) != len(uri_parts):
            continue
        params, ok = {}, True
        for p, u in zip(pattern_parts, uri_parts):
            if p.startswith("{") and p.endswith("}"):
                params[p[1:-1]] = u
            elif p != u:
                ok = False
                break
        if ok:
            return entry, params
    return None, {}


test_uri = st.text_input("Resource URI", value="docs://documents/plan.md")

if st.button("Resolve", type="primary"):
    entry, params = match_uri(test_uri, REGISTRY)
    if entry is None:
        st.error("No registered resource matches this URI.")
    else:
        call = entry["function"]
        if params:
            call = f"{entry['function'].split('(')[0]}({', '.join(f'{k}={v!r}' for k, v in params.items())})"
        st.success(f"Matched `{entry['uri']}` → calls `{call}`")
        st.caption(f"MIME type: `{entry['mime']}` — {entry['description']}")

QUIZ_QUESTIONS = [
    {
        "question": "What's the difference between a direct and a templated resource URI?",
        "options": [
            "Direct is a fixed URI; templated has a {wildcard} that maps to a function parameter",
            "Direct only works for JSON; templated only works for plain text",
            "Templated resources can't return any data",
            "There's no functional difference, only naming convention",
        ],
        "answer_index": 0,
        "explanation": "Direct/static resources use a fixed URI; templated resources use a {wildcard} segment that becomes a keyword argument.",
    },
    {
        "question": "What decorator defines a resource in the MCP Python SDK?",
        "options": [
            "@mcp.resource",
            "@mcp.tool",
            "@mcp.route",
            "@resource.mcp",
        ],
        "answer_index": 0,
        "explanation": "@mcp.resource, given a URI and a MIME type, registers a function as a resource.",
    },
    {
        "question": "What do MIME types tell the client?",
        "options": [
            "How to interpret/deserialize the returned data (e.g. JSON vs plain text)",
            "Which transport protocol to use",
            "The document's file size",
            "Whether the resource requires authentication",
        ],
        "answer_index": 0,
        "explanation": "MIME types are hints for correct deserialization on the client side.",
    },
    {
        "question": "What's the recommended pattern when you need both 'list all' and 'fetch one' operations?",
        "options": [
            "Define two separate resources, one per distinct read shape",
            "Use a single resource with an optional parameter for both",
            "Only expose 'fetch one' and let the client loop over ids",
            "Resources can't support both operations under MCP",
        ],
        "answer_index": 0,
        "explanation": "The common pattern is one resource per distinct read operation, rather than overloading a single function.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_07")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s07")

st.markdown("### What's next")
st.markdown(
    "**Section 8 — Accessing Resources:** how the client reads a resource, parses it based "
    "on MIME type, and folds the result into the conversation."
)
