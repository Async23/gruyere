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
