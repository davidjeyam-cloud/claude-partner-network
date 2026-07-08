import streamlit as st

from utils.chat import render_lesson_chat
from utils.llm import ask_claude
from utils.quiz import render_quiz
from utils.trace import render_trace

LESSON_CONTEXT = """\
A skill is a directory containing a SKILL.md file with metadata (name, description) in
frontmatter and instructions below. Claude loads only skill names and descriptions at
startup, then matches incoming requests against those descriptions using semantic matching.

Before Claude loads the full skill content into context, it asks the user to confirm —
this keeps the user aware of what context is being pulled in.

Skill priority for name conflicts, highest to lowest: Enterprise (managed settings) >
Personal (~/.claude/skills) > Project (.claude/skills in a repo) > Plugins (installed
plugins). This lets organizations enforce standards through enterprise skills while still
allowing individual customization. To avoid conflicts, use descriptive names instead of
generic ones like "review".

To update a skill, edit its SKILL.md. To remove one, delete its directory. Always restart
Claude Code for changes to take effect, since skills load at startup.
"""

QUIZ_QUESTIONS = [
    {
        "question": "What must you do after creating or editing a skill for the change to take effect?",
        "options": [
            "Restart Claude Code",
            "Nothing — changes apply instantly",
            "Re-run 'claude init'",
            "Push the skill to GitHub",
        ],
        "answer_index": 0,
        "explanation": "Claude Code loads skills at startup, so you must restart your session for new or edited skills to be picked up.",
    },
    {
        "question": "What happens right before Claude loads the full content of a matched skill?",
        "options": [
            "Claude asks you to confirm loading it",
            "Claude silently loads it with no confirmation",
            "Claude emails you a summary",
            "Claude runs it in a sandbox first",
        ],
        "answer_index": 0,
        "explanation": "The confirmation step keeps you aware of exactly what context is being pulled into the conversation.",
    },
    {
        "question": "If a Personal skill and a Project skill share the same name, which one wins?",
        "options": [
            "The Project skill",
            "The Personal skill",
            "Whichever was created most recently",
            "Neither loads — Claude errors out",
        ],
        "answer_index": 1,
        "explanation": "Priority order is Enterprise > Personal > Project > Plugins, so Personal outranks Project.",
    },
    {
        "question": "How do you remove a skill?",
        "options": [
            "Delete its directory",
            "Set 'active: false' in the frontmatter",
            "Rename SKILL.md to SKILL.md.bak",
            "Skills can't be removed once created",
        ],
        "answer_index": 0,
        "explanation": "There's no disable flag — deleting the skill's directory removes it, then restart Claude Code.",
    },
]

st.set_page_config(page_title="Creating your first skill", page_icon="🧩", layout="wide")
st.title("Creating your first skill")
st.caption("Introduction to Agent Skills — Section 2 of 6 · ~20 minutes")

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Create a skill from scratch with proper frontmatter structure
- Test and verify that a skill loads correctly in Claude Code
- Explain how Claude Code matches incoming requests to available skills
- Describe the skill priority hierarchy (Enterprise, Personal, Project, Plugins)
        """
    )

with st.expander("📖 Creating a skill — concept", expanded=True):
    st.markdown(
        """
We'll build a personal skill that teaches Claude how to write PR descriptions in a
consistent format. Since it's a personal skill, it lives in your home directory and works
across all your projects.

First, create a directory for the skill inside the skills folder — the directory name
should match the skill name:

```bash
mkdir -p ~/.claude/skills/pr-description
```

Then create a `SKILL.md` file inside it. The **name** identifies the skill. The
**description** is the matching criteria — it tells Claude when to use it. Everything after
the frontmatter is the instructions Claude follows once the skill activates.

**Testing it:** Claude Code loads skills at startup, so restart your session after creating
one, then confirm it appears in the available skills list. To try it, make changes on a
branch and say something like *"write a PR description for my changes"* — Claude will
indicate it's using the skill, check your diff, and follow the template every time.

**Updating and removing:** edit `SKILL.md` to update a skill, delete its directory to
remove one. Always restart Claude Code afterward for changes to take effect.
        """
    )

with st.expander("📐 Core Code Pattern — a complete SKILL.md"):
    st.code(
        """---
name: pr-description
description: Writes pull request descriptions. Use when creating a PR, writing a PR, or when the user asks to summarize changes for a pull request.
---

When writing a PR description:

1. Run `git diff main...HEAD` to see all changes on this branch
2. Write a description following this format:

## What
One sentence explaining what this PR does.

## Why
Brief context on why this change is needed

## Changes
- Bullet points of specific changes made
- Group related changes together
- Mention any files deleted or renamed
""",
        language="markdown",
    )
    st.markdown(
        """
**Key insight:** the frontmatter (`name`, `description`) is all Claude loads at startup —
cheap to scan across every skill on your system. The body only loads once this specific
skill is matched and confirmed, which is what keeps dozens of skills from bloating context.
        """
    )

st.markdown("### How Skill Matching Works")
st.markdown(
    """
