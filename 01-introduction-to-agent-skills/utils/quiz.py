import streamlit as st


def render_quiz(questions: list, key: str) -> None:
    st.markdown("#### Quick knowledge check")
    answers = {}
    for i, q in enumerate(questions):
        answers[i] = st.radio(
            f"{i + 1}. {q['question']}",
            q["options"],
            key=f"{key}_q{i}",
            index=None,
        )

    if st.button("Check my answers", key=f"{key}_submit"):
        score = 0
        for i, q in enumerate(questions):
            chosen = answers[i]
            correct = q["options"][q["answer_index"]]
            if chosen == correct:
                score += 1
                st.success(f"Q{i + 1}. Correct — {q['explanation']}")
            elif chosen is None:
                st.warning(f"Q{i + 1}. Not answered. Correct answer: **{correct}** — {q['explanation']}")
            else:
                st.error(f"Q{i + 1}. Not quite. Correct answer: **{correct}** — {q['explanation']}")
        st.markdown(f"**Score: {score}/{len(questions)}**")
