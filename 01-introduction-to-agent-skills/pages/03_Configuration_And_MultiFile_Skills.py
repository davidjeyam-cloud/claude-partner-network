import streamlit as st

from utils.chat import render_lesson_chat
from utils.llm import ask_claude
from utils.quiz import render_quiz
from utils.trace import render_trace

LESSON_CONTEXT = """\
name and description are required frontmatter fields; allowed-tools and model are optional
but powerful additions. A good description answers two questions: what does the skill do,
and when should Claude use it.

allowed-tools restricts which tools Claude can use when the skill is active — useful for
read-only or security-sensitive workflows. Omit it and nothing is restricted.

Progressive disclosure: keep SKILL.md under 500 lines and link to supporting files
(references/, scripts/, assets/) that Claude reads only when needed. Scripts execute
without loading their contents into context — only the output consumes tokens, which is
what keeps context efficient for environment validation, data transformations, and any
operation more reliable as tested code than generated code.
"""

QUIZ_QUESTIONS = [
    {
        "question": "Which fields are optional in SKILL.md frontmatter?",
        "options": [
            "allowed-tools and model",
            "name and description",
            "name and allowed-tools",
            "All fields are required",
        ],
        "answer_index": 0,
        "explanation": "name and description are required; allowed-tools and model are optional additions.",
    },
    {
        "question": "What does setting 'allowed-tools: Read, Grep, Glob, Bash' do?",
        "options": [
            "Restricts Claude to only those tools while the skill is active",
            "Tells Claude which tools to install",
            "Sets the order tools are tried in",
            "Has no effect unless model is also set",
        ],
        "answer_index": 0,
        "explanation": "With allowed-tools set, Claude can't edit or write files while this skill is active — only the listed tools are available.",
    },
    {
        "question": "What's the recommended max length for SKILL.md before splitting into reference files?",
        "options": [
            "500 lines",
            "50 lines",
            "5,000 lines",
            "There's no recommended limit",
        ],
        "answer_index": 0,
        "explanation": "Past ~500 lines, move detailed material into references/ so SKILL.md stays a lean table of contents.",
    },
    {
        "question": "Why tell Claude to run a script rather than read it?",
        "options": [
            "Only the script's output consumes context tokens, not its full source",
            "Scripts can't be read by Claude",
            "Running is faster than reading, but token cost is identical",
            "It's a security requirement, not a context one",
        ],
        "answer_index": 0,
        "explanation": "Executing the script keeps its source out of context entirely — only the output is consumed as tokens.",
    },
]

st.set_page_config(page_title="Configuration and multi-file skills", page_icon="🧩", layout="wide")
st.title("Configuration and multi-file skills")
st.caption("Introduction to Agent Skills — Section 3 of 6 · ~20 minutes")

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Configure advanced skill metadata fields including `allowed-tools` and `model`
- Write effective skill descriptions that reliably trigger on the right requests
- Use `allowed-tools` to restrict what Claude can do when a skill is active
- Organize complex skills using progressive disclosure and multi-file structures
        """
    )

with st.expander("📖 Skill metadata fields — concept", expanded=True):
    st.markdown(
        """
A basic skill works with just a name and description, but the agent skills open standard
supports more fields in the `SKILL.md` frontmatter — two required, the rest optional.

| Field | Required? | Purpose |
|---|---|---|
| `name` | Yes | Identifies the skill. Lowercase letters, numbers, hyphens only. Max 64 characters. Should match the directory name. |
| `description` | Yes | Tells Claude when to use the skill — max 1,024 characters. **The most important field**, since Claude uses it for matching. |
| `allowed-tools` | No | Restricts which tools Claude can use while the skill is active. |
| `model` | No | Pins which Claude model runs the skill. |

**Writing effective descriptions:** be explicit. If someone told you *"your job is to help
with docs"* you wouldn't know what to do — Claude thinks the same way. A good description
answers two questions:

1. **What does the skill do?**
2. **When should Claude use it?**

If a skill isn't triggering when expected, add more keywords that match how you actually
phrase requests — the description is the only thing Claude has to decide relevance.
        """
    )

with st.expander("📐 Core Code Pattern — restricting tools with allowed-tools"):
    st.code(
        """---
name: codebase-onboarding
description: Helps new developers understand how the system works.
allowed-tools: Read, Grep, Glob, Bash
model: sonnet
---
""",
        language="yaml",
    )
    st.markdown(
        """
