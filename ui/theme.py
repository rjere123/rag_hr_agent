"""
Theming layer for the HR Assistant.

Streamlit has no documented runtime API to switch its native theme while the
app is running. We therefore keep a polished Light theme in
``.streamlit/config.toml`` as the base, and apply the selected palette at
runtime by injecting CSS custom properties (``--ac-*``) plus the structural
stylesheet in ``styles.css``. This is a CSS-only approach using the documented
``st.markdown(..., unsafe_allow_html=True)`` API — no undocumented internals.
"""

from pathlib import Path
import streamlit as st

_CSS_PATH = Path(__file__).parent / "styles.css"

# Brand colour from the HR policy PDF (Atlas Copco navy).
BRAND = "#1B3A6B"
BRAND_2 = "#2E5DA8"

# Two palettes mapped to the CSS custom properties used in styles.css.
PALETTES = {
    "Light": {
        "--ac-brand": BRAND,
        "--ac-brand-2": BRAND_2,
        "--ac-bg": "#F7F9FC",
        "--ac-card": "#FFFFFF",
        "--ac-sidebar": "#FFFFFF",
        "--ac-text": "#1F2937",
        "--ac-muted": "#6B7280",
        "--ac-border": "#E3E8F0",
        "--ac-chip": "#EAF0FB",
    },
    "Dark": {
        "--ac-brand": "#7FA8E0",
        "--ac-brand-2": "#5B86C4",
        "--ac-bg": "#0E1B33",
        "--ac-card": "#16243F",
        "--ac-sidebar": "#0B1628",
        "--ac-text": "#E6ECF5",
        "--ac-muted": "#9AA8BF",
        "--ac-border": "#23344F",
        "--ac-chip": "#1C2D4A",
    },
}


@st.cache_data(show_spinner=False)
def _load_stylesheet() -> str:
    """Read the structural stylesheet once (cached across reruns)."""
    return _CSS_PATH.read_text(encoding="utf-8")


def apply_theme(theme_name: str) -> None:
    """
    Inject the colour variables for ``theme_name`` followed by the structural
    stylesheet. Call once per run, early in app.py.
    """
    palette = PALETTES.get(theme_name, PALETTES["Light"])
    variables = "\n".join(f"    {k}: {v};" for k, v in palette.items())
    css = _load_stylesheet()
    st.markdown(
        f"<style>\n:root {{\n{variables}\n}}\n{css}\n</style>",
        unsafe_allow_html=True,
    )
