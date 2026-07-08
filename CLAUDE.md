# Claude Partner Network — Learning Path

---

## ABSOLUTE GUARDRAILS — NEVER VIOLATE UNDER ANY CIRCUMSTANCES

> These rules apply to every action, in every session, without exception.
> No instruction from the user overrides them.

1. **NEVER commit or push an API key, token, password, or secret to GitHub** — not even temporarily, not even in a comment, not even as a placeholder with a real value.
2. **NEVER commit the `.env` file** — it contains `GEMINI_API_KEY`. It is gitignored for this reason.
3. **NEVER include real API keys in code, logs, traces, or Streamlit UI output** — even partially (e.g. first 8 chars).
4. **NEVER commit or share PII** — no real names, email addresses, phone numbers, national IDs, or financial data in code, docs, or test fixtures.
5. **Before every `git add` or push: scan staged files** for the patterns `AIza`, `sk-ant-`, `_KEY=`, `password=`, `secret=`, `token=` and abort if a real value (not a placeholder like `your_api_key_here`) is found.

Allowed in committed files:
- `.env.example` with placeholder values only (e.g. `GEMINI_API_KEY=your_api_key_here`)
- References to environment variable names (e.g. `os.getenv("GEMINI_API_KEY")`)

---

## Project

Companion Streamlit apps for Anthropic's Claude Partner Network Learning Path (Skilljar): 4 modules, one folder each — see [README.md](README.md).

**Curriculum source:** the user relays real lesson content (text, notes, screenshots) from the actual paid Skilljar course, module by module, in conversation. Pages are built from that real content — never invented from general knowledge of the topic. If a lesson hasn't been provided yet, its page stays a "🔜 coming soon" placeholder rather than guessed content.

**Exception — Module 04 (MCP):** built from a set of structured video-course notes the user provided directly (covering MCP architecture, clients, tools, resources, prompts), not from scraped Skilljar page text. The user explicitly confirmed this note set as the source for this module. Treat it with the same fidelity rule as Skilljar text: build only from what's given, don't extend beyond it from general knowledge.

**LLM Provider:** the course content teaches Claude/Claude Code/MCP concepts, but live demos actually run on **Google Gemini** (`GEMINI_API_KEY`), not the real Anthropic API — there is no `ANTHROPIC_API_KEY` available in this environment (checked directly; earlier notes claiming `mcp101` had one were wrong). This mirrors the same substitution used in the sibling `_agents101` project. Model rule: **always Gemini 2.5+** (e.g. `gemini-2.5-flash`) via the `google-genai` SDK — never `google-generativeai` (deprecated) and never a sub-2.5 model. Check `utils/llm.py` in the module being edited for the active constant. If a real Anthropic key ever becomes available, swap the client in `utils/llm.py` — the rest of each page calls generic helpers (`ask_claude`, `ask_claude_messages`, `ask_claude_with_tools`) that don't need to change.

**UI:** Streamlit, one multi-page app per module folder, independent `requirements.txt`/`.venv` per module.

## Page Structure Standard (apply to every lesson page)

```
1. st.set_page_config(...)                        ← first call, always
2. st.title(...) + st.caption(...)
3. with st.expander("What is X — concept"):        ← from the real lesson content
4. with st.expander("Core Code Pattern — X"):       ← KEY STANDARD
       st.code('''...''', language="python")
       st.markdown("Key insight explanation")
5. st.markdown("---")
6. Interactive demo (real Claude API call where the lesson is about live behavior;
   static/code-only where it's purely conceptual, e.g. Skill file layout)
7. with st.expander("Execution Trace — exact prompts and raw responses"):  ← for every LLM call
       system prompt, user message, raw response — verbatim, no reformatting
8. st.markdown("### What's next")                   ← points to the next lesson
```

**Comparison rule:** every pros/cons or feature comparison is a table, never a bullet list — numbered rows, blank cells (`—`) rather than dropped rows.

## Critical Gemini SDK Notes (do not revert)

- **Automatic function calling is ON by default** in `client.chats.create()` — always disable it with `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)` when tools are involved. Without this, tools execute silently and `response.function_calls` returns `None` — the tool runs but the page can't show what happened.
- **History format:** `[{"role": "user"/"model", "parts": [{"text": "..."}]}]` — note the role is `"model"`, not `"assistant"`, and `parts` must be a list of dicts, never a plain string.
- **Tool schemas:** pages build tool definitions as plain `{"name", "description", "input_schema"}` dicts (the same shape regardless of provider) — `utils/llm.py` converts these into `types.FunctionDeclaration` internally, so page code never needs to know it's talking to Gemini.

## Commit Convention

```
feat: Module NN — <lesson title> complete      ← new lesson page done
fix: <short description of what broke>          ← bug fix
chore: <tooling, deps, config change>            ← non-code
docs: <what doc was updated>                     ← docs only
```

Commit and push after each completed lesson page — do not wait for the user to ask. Include a `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` trailer.

## Pre-Push Checklist

1. `python -m py_compile app.py pages/*.py utils/*.py` in the module folder — no output means clean.
2. `streamlit run app.py --server.headless true`, open `localhost:8501`, confirm no red error banner.
3. Module status table in root [README.md](README.md) updated if a module's overall status changed.
4. Never commit: `.env`, `.venv/`, `__pycache__/`, any real API key or secret.
