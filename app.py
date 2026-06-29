"""
Atlas Copco Airpower — HR Assistant
Streamlit frontend (Concept C: Branded Enterprise + Sources).

Run with:  streamlit run app.py

Design notes / honest limitations (frontend-only scope):
  * Model, temperature, top-p and max-tokens are fixed in the backend
    (rag.py / config.py) and are intentionally NOT exposed as controls here,
    so nothing on screen is decorative.
  * The backend call is blocking (no streaming), so a true mid-generation
    "Stop" button is not offered — Streamlit cannot cancel an in-flight
    request. Controls are disabled while a response is generating.
  * Token usage and execution time are REAL values returned by the Anthropic
    API, not estimates.
  * Light/Dark theming is applied via injected CSS variables (see ui/theme.py)
    because Streamlit has no documented runtime theme-switch API.
"""

import os
import time

import streamlit as st

from ui.theme import apply_theme
from ui import components as ui

# --------------------------------------------------------------------------
# Page configuration (must be the first Streamlit call).
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Atlas Copco Airpower — HR Assistant",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------
# Session state initialisation.
# --------------------------------------------------------------------------
def _init_state() -> None:
    defaults = {
        "theme": "Light",
        "messages": [],          # list of {"role", "content"} for chat history
        "sources": [],           # sources for the most recent answer
        "usage": None,           # token usage for the most recent answer
        "latency": None,         # execution time for the most recent answer
        "pending": None,         # a question queued for processing
        "generating": False,     # True while awaiting the model
        "last_question": None,    # supports "Regenerate"
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


_init_state()

# Bridge Streamlit Cloud secrets → os.environ so rag.py finds the key.
if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ.setdefault("ANTHROPIC_API_KEY", st.secrets["ANTHROPIC_API_KEY"])


# --------------------------------------------------------------------------
# Backend loader (cached so the heavy rag.py import / model load happens once).
# rag.py reads ANTHROPIC_API_KEY from the environment at import time, so any
# user-supplied override key is placed in os.environ BEFORE this runs.
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_backend():
    import rag
    return rag


def _backend_ready() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


# --------------------------------------------------------------------------
# Sidebar — settings, theme, conversation controls, about.
# --------------------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        # --- API key (password; never displayed or logged) ---------------
        st.caption("API key is read from your .env file. You may override it for this session only.")
        override = st.text_input(
            "Anthropic API key",
            type="password",
            placeholder="sk-ant-… (optional override)",
            help="Stored only in this session's environment; never shown or saved to disk.",
        )
        if override:
            os.environ["ANTHROPIC_API_KEY"] = override

        # --- Fixed backend info (honest: these are not adjustable here) ---
        with st.expander("Model & retrieval (read-only)"):
            try:
                from config import CLAUDE_MODEL, EMBEDDING_MODEL, TOP_K
                st.write(f"**Model:** `{CLAUDE_MODEL}`")
                st.write(f"**Embeddings:** `{EMBEDDING_MODEL}`")
                st.write(f"**Top-K chunks:** `{TOP_K}`")
                st.write("**Max tokens:** `1024`")
            except Exception as exc:  # pragma: no cover - defensive
                st.warning(f"Could not read config: {exc}")
            st.caption(
                "These are fixed in config.py / rag.py. Temperature, Top-P and "
                "model selection are not exposed because the backend does not "
                "use them — no decorative controls."
            )

        st.divider()

        # --- Theme toggle -------------------------------------------------
        dark = st.toggle("🌙 Dark theme", value=(st.session_state.theme == "Dark"))
        new_theme = "Dark" if dark else "Light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()

        st.divider()

        # --- Conversation controls ---------------------------------------
        if st.button("🗑️ Clear conversation", use_container_width=True,
                     disabled=st.session_state.generating):
            st.session_state.messages = []
            st.session_state.sources = []
            st.session_state.usage = None
            st.session_state.latency = None
            st.session_state.last_question = None
            st.toast("Conversation cleared", icon="🧹")
            st.rerun()

        st.divider()

        # --- About --------------------------------------------------------
        with st.expander("ℹ️ About"):
            st.markdown(
                "**HR Assistant** answers employee questions using a "
                "retrieval-augmented pipeline over the official Atlas Copco "
                "Airpower HR policy document.\n\n"
                "Pipeline: **PDF → chunks → ChromaDB → retrieval → Claude**.\n\n"
                "Answers are grounded strictly in the policy; if information "
                "isn't present, the assistant says so rather than guessing."
            )


# --------------------------------------------------------------------------
# Prompt area — large text box + action buttons (inside a form).
# --------------------------------------------------------------------------
SUGGESTIONS = [
    "What is the leave policy for casual leaves per year?",
    "What is the notice period for employees?",
    "What is the max hotel allowance on domestic travel?",
    "How does the grievance redressal process work?",
]


def render_suggestions() -> None:
    """Clickable example questions for the empty state."""
    cols = st.columns(2)
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i % 2]:
            if st.button(suggestion, key=f"sugg_{i}", use_container_width=True,
                         disabled=st.session_state.generating):
                st.session_state.pending = suggestion
                st.rerun()


