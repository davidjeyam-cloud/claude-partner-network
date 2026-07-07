import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-5"

_client = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def ask_claude_messages(system: str, messages: list, model: str = MODEL) -> str:
    response = get_client().messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        messages=messages,
    )
    return response.content[0].text


def ask_claude(system: str, user: str, model: str = MODEL) -> str:
    return ask_claude_messages(system, [{"role": "user", "content": user}], model)


def ask_claude_with_tools(system: str, user: str, tools: list, tool_executor, model: str = MODEL) -> dict:
    """Runs one real tool-use round trip against the Claude API — the same
    tool_use/tool_result exchange an MCP client mediates between Claude and
    an MCP server, just without the protocol layer in between.
    """
    client = get_client()
    messages = [{"role": "user", "content": user}]

    first = client.messages.create(
        model=model, max_tokens=1024, system=system, tools=tools, messages=messages
    )

    tool_use_block = next((b for b in first.content if b.type == "tool_use"), None)
    if tool_use_block is None:
        text = next((b.text for b in first.content if b.type == "text"), "")
        return {"tool_call": None, "tool_result": None, "final_text": text, "raw_first": first}

    tool_result = tool_executor(tool_use_block.name, tool_use_block.input)

    messages.append({"role": "assistant", "content": first.content})
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": str(tool_result),
                }
            ],
        }
    )

    final = client.messages.create(
        model=model, max_tokens=1024, system=system, tools=tools, messages=messages
    )
    final_text = next((b.text for b in final.content if b.type == "text"), "")

    return {
        "tool_call": tool_use_block,
        "tool_result": tool_result,
        "final_text": final_text,
        "raw_first": first,
        "raw_final": final,
    }
