"""
Reusable, presentational UI components for the HR Assistant.

Each function renders a self-contained piece of UI using documented Streamlit
APIs (st.markdown, st.container, st.expander, st.metric, ...). Keeping these
here makes app.py read like a layout/orchestration file.
"""

import html
import streamlit as st


def render_header(status: str = "connected") -> None:
    """Branded header band with title, subtitle and a connection-status pill.

    status: one of "connected" | "warming" | "error".
    """
    status_map = {
        "connected": ("ac-status__dot--ok", "Connected"),
        "warming": ("ac-status__dot--warn", "Warming up"),
        "error": ("ac-status__dot--err", "Disconnected"),
    }
    dot_class, label = status_map.get(status, status_map["connected"])

    st.markdown(
        f"""
        <div class="ac-header">
            <div class="ac-header__brand">
                <div class="ac-header__logo">AC</div>
                <div>
                    <p class="ac-header__title">Atlas Copco Airpower &mdash; HR Assistant</p>
                    <p class="ac-header__subtitle">Ask anything about the company HR policy &middot; answers grounded in the official document</p>
                </div>
            </div>
            <div class="ac-status">
                <span class="ac-status__dot {dot_class}"></span>{label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    """Attractive empty state shown before the first question."""
    st.markdown(
        """
        <div class="ac-empty">
            <div class="ac-empty__icon">&#128172;</div>
            <p class="ac-empty__title">How can I help with HR policy today?</p>
            <p class="ac-empty__sub">Answers are generated only from the official HR policy document.</p>
            <p class="ac-empty__sub">Try one of the suggested questions below to get started.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_message(role: str, content: str) -> None:
    """Render a single chat message with Streamlit's native markdown.

    Using st.chat_message + st.markdown gives us tables, syntax-highlighted
    code blocks and expanders for free (all documented behaviour).
    """
    avatar = "\U0001F9D1" if role == "user" else "\U0001F4D8"  # 🧑 / 📘
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


def render_answer_actions(answer: str, index: int) -> None:
    """Copy (via code block) and Download controls for an assistant answer."""
    col_dl, col_copy = st.columns(2)
    with col_dl:
        st.download_button(
            "Download",
            data=answer,
            file_name=f"hr_answer_{index + 1}.md",
            mime="text/markdown",
            use_container_width=True,
            key=f"dl_{index}",
        )
    with col_copy:
        # st.code() exposes a native copy-to-clipboard icon. We surface the raw
        # answer text inside an expander so users can copy it verbatim.
        with st.expander("Copy text"):
            st.code(answer, language="markdown")


def render_sources_rail(sources: list[dict]) -> None:
    """Right-hand rail listing the retrieved source chunks (citations)."""
    st.markdown('<p class="ac-rail-title">Sources</p>', unsafe_allow_html=True)

    if not sources:
        st.caption("Sources from the HR policy document will appear here after you ask a question.")
        return

    for src in sources:
        distance = src.get("distance")
        score = f"distance {distance:.3f}" if isinstance(distance, (int, float)) else "retrieved"
        safe_id = html.escape(str(src.get("id", "chunk")))
        safe_text = html.escape(src.get("text", "").strip())
        st.markdown(
            f"""
            <div class="ac-source">
                <div class="ac-source__head">
                    <span class="ac-source__id">{safe_id}</span>
                    <span class="ac-source__score">{score}</span>
                </div>
                <div class="ac-source__text">{safe_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metrics(usage: dict | None, latency: float | None) -> None:
    """Compact telemetry row: input/output tokens and execution time.

    Rendered as static HTML (not st.metric) so the values appear instantly
    with no count-up animation.
    """
    st.markdown('<p class="ac-rail-title">Last response</p>', unsafe_allow_html=True)
    in_tok = usage.get("input_tokens") if usage else None
    out_tok = usage.get("output_tokens") if usage else None
    in_s = str(in_tok) if in_tok is not None else "&mdash;"
    out_s = str(out_tok) if out_tok is not None else "&mdash;"
    time_s = f"{latency:.2f}s" if latency is not None else "&mdash;"
    st.markdown(
        f"""
        <div class="ac-metrics">
            <div class="ac-metric">
                <div class="ac-metric__label">Input tok</div>
                <div class="ac-metric__value">{in_s}</div>
            </div>
            <div class="ac-metric">
                <div class="ac-metric__label">Output tok</div>
                <div class="ac-metric__value">{out_s}</div>
            </div>
            <div class="ac-metric">
                <div class="ac-metric__label">Time</div>
                <div class="ac-metric__value">{time_s}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
