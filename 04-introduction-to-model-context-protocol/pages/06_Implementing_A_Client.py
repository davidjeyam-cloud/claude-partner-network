import streamlit as st

from utils.chat import render_lesson_chat
from utils.quiz import render_quiz

st.set_page_config(page_title="Implementing a Client", page_icon="🧩", layout="wide")
st.title("Implementing a Client")
st.caption("Introduction to Model Context Protocol — Section 6 of 11")

LESSON_CONTEXT = """\
An MCP Client is a wrapper class around a client session, built for connecting to an MCP
server with resource cleanup management.

The Client Session is the actual connection to the MCP server, provided by the MCP Python
SDK, and it requires cleanup when closing.

Resource cleanup is the process needed when shutting down, handled by connect/cleanup and
async enter/async exit functions.

The client's purpose is to expose the MCP server's functionality to the rest of the
codebase — it's the interface between application code and the server.

Key functions:
- list_tools() — calls `await self.session.list_tools()` and returns `result.tools`
- call_tool() — calls `await self.session.call_tool(tool_name, tool_input)`

Implementation flow: the application requests a tool list for Claude → the client calls
list_tools() to get the server's available tools → Claude selects a tool and provides
parameters → the client calls call_tool() to execute it on the server → results are
returned to Claude.

Testing: run client.py directly with a testing harness to verify the connection and tool
listing.

Integration: once implemented, you can run the CLI and have Claude use the tools (e.g.
"what is the contents of the report.pdf document").

Common practice: wrap the client session in a larger class rather than using it directly,
for better resource management.
"""

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Explain what an MCP client wrapper class is responsible for
- Use `list_tools()` and `call_tool()` correctly
- Understand why resource cleanup matters for a client session
- Trace the implementation flow from application request to Claude's tool call
        """
    )

with st.expander("📖 Building the client wrapper — concept", expanded=True):
    st.markdown(
        """
The **Client Session** (from the MCP Python SDK) is the actual connection to an MCP server
— and like any connection, it needs proper cleanup when you're done with it. Rather than
using the session directly everywhere in your codebase, **common practice is to wrap it in
a class** that manages that lifecycle and exposes just two functions to the rest of your
application:

| Function | Does |
|---|---|
| `list_tools()` | `await self.session.list_tools()`, returns `result.tools` |
| `call_tool()` | `await self.session.call_tool(tool_name, tool_input)` |

**Implementation flow:** the application asks the client for a tool list → the client calls
`list_tools()` → Claude picks a tool and supplies parameters → the client calls
`call_tool()` to actually run it on the server → the result comes back to Claude.

**Resource cleanup:** connecting and cleaning up are handled through `connect()`/`cleanup()`
methods, plus Python's async context manager protocol (`__aenter__`/`__aexit__`), so the
connection is reliably closed even if something goes wrong mid-session.
        """
    )

with st.expander("📐 Core Code Pattern — the MCPClient wrapper"):
    st.code(
        '''class MCPClient:
    def __init__(self, server_params):
        self.server_params = server_params
        self.session = None
        self._streams_context = None
        self._session_context = None

    async def connect(self):
        self._streams_context = stdio_client(self.server_params)
        streams = await self._streams_context.__aenter__()
        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()

    async def list_tools(self):
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, tool_name, tool_input):
        return await self.session.call_tool(tool_name, tool_input)

    async def cleanup(self):
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.cleanup()
''',
        language="python",
    )
    st.markdown(
        """
**Key insight:** the wrapper class is the *only* thing in your codebase that talks directly
to `ClientSession`. Everything else calls `list_tools()` / `call_tool()` on the wrapper —
so cleanup, reconnection logic, and error handling live in exactly one place.
        """
    )

QUIZ_QUESTIONS = [
    {
        "question": "What does list_tools() actually call and return?",
        "options": [
            "await self.session.list_tools(), returning result.tools",
            "await self.session.get_tools(), returning a raw dict",
            "A synchronous call with no await needed",
            "It reads a local tools.json file",
        ],
        "answer_index": 0,
        "explanation": "list_tools() awaits the session call and returns the .tools attribute of the result.",
    },
    {
        "question": "Why wrap the client session in a larger class rather than using it directly?",
        "options": [
            "For better resource management — connect/cleanup logic lives in one place",
            "Because ClientSession can't be imported directly",
            "It's required by the MCP spec",
            "To make the code run synchronously instead of async",
        ],
        "answer_index": 0,
        "explanation": "Common practice wraps the session so connection lifecycle and cleanup are centralized rather than scattered.",
    },
    {
        "question": "Which functions handle resource cleanup for the client session?",
        "options": [
            "connect/cleanup and the async __aenter__/__aexit__ methods",
            "open() and close() only",
            "A single teardown() function with no async support",
            "Cleanup happens automatically with no code needed",
        ],
        "answer_index": 0,
        "explanation": "The lesson describes cleanup being handled through connect/cleanup plus the async context manager protocol.",
    },
    {
        "question": "In the implementation flow, what happens right after Claude selects a tool and supplies parameters?",
        "options": [
            "The client calls call_tool() to execute it on the server",
            "The client re-runs list_tools() to double check",
            "The application restarts the session",
            "The server automatically detects the request without a call_tool message",
        ],
        "answer_index": 0,
        "explanation": "Once Claude has chosen a tool and parameters, the client's call_tool() actually executes it on the server.",
    },
]

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_06")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s06")

st.markdown("### What's next")
st.markdown(
    "**Section 7 — Defining Resources:** the second MCP primitive — exposing data for read "
    "operations via direct and templated URIs."
)
