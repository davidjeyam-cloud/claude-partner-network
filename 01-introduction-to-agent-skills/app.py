import streamlit as st

from utils.styles import apply_theme, phase_header

st.set_page_config(page_title="Introduction to Agent Skills", page_icon="🧩", layout="wide")
apply_theme()
phase_header("Introduction to Agent Skills", "Claude Partner Network Learning Path — Module 01")

st.markdown("---")

with st.expander("About this course", expanded=True):
    st.markdown(
        """
In this course, you'll learn how to stop repeating yourself and start teaching Claude once.
You'll discover what Skills are and how they differ from other Claude Code customization
options like CLAUDE.md, hooks, and subagents. You'll create your first Skill from scratch —
writing the SKILL.md frontmatter, crafting effective descriptions that reliably trigger
matching, and organizing your skill directory with progressive disclosure to keep context
windows efficient. You'll also explore advanced configuration options like restricting tool
access with `allowed-tools` and using scripts that execute without consuming context.

Beyond building individual Skills, you'll learn how to share them with your team by
committing them to a repository, distribute them more broadly through plugins, and deploy
them organization-wide using enterprise managed settings. You'll see how to wire Skills into
custom subagents for isolated, expert task delegation, and you'll walk through a complete
troubleshooting guide for diagnosing issues — from skills that won't trigger to priority
conflicts and runtime errors. By the end, you'll have the knowledge to build a full
Skills-based workflow that keeps Claude consistent, context-efficient, and aligned with your
team's standards.

*— course description, Anthropic Claude Partner Network / Skilljar*
        """
    )

st.markdown("### Sections")

sections = [
    (1, "What are Skills?", "01_What_Are_Skills"),
    (2, "Creating your first skill", "02_Creating_Your_First_Skill"),
    (3, "Configuration and multi-file skills", "03_Configuration_And_MultiFile_Skills"),
    (4, "Skills vs. other Claude Code features", "04_Skills_Vs_Other_Claude_Code_Features"),
    (5, "Sharing skills", "05_Sharing_Skills"),
    (6, "Troubleshooting skills", "06_Troubleshooting_Skills"),
]

rows = "\n".join(f"| {n} | {title} | 🔜 Awaiting lesson content |" for n, title, _ in sections)
st.markdown(
    f"""
| # | Section | Status |
|---|---|---|
{rows}
"""
)

st.info(
    "Each section above is a page in the sidebar. Paste in that section's real lesson "
    "content and it'll be built out into a full concept + code + demo page, one at a time."
)