**Key insight:** with `allowed-tools` set, Claude can only use `Read`, `Grep`, `Glob`, and
`Bash` while this skill is active — no editing, no writing. Useful for read-only or
security-sensitive workflows. **Omit `allowed-tools` entirely and nothing is restricted** —
Claude falls back to its normal permission model.
        """
    )

st.markdown("### Progressive Disclosure")
st.markdown(
    """
Skills share Claude's context window with your conversation — loading a 2,000-line
`SKILL.md` eats a lot of that space and is painful to maintain. **Progressive disclosure**
keeps essential instructions in `SKILL.md` and pushes detailed material into separate files
Claude only reads when it actually needs them:

```
my-skill/
├── SKILL.md              ← essential instructions + links to the files below
├── scripts/               ← executable code
├── references/            ← additional documentation
└── assets/                ← images, templates, other data
```

`SKILL.md` links to the supporting files with clear instructions about *when* to load
them — e.g. read `references/architecture-guide.md` only if someone asks about system
design, never if they're just asking where to add a component. It's a table of contents in
context, not the whole document.

**Rule of thumb: keep `SKILL.md` under 500 lines.** Past that, split content into reference
files.

**Scripts run without loading their contents into context** — only the *output* consumes
tokens. Tell Claude to *run* the script, not *read* it. This is especially useful for
environment validation, data transformations that must stay consistent, and any operation
more reliable as tested code than generated code.
    """
)

st.markdown("---")
st.markdown("### Try it yourself — allowed-tools guardrail simulator")
st.markdown(
    "Configure `allowed-tools` for the `codebase-onboarding` skill above, then check whether "
    "a given action would be permitted while the skill is active."
)

ALL_TOOLS = ["Read", "Grep", "Glob", "Bash", "Edit", "Write"]
col1, col2 = st.columns(2)
with col1:
    allowed = st.multiselect("allowed-tools", ALL_TOOLS, default=["Read", "Grep", "Glob", "Bash"])
with col2:
    action = st.selectbox(
        "Attempted action",
        [
            ("Search the codebase for a function", "Grep"),
            ("Read a file's contents", "Read"),
            ("Find files matching a pattern", "Glob"),
            ("Run a shell command", "Bash"),
            ("Edit an existing file", "Edit"),
            ("Write a brand-new file", "Write"),
        ],
        format_func=lambda x: x[0],
    )

required_tool = action[1]
if required_tool in allowed:
    st.success(f"✅ Allowed — `{required_tool}` is in `allowed-tools`.")
else:
    st.error(f"⛔ Blocked — `{required_tool}` is not in `allowed-tools` for this skill.")

st.markdown("---")
st.markdown("### Try it yourself — description quality checker")
st.markdown(
    "Paste a candidate `description` field. Claude checks whether it answers the two "
    "required questions — **what does it do** and **when should Claude use it** — the same "
    "standard the lesson sets for a description that reliably triggers."
)

candidate = st.text_area(
    "Candidate description",
    value="Helps with documentation.",
    height=80,
)

if st.button("Check this description", type="primary"):
    if not candidate.strip():
        st.warning("Paste a description first.")
    else:
        system_prompt = (
            "You evaluate a single Claude Code skill `description` field. A good description "
            "answers two questions: (1) what does the skill do, and (2) when should Claude use "
            "it — ideally with concrete trigger phrases. Judge the given description against "
            "those two questions. Reply with a verdict (STRONG or WEAK), then 1-2 sentences of "
            "reasoning, then if WEAK, a rewritten description that would trigger reliably."
        )
        user_message = f'Description: "{candidate}"'
        try:
            with st.spinner("Checking against the two-question standard..."):
                answer = ask_claude(system_prompt, user_message)
            st.markdown(answer)
            render_trace(system_prompt, user_message, answer)
        except Exception as e:
            st.error(f"Couldn't reach the Gemini API — check GEMINI_API_KEY in .env. ({e})")

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_03")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s03")

st.markdown("---")
with st.expander("Lesson reflection"):
    st.markdown(
        """
- Think about a skill you'd like to build that involves multiple files. How would you
  structure the `SKILL.md` versus supporting reference files?
- Are there workflows in your team where restricting tool access with `allowed-tools`
  would add an important safety layer?
        """
    )
    st.text_area("Your notes (not saved — just for thinking out loud)", key="reflection_notes_03")

st.markdown("### What's next")
st.markdown(
    "**Section 4 — Skills vs. other Claude Code features:** compare skills to CLAUDE.md, "
    "subagents, hooks, and MCP servers, so you can choose the right tool for each situation."
)
