# Gruyere Theme Support Design

## Goal

Add theme system with built-in presets and automatic dark/light terminal detection.

## Built-in Themes

| Theme | Mode | Gradient Colors | Selected Color |
|-------|------|----------------|----------------|
| `default` | dark | #EE6FF8 / #EDFF82 / #643AFF / #14F9D5 | #EE6FF8 |
| `one-half-dark` | dark | One Half Dark palette blues/cyans | #61AFEF |
| `tomorrow` | light | Tomorrow palette warm tones | #4271AE |
| `kanagawa` | dark | Kanagawa Wave palette | #7E9CD8 |
| `nord` | dark | Nord palette frost/aurora | #88C0D0 |

## Theme Resolution Priority

1. `--theme` CLI parameter (highest)
2. `GRUYERE_THEME` environment variable
3. Auto-detect: macOS `AppleInterfaceStyle` → dark=`one-half-dark`, light=`tomorrow`
4. Fallback: `one-half-dark`

## Code Changes

Single file: `gruyere/main.py`

- `Theme` dataclass: gradient 4 corners + selected_color
- `THEMES` dict with 5 presets
- `detect_theme()`: auto-detection logic
- `_colorGrid()`: read from active theme instead of hardcoded colors
- `SELECTED_COLOR`: read from active theme
- `main()`: add `--theme` typer.Option

## Build & Replace

```bash
cd ~/code/gruyere
uv sync
uv pip install -e .
# or: uv run gruyere
```
