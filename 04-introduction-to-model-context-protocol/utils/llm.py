import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# This course teaches Claude / Claude Code / MCP concepts, but live demos run on
# Google Gemini here — there is no ANTHROPIC_API_KEY available in this environment.
# See CLAUDE.md "LLM Provider" for why. Swap the client below if a real Anthropic
# key ever becomes available; page code only calls the generic functions below.
MODEL = "gemini-2.5-flash"

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def _to_gemini_history(messages: list) -> list:
    role_map = {"user": "user", "assistant": "model"}
    history = []
    for m in messages:
        history.append(
            {"role": role_map.get(m["role"], m["role"]), "parts": [{"text": m["content"]}]}
        )
    return history


def ask_claude_messages(system: str, messages: list, model: str = MODEL) -> str:
    chat = get_client().chats.create(
        model=model,
        config=types.GenerateContentConfig(system_instruction=system),
        history=_to_gemini_history(messages[:-1]),
    )
    response = chat.send_message(messages[-1]["content"])
    return response.text


def ask_claude(system: str, user: str, model: str = MODEL) -> str:
    return ask_claude_messages(system, [{"role": "user", "content": user}], model)


class ToolCall:
    """Minimal name/input view of a function call, so page code that reads
    result["tool_call"].name / .input doesn't need to know which provider ran it."""

    def __init__(self, name: str, input: dict):
        self.name = name
        self.input = input


def _to_gemini_tools(tools: list) -> list:
    declarations = [
        types.FunctionDeclaration(
            name=t["name"], description=t["description"], parameters=t["input_schema"]
        )
        for t in tools
    ]
    return [types.Tool(function_declarations=declarations)]


def ask_claude_with_tools(system: str, user: str, tools: list, tool_executor, model: str = MODEL) -> dict:
    """Runs one real tool-call round trip against the Gemini API — the same
    tool-call/tool-result exchange an MCP client mediates between a model and
    an MCP server, just without the protocol layer in between.
    """
    chat = get_client().chats.create(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=system,
            tools=_to_gemini_tools(tools),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        ),
    )
    first = chat.send_message(user)

    if not first.function_calls:
        return {"tool_call": None, "tool_result": None, "final_text": first.text, "raw_first": first}

    fc = first.function_calls[0]
    tool_input = dict(fc.args)
    tool_result = tool_executor(fc.name, tool_input)

    final = chat.send_message(
        types.Part.from_function_response(name=fc.name, response={"result": tool_result})
    )

    return {
        "tool_call": ToolCall(fc.name, tool_input),
        "tool_result": tool_result,
        "final_text": final.text,
        "raw_first": first,
        "raw_final": final,
    }
