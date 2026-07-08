import streamlit as st

from utils.chat import render_lesson_chat
from utils.llm import ask_claude
from utils.quiz import render_quiz
from utils.trace import render_trace

LESSON_CONTEXT = """\
A Skill is a folder of instructions and resources that Claude Code can discover and use to
handle a task more accurately. Each skill lives in a SKILL.md file with a name and
description in its frontmatter. The description is how Claude decides whether to use the
skill — Claude compares a request against every available skill's description and activates
the ones that match.

Personal skills live in ~/.claude/skills (Windows: C:/Users/<you>/.claude/skills) and follow
you across every project. Project skills live in .claude/skills at the repo root, are
committed to version control, and are shared with anyone who clones the repo.

Skills vs. CLAUDE.md vs. Slash Commands: CLAUDE.md loads into every conversation and is best
for rules that always apply. Skills load on demand, only when the description matches, and
are best for task-specific knowledge — this keeps the context window efficient. Slash
commands require the user to explicitly type them; skills activate automatically when Claude
recognizes the situation.

Rule of thumb: if you find yourself explaining the same thing to Claude repeatedly, that's a
skill waiting to be written.
"""

QUIZ_QUESTIONS = [
    {
        "question": "What two fields must every SKILL.md frontmatter include?",
        "options": [
            "name and description",
            "name and allowed-tools",
            "description and model",
            "name and model",
        ],
        "answer_index": 0,
        "explanation": "name and description are what Claude reads to discover and match skills; allowed-tools and model are optional.",
    },
    {
        "question": "Where do project skills live?",
        "options": [
            ".claude/skills inside the repository",
            "~/.claude/skills in your home directory",
            "A cloud-hosted skill registry",
            "Inside the SKILL.md file itself",
        ],
        "answer_index": 0,
        "explanation": "Project skills live in .claude/skills at the repo root and are committed to version control, so the whole team shares them.",
    },
    {
        "question": "What's the key difference between a Skill and a CLAUDE.md file?",
        "options": [
            "Skills load on demand when they match a request; CLAUDE.md loads into every conversation",
            "Skills only work in personal directories; CLAUDE.md only works in projects",
            "CLAUDE.md is deprecated in favor of Skills",
            "There is no difference",
        ],
        "answer_index": 0,
        "explanation": "CLAUDE.md always loads into context; skills load only when their description matches the request, keeping context efficient.",
    },
    {
        "question": "What decides whether a skill activates for a given request?",
        "options": [
            "The description field, matched against the request",
            "The order skills were installed in",
            "The length of the SKILL.md file",
            "Whether the user types a slash command",
        ],
        "answer_index": 0,
        "explanation": "Claude compares the request against every available skill's description text to decide which one(s) match.",
    },
]

st.set_page_config(page_title="What are Skills?", page_icon="🧩", layout="wide")
st.title("What are Skills?")
st.caption("Introduction to Agent Skills — Section 1 of 6 · ~15 minutes")

with st.expander("What you'll learn", expanded=True):
    st.markdown(
        """
- Define what Claude Code skills are and how they work
- Explain where skills live (personal vs. project directories)
- Distinguish between skills, CLAUDE.md, and slash commands
- Identify scenarios where skills are the right customization tool
        """
    )

with st.expander("📖 What is a Skill — concept", expanded=True):
    st.markdown(
        """
Every time you explain your team's coding standards to Claude, you're repeating yourself.
Every PR review, you re-describe how you want feedback structured. Every commit message,
you remind Claude of your preferred format. **Skills fix this.**

A **Skill** is a folder of instructions and resources that Claude Code can discover and use
to handle a task more accurately. Each skill lives in a `SKILL.md` file with a `name` and
`description` in its frontmatter. The **description is how Claude decides whether to use
the skill** — when you make a request, Claude compares it against every available skill's
description and activates the ones that match.

**Where skills live:**

| Scope | Location | Shared with |
|---|---|---|
| Personal | `~/.claude/skills` (Windows: `C:/Users/<you>/.claude/skills`) | Just you, across every project |
| Project | `.claude/skills` at the repo root | Anyone who clones the repo — committed to version control |

Project skills are where team standards live: brand guidelines, preferred fonts and colors,
code review checklists — anything the whole team should share automatically.

**The rule of thumb:** if you find yourself explaining the same thing to Claude repeatedly,
that's a skill waiting to be written.
        """
    )

