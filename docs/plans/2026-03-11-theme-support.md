# Theme Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a theme system to Gruyere with 5 built-in presets and automatic dark/light terminal detection.

**Architecture:** Define a `Theme` dataclass holding gradient colors + accent color. Replace all hardcoded color references with theme lookups. Resolve theme via CLI flag > env var > auto-detect chain.

**Tech Stack:** Python 3.13, Rich (styles/colors), typer (CLI), psutil. Project uses pyright strict + ruff for linting.

---

### Task 1: Add Theme dataclass and theme definitions

**Files:**
- Create: `gruyere/themes.py`
- Test: `test_themes.py`

**Step 1: Write failing tests for theme resolution**

```python
# test_themes.py
import os
from unittest.mock import patch

from gruyere.themes import THEMES, Theme, detect_mode, resolve_theme


def test_theme_dataclass_fields():
    t = THEMES["default"]
    assert isinstance(t, Theme)
    assert t.selected_color == "#EE6FF8"
    assert t.title_fg == "white"


def test_all_themes_exist():
    assert set(THEMES.keys()) == {"default", "one-half-dark", "tomorrow", "kanagawa", "nord"}


def test_resolve_theme_cli_flag_highest_priority():
    assert resolve_theme("nord").selected_color == THEMES["nord"].selected_color


def test_resolve_theme_env_var():
    with patch.dict(os.environ, {"GRUYERE_THEME": "kanagawa"}):
        assert resolve_theme(None).selected_color == THEMES["kanagawa"].selected_color


def test_resolve_theme_invalid_name_falls_back():
    t = resolve_theme("nonexistent")
    # Should fall back to auto-detect default, not crash
    assert isinstance(t, Theme)


def test_detect_mode_dark_on_macos_dark():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Dark"
        assert detect_mode() == "dark"


def test_detect_mode_light_on_macos_light():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("not set")
        with patch.dict(os.environ, {}, clear=True):
            assert detect_mode() == "light"


def test_detect_mode_colorfgbg_dark():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("not set")
        with patch.dict(os.environ, {"COLORFGBG": "15;0"}):
            assert detect_mode() == "dark"


def test_detect_mode_colorfgbg_light():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("not set")
        with patch.dict(os.environ, {"COLORFGBG": "0;15"}):
            assert detect_mode() == "light"
```

**Step 2: Run tests to verify they fail**

Run: `cd ~/code/gruyere && uv run pytest test_themes.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'gruyere.themes'`

**Step 3: Implement themes module**

```python
# gruyere/themes.py
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
```

**Step 4: Run tests to verify they pass**

Run: `cd ~/code/gruyere && uv run pytest test_themes.py -v`
Expected: All PASS

**Step 5: Run linters**

Run: `cd ~/code/gruyere && uv run ruff check gruyere/themes.py && uv run pyright gruyere/themes.py`
Expected: Clean

**Step 6: Commit**

```bash
cd ~/code/gruyere
git add gruyere/themes.py test_themes.py
git commit -m "feat: add Theme dataclass, 5 presets, and auto-detect logic"
```

---

### Task 2: Wire theme into rendering functions in main.py

**Files:**
- Modify: `gruyere/main.py`

The global `SELECTED_COLOR` and hardcoded colors in `_colorGrid()` need to read from a `Theme` instance. Strategy: pass theme as a parameter to all rendering functions.

**Step 1: Replace SELECTED_COLOR and update _colorGrid**

In `gruyere/main.py`, make these changes:

1. Add import at top:
```python
from gruyere.themes import Theme, resolve_theme
```

2. Remove the hardcoded `SELECTED_COLOR` global (line 31). Replace with a helper:
```python
def _selected_style(theme: Theme) -> Style:
    return Style(color=theme.selected_color, bold=True)
```

3. Update `_colorGrid` to accept a theme parameter:
```python
def _colorGrid(x_steps: int, y_steps: int, theme: Theme) -> list[list[Style]]:
    x0y0, x1y0 = (
        Color.parse(theme.gradient_top_left).get_truecolor(),
        Color.parse(theme.gradient_top_right).get_truecolor(),
    )
    x0y1, x1y1 = (
        Color.parse(theme.gradient_bottom_left).get_truecolor(),
        Color.parse(theme.gradient_bottom_right).get_truecolor(),
    )
    # ... rest unchanged
```

4. Update `_render_title(theme: Theme)`:
   - Pass `theme` to `_colorGrid(1, 5, theme)`
   - Change `Style(color="white", ...)` → `Style(color=theme.title_fg, ...)`