1. At startup, Claude Code scans four locations for skills but only loads each one's
   `name` and `description` — never the full body yet.
2. When you send a request, Claude compares it against every available description using
   **semantic matching** — intent, not just keyword overlap. *"Explain what this function
   does"* would match a skill described as *"explain code with visual diagrams"* because the
   intent overlaps, even with no shared words.
3. Once a match is found, **Claude asks you to confirm** loading the skill — this keeps you
   aware of what context is being pulled in.
4. After you confirm, Claude reads the complete `SKILL.md` and follows its instructions.
    """
)

st.markdown("### Skill Priority Hierarchy")
st.markdown(
    """
| Rank | Scope | Location | Notes |
|---|---|---|---|
| 1 (highest) | Enterprise | Managed settings | Lets organizations enforce standards org-wide |
| 2 | Personal | `~/.claude/skills` | Your own customization, follows you everywhere |
| 3 | Project | `.claude/skills` in the repo | Shared with anyone who clones the repo |
| 4 (lowest) | Plugins | Installed plugins | Lowest priority — easiest to override |
"""
)
st.markdown(
    "If a name conflicts across scopes, the higher-priority scope wins — e.g. a company "
    "enterprise `code-review` skill beats a personal skill of the same name. **To avoid "
    "conflicts, use descriptive names** — `frontend-review` or `backend-review` instead of "
    "just `review`."
)

st.markdown("---")
st.markdown("### Try it yourself — priority resolver")
st.markdown(
    "Suppose a skill named **`code-review`** exists in more than one scope at once. "
    "Tick every scope where it's defined and see which one Claude Code actually loads."
)

PRIORITY = ["Enterprise", "Personal", "Project", "Plugins"]
cols = st.columns(4)
present = {}
for col, scope in zip(cols, PRIORITY):
    with col:
        present[scope] = st.checkbox(scope, value=(scope in ("Personal", "Project")))

active = [s for s in PRIORITY if present[s]]
if not active:
    st.warning("No scope selected — `code-review` isn't defined anywhere, so nothing loads.")
else:
    winner = active[0]
    st.success(f"**{winner}** wins — it's the highest-priority scope where `code-review` is defined.")
    if len(active) > 1:
        st.caption(f"Shadowed: {', '.join(active[1:])} (defined, but lower priority)")

st.markdown("---")
st.markdown("### See the skill in action")
st.markdown(
    "This runs the actual `pr-description` skill instructions above as a system prompt "
    "against a real (mocked) `git diff`, exactly like Claude Code would after matching and "
    "confirming the skill."
)

SKILL_INSTRUCTIONS = """When writing a PR description:

1. Read the diff provided.
2. Write a description following this format:

## What
One sentence explaining what this PR does.

## Why
Brief context on why this change is needed

## Changes
- Bullet points of specific changes made
- Group related changes together
- Mention any files deleted or renamed"""

sample_diff = """diff --git a/utils/llm.py b/utils/llm.py
index 3a1e2c4..9b7f001 100644
--- a/utils/llm.py
+++ b/utils/llm.py
@@ -18,3 +18,10 @@ def ask_claude(system, user, model=MODEL):
     )
     return response.content[0].text
+
+
+def ask_claude_with_retry(system, user, model=MODEL, retries=3):
+    for attempt in range(retries):
+        try:
+            return ask_claude(system, user, model)
+        except Exception:
+            if attempt == retries - 1:
+                raise
diff --git a/tests/test_llm.py b/tests/test_llm.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/tests/test_llm.py
"""

diff_input = st.text_area("Mock `git diff main...HEAD`", value=sample_diff, height=220)

if st.button("Run the pr-description skill", type="primary"):
    if not diff_input.strip():
        st.warning("Paste a diff first.")
    else:
        user_message = f"Diff:\n{diff_input}"
        try:
            with st.spinner("Applying the pr-description skill..."):
                answer = ask_claude(SKILL_INSTRUCTIONS, user_message)
            st.markdown(answer)
            render_trace(SKILL_INSTRUCTIONS, user_message, answer)
        except Exception as e:
            st.error(f"Couldn't reach the Gemini API — check GEMINI_API_KEY in .env. ({e})")

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_02")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s02")

st.markdown("---")
with st.expander("Lesson reflection"):
    st.markdown(
        """
- What's one task in your daily workflow that you could turn into a skill right now?
  What would the description look like?
- How might the priority hierarchy affect your team's skill management strategy? Would
  you rely more on personal or project-level skills?
        """
    )
    st.text_area("Your notes (not saved — just for thinking out loud)", key="reflection_notes_02")

st.markdown("### What's next")
st.markdown(
    "**Section 3 — Configuration and multi-file skills:** metadata fields, tool "
    "restrictions with `allowed-tools`, and structuring larger skills with progressive "
    "disclosure and multi-file organization."
)