with st.expander("📐 Core Code Pattern — SKILL.md frontmatter"):
    st.code(
        """---
name: pr-review
description: Reviews pull requests for code quality. Use when reviewing PRs or checking code changes.
---

# Below the frontmatter: the actual instructions
# your review checklist, formatting preferences, whatever
# Claude needs to know to do this task well.
""",
        language="yaml",
    )
    st.markdown(
        """
**Key insight:** Claude only loads the `name` and `description` up front — the body below
the frontmatter (the real instructions) only loads into context once the skill actually
matches a request. That's what keeps skills context-efficient: your PR review checklist
isn't sitting in context while you're debugging an unrelated issue.
        """
    )

st.markdown("### Skills vs. CLAUDE.md vs. Slash Commands")
st.markdown(
    """
| # | CLAUDE.md | Skills | Slash Commands |
|---|---|---|---|
| 1 | Loads into every conversation | Loads on demand, only when the description matches | Requires the user to explicitly type it |
| 2 | Best for rules that always apply (e.g. "always use TypeScript strict mode") | Best for task-specific knowledge (PR review, commit format, brand guidelines) | Best for actions you want to trigger deliberately |
| 3 | Always consumes context | Only consumes context when activated — keeps the window efficient | — |
| 4 | — | Activates automatically when Claude recognizes the situation | Never activates automatically |
"""
)

st.markdown("---")
st.markdown("### Try it yourself — skill matching, live")
st.markdown(
    "This is the same decision Claude Code makes internally: compare your request against "
    "each skill's `description` text and decide which one (if any) matches. The mini skill "
    "registry below is fixed — only your request changes."
)

SKILL_REGISTRY = """\
1. name: pr-review
   description: Reviews pull requests for code quality. Use when reviewing PRs or checking code changes.
2. name: commit-message
   description: Writes commit messages following Conventional Commits format. Use when creating a git commit.
3. name: brand-guidelines
   description: Applies company brand voice, fonts, and colors. Use when writing marketing copy or designing web pages.
4. name: debug-checklist
   description: Walks through a systematic debugging checklist for Python errors. Use when diagnosing a bug or exception.
"""

st.code(SKILL_REGISTRY, language="yaml")

request = st.text_input(
    "Your request to Claude Code",
    placeholder="e.g. Can you help me write a commit message for this fix?",
)

if st.button("Ask Claude which skill would match", type="primary"):
    if not request.strip():
        st.warning("Type a request first.")
    else:
        system_prompt = (
            "You are simulating the skill-matching step Claude Code performs before "
            "responding to a request. You are given a numbered list of available skills, "
            "each with a name and a description from its SKILL.md frontmatter. Decide which "
            "skill, if any, matches the user's request — based only on the description text, "
            "the same way Claude Code compares a request against skill descriptions. Reply "
            "with the matched skill name (or 'no match'), then one sentence naming the exact "
            "phrase in the description that triggered the match."
        )
        user_message = f"Available skills:\n{SKILL_REGISTRY}\nUser request: \"{request}\""
        try:
            with st.spinner("Matching against skill descriptions..."):
                answer = ask_claude(system_prompt, user_message)
            st.success(answer)
            render_trace(system_prompt, user_message, answer)
        except Exception as e:
            st.error(f"Couldn't reach the Gemini API — check GEMINI_API_KEY in .env. ({e})")

st.markdown("---")
render_quiz(QUIZ_QUESTIONS, key="quiz_01")

st.markdown("---")
render_lesson_chat(LESSON_CONTEXT, key="s01")

st.markdown("---")
with st.expander("Lesson reflection"):
    st.markdown(
        """
- Think about your most recent interactions with Claude Code. Which instructions did you
  find yourself repeating? How might a skill have saved you time?
- Consider your team's workflow. Which standards or processes would benefit most from being
  encoded as skills?
        """
    )
    st.text_area("Your notes (not saved — just for thinking out loud)", key="reflection_notes")

st.markdown("### What's next")
st.markdown(
    "**Section 2 — Creating your first skill:** create a skill from scratch and see how "
    "Claude Code discovers, matches, and loads skills behind the scenes."
)