5. Update `_render_processes_table(processes, selected, show_details, is_filtering, theme)`:
   - Replace all `SELECTED_COLOR` references with `_selected_style(theme)`

6. Update `create_filter_panel(filter_text, theme)`:
   - Replace `SELECTED_COLOR` with `_selected_style(theme)`

7. Update `_show_confirmation_view(console, process, title, theme)`:
   - Replace `SELECTED_COLOR` with `_selected_style(theme)`

**Step 2: Update main() to resolve theme and pass it through**

```python
@app.command()
def main(
    # ... existing params ...
    theme: Optional[str] = typer.Option(
        None, "--theme", "-t",
        help="Color theme (default, one-half-dark, tomorrow, kanagawa, nord)"
    ),
):
    active_theme = resolve_theme(theme)
    selected_style = _selected_style(active_theme)
    text = _render_title(active_theme)
    # ... pass active_theme to all rendering calls ...
```

All call sites for `_render_processes_table`, `create_filter_panel`, `_show_confirmation_view` in the `main()` function body need the extra `theme=active_theme` argument. There are ~12 call sites.

**Step 3: Run existing tests**

Run: `cd ~/code/gruyere && uv run pytest test_gruyere.py test_themes.py -v`
Expected: `test_create_filter_panel` will FAIL because it imports `SELECTED_COLOR` which no longer exists.

**Step 4: Fix test_gruyere.py**

Update the import and `test_create_filter_panel`:
```python
# Remove SELECTED_COLOR from import
from gruyere.main import (
    Process,
    _selected_style,
    apply_filter,
    create_filter_panel,
    extract_app_name,
    get_processes,
    parse_port,
)
from gruyere.themes import THEMES

# ...

def test_create_filter_panel():
    theme = THEMES["default"]
    panel = create_filter_panel("test", theme)
    assert isinstance(panel, Panel)
    assert panel.border_style == _selected_style(theme)
```

**Step 5: Run all tests**

Run: `cd ~/code/gruyere && uv run pytest test_gruyere.py test_themes.py -v`
Expected: All PASS

**Step 6: Run linters**

Run: `cd ~/code/gruyere && uv run ruff check gruyere/ && uv run pyright gruyere/`
Expected: Clean (fix any issues pyright reports)

**Step 7: Commit**

```bash
cd ~/code/gruyere
git add gruyere/main.py test_gruyere.py
git commit -m "feat: wire theme into all rendering functions and CLI"
```

---

### Task 3: Manual smoke test

**Step 1: Install in dev mode**

```bash
cd ~/code/gruyere && uv sync
```

**Step 2: Test each theme**

```bash
# Default auto-detect (should pick one-half-dark on dark terminal)
uv run gruyere

# Explicit themes
uv run gruyere --theme default
uv run gruyere --theme one-half-dark
uv run gruyere --theme tomorrow
uv run gruyere --theme kanagawa
uv run gruyere --theme nord

# Env var
GRUYERE_THEME=nord uv run gruyere
```

Verify: title gradient colors change, selected item highlight color changes, filter panel border color changes.

**Step 3: Test light mode detection**

```bash
# Temporarily switch macOS to light mode, run gruyere, should auto-pick "tomorrow"
uv run gruyere
```

---

### Task 4: Build and replace local binary

**Step 1: Remove old Go binary**

```bash
rm ~/go/bin/gruyere
```

**Step 2: Install via uv tool**

```bash
cd ~/code/gruyere && uv tool install --force --editable .
```

This installs `gruyere` to `~/.local/bin/gruyere` (uv tool default). Verify it's on PATH:

```bash
which gruyere
gruyere --help
```

If `~/.local/bin` isn't on PATH, add to `~/.zshrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Step 3: Verify installed binary**

```bash
gruyere --theme nord
```

**Step 4: Commit any remaining changes**

```bash
cd ~/code/gruyere
git add -A
git commit -m "docs: finalize theme support implementation"
```

---

### Summary of all files changed

| File | Action | Purpose |
|------|--------|---------|
| `gruyere/themes.py` | Create | Theme dataclass, 5 presets, detect_mode, resolve_theme |
| `gruyere/main.py` | Modify | Wire theme into all rendering functions, add --theme CLI param |
| `test_themes.py` | Create | Tests for theme resolution and detection |
| `test_gruyere.py` | Modify | Update test_create_filter_panel for new theme API |