def render_prompt_box() -> None:
    """Large prompt box with Submit; Regenerate/Clear sit alongside."""
    with st.form("prompt_form", clear_on_submit=True):
        question = st.text_area(
            "Your question",
            placeholder="Ask about leave, travel, benefits, notice period, grievance process…",
            height=120,
            label_visibility="collapsed",
            disabled=st.session_state.generating,
        )
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            submitted = st.form_submit_button(
                "📨 Send", type="primary", use_container_width=True,
                disabled=st.session_state.generating,
            )
        with c2:
            regenerate = st.form_submit_button(
                "🔄 Regenerate", use_container_width=True,
                disabled=st.session_state.generating or not st.session_state.last_question,
            )
        with c3:
            cleared = st.form_submit_button(
                "✖ Clear", use_container_width=True,
                disabled=st.session_state.generating or not st.session_state.messages,
            )

    if submitted and question.strip():
        st.session_state.pending = question.strip()
        st.rerun()
    elif submitted and not question.strip():
        st.toast("Please type a question first.", icon="⚠️")

    if regenerate and st.session_state.last_question:
        st.session_state.pending = st.session_state.last_question
        st.rerun()

    if cleared:
        st.session_state.messages = []
        st.session_state.sources = []
        st.session_state.usage = None
        st.session_state.latency = None
        st.session_state.last_question = None
        st.rerun()


# --------------------------------------------------------------------------
# Generation — process a pending question with progress + telemetry.
# --------------------------------------------------------------------------
def process_pending() -> None:
    question = st.session_state.pending
    st.session_state.pending = None

    if not _backend_ready():
        st.error("No Anthropic API key found. Add ANTHROPIC_API_KEY to your "
                 ".env file or paste an override in the sidebar.")
        return

    # Record the user turn immediately so it shows during generation.
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.last_question = question
    st.session_state.generating = True

    try:
        rag = load_backend()

        # Step 1: Retrieval (fast — sub-second ChromaDB lookup).
        with st.spinner("Retrieving relevant policy sections…"):
            start = time.perf_counter()
            retrieval = rag.retrieve(question)

        st.session_state.sources = retrieval["sources"]

        # Step 2: Stream the LLM response so tokens appear immediately.
        with rag.stream_response(question, retrieval["context"]) as stream:
            with st.chat_message("assistant"):
                answer = st.write_stream(stream.text_stream)
            final_msg = stream.get_final_message()

        latency = time.perf_counter() - start
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.usage = {
            "input_tokens": final_msg.usage.input_tokens,
            "output_tokens": final_msg.usage.output_tokens,
        }
        st.session_state.latency = latency
        st.toast("Answer ready", icon="✅")

    except Exception as exc:
        # Surface a friendly message; never echo secrets.
        msg = str(exc)
        if "credit balance" in msg.lower():
            friendly = ("Your Anthropic account is out of credits. Add credits "
                        "in the Anthropic Console (Plans & Billing) and retry.")
        elif "authentication" in msg.lower() or "api key" in msg.lower():
            friendly = "Authentication failed. Check your Anthropic API key."
        else:
            friendly = f"Something went wrong while generating the answer: {msg}"
        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {friendly}"})
        st.toast("Generation failed", icon="❌")
    finally:
        st.session_state.generating = False
        st.rerun()


# --------------------------------------------------------------------------
# Main render.
# --------------------------------------------------------------------------
def main() -> None:
    apply_theme(st.session_state.theme)
    render_sidebar()

    status = "connected" if _backend_ready() else "error"
    ui.render_header(status)

    # Two-column layout: chat (main) + sources/telemetry rail (right).
    main_col, rail_col = st.columns([2.4, 1], gap="large")

    with main_col:
        if st.session_state.messages:
            for i, msg in enumerate(st.session_state.messages):
                ui.render_message(msg["role"], msg["content"])
                # Show actions under the latest assistant message only.
                is_last_assistant = (
                    msg["role"] == "assistant" and i == len(st.session_state.messages) - 1
                )
                if is_last_assistant and not msg["content"].startswith("⚠️"):
                    ui.render_answer_actions(msg["content"], i)
        else:
            ui.render_empty_state()
            st.write("")
            render_suggestions()

        st.write("")
        render_prompt_box()

        # Process pending inside the chat column so the stream renders here.
        if st.session_state.pending:
            process_pending()

    with rail_col:
        ui.render_metrics(st.session_state.usage, st.session_state.latency)
        st.write("")
        ui.render_sources_rail(st.session_state.sources)


if __name__ == "__main__":
    main()
