# Claude Partner Network — Learning Path

Hands-on, code-driven companion to Anthropic's [Claude Partner Network Learning Path](https://anthropic-partners.skilljar.com/page/claude-partner-network-learning-path) on Skilljar. Each module is a self-contained Streamlit app: read the concept, run the code, see the exact prompts/responses in an execution trace.

Course content (lesson text, screenshots, notes) is relayed by the learner from the real Skilljar course as they progress — this repo does not reproduce Skilljar's material independently.

## Modules

| # | Module | Skilljar link | Status |
|---|---|---|---|
| 01 | Introduction to Agent Skills | [link](https://anthropic-partners.skilljar.com/introduction-to-agent-skills) | 🧭 In progress — 1/6 sections built |
| 02 | Building with the Claude API | [link](https://anthropic-partners.skilljar.com/claude-with-the-anthropic-api) | 🔜 Scaffolded |
| 03 | Claude Code in Action | [link](https://anthropic-partners.skilljar.com/claude-code-in-action) | 🔜 Scaffolded |
| 04 | Introduction to Model Context Protocol | [link](https://anthropic-partners.skilljar.com/introduction-to-model-context-protocol) | 🔜 Scaffolded |

## Running a module

```bash
cd 01-introduction-to-agent-skills
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env    # add your ANTHROPIC_API_KEY
streamlit run app.py
```

Each module folder is independent — its own `requirements.txt` and `.venv`.

See [CLAUDE.md](CLAUDE.md) for conventions, page structure standard, and commit checklist.
