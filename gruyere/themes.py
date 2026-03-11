import os
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    gradient_top_left: str
    gradient_top_right: str
    gradient_bottom_left: str
    gradient_bottom_right: str
    selected_color: str
    title_fg: str  # "white" for dark themes, "black" for light


THEMES: dict[str, Theme] = {
    "default": Theme(
        gradient_top_left="#EE6FF8",
        gradient_top_right="#EDFF82",
        gradient_bottom_left="#643AFF",
        gradient_bottom_right="#14F9D5",
        selected_color="#EE6FF8",
        title_fg="white",
    ),
    "one-half-dark": Theme(
        gradient_top_left="#C678DD",
        gradient_top_right="#61AFEF",
        gradient_bottom_left="#E06C75",
        gradient_bottom_right="#56B6C2",
        selected_color="#61AFEF",
        title_fg="white",
    ),
    "tomorrow": Theme(
        gradient_top_left="#8959A8",
        gradient_top_right="#4271AE",
        gradient_bottom_left="#3E999F",
        gradient_bottom_right="#718C00",
        selected_color="#4271AE",
        title_fg="black",
    ),
    "kanagawa": Theme(
        gradient_top_left="#D27E99",
        gradient_top_right="#E6C384",
        gradient_bottom_left="#957FB8",
        gradient_bottom_right="#7E9CD8",
        selected_color="#7E9CD8",
        title_fg="white",
    ),
    "nord": Theme(
        gradient_top_left="#B48EAD",
        gradient_top_right="#88C0D0",
        gradient_bottom_left="#5E81AC",
        gradient_bottom_right="#A3BE8C",
        selected_color="#88C0D0",
        title_fg="white",
    ),
}


def detect_mode() -> str:
    """Detect terminal dark/light mode. Returns 'dark' or 'light'."""
    # 1. Check COLORFGBG (format: "fg;bg", bg < 8 = dark)
    colorfgbg = os.environ.get("COLORFGBG")
    if colorfgbg:
        parts = colorfgbg.split(";")
        if len(parts) >= 2:
            try:
                bg = int(parts[-1])
                return "dark" if bg < 8 else "light"
            except ValueError:
                pass

    # 2. macOS: check system appearance
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0 and "Dark" in result.stdout:
                return "dark"
            return "light"
        except Exception:
            return "light"

    # 3. Default to dark (most terminal users use dark themes)
    return "dark"


def resolve_theme(theme_name: str | None) -> Theme:
    """Resolve theme by: CLI flag > env var > auto-detect."""
    # 1. CLI flag
    if theme_name and theme_name in THEMES:
        return THEMES[theme_name]

    # 2. Env var
    env_theme = os.environ.get("GRUYERE_THEME")
    if env_theme and env_theme in THEMES:
        return THEMES[env_theme]

    # 3. Auto-detect
    mode = detect_mode()
    if mode == "light":
        return THEMES["tomorrow"]
    return THEMES["one-half-dark"]
