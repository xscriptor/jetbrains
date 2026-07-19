#!/usr/bin/env python3
"""
Xscriptor Theme Generator
=========================
Reads colors.md and produces all theme.json + editor XML files
for the Xscriptor JetBrains plugin (12 themes).

Usage:
    python3 scripts/generate_themes.py

Output (by default, no files outside scripts/output/ are touched):
    scripts/output/themes/*.theme.json    UI theme files
    scripts/output/colors/*.xml           Editor color scheme files
    scripts/output/plugin.xml             Generated plugin.xml reference

To apply to the real plugin source, copy scripts/output/* into
src/main/resources/ or use --apply flag.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths relative to this file
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
COLORS_JSON = PROJECT_DIR.parent / "colors.json"
COLORS_MD = PROJECT_DIR.parent / "colors.md"
RESOURCES_DIR = PROJECT_DIR / "src" / "main" / "resources"
TEMPLATES_DIR = RESOURCES_DIR / "templates"  # optional, created below

OUTPUT_DIR = SCRIPT_DIR / "output"

# ---------------------------------------------------------------------------
# Color math
# ---------------------------------------------------------------------------
def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def blend(c1: str, c2: str, ratio: float) -> str:
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex(
        int(r1 + (r2 - r1) * ratio),
        int(g1 + (g2 - g1) * ratio),
        int(b1 + (b2 - b1) * ratio),
    )


def darken(c: str, factor: float) -> str:
    return blend(c, "#000000", factor)


def lighten(c: str, factor: float) -> str:
    return blend(c, "#FFFFFF", factor)


def alpha(c: str, a: str) -> str:
    return c + a


# ---------------------------------------------------------------------------
# Parse colors.md
# ---------------------------------------------------------------------------
def load_palettes() -> dict:
    if COLORS_JSON.exists():
        return json.loads(COLORS_JSON.read_text())
    text = COLORS_MD.read_text()
    results = {}
    for name, raw in re.findall(
        r"<h2[^>]*>(.*?)</h2>\s*```json\s*(.*?)\s*```", text, re.DOTALL
    ):
        results[name.strip()] = json.loads(raw)
    return results


# ---------------------------------------------------------------------------
# Theme definitions
# ---------------------------------------------------------------------------
DARK_THEMES = ["X", "Lahabana", "Miami", "Paris", "Tokio", "Oslo",
               "Berlin", "Praha", "Bogota"]
LIGHT_THEMES = ["Madrid", "Helsinki", "London"]


def derive_dark_colors(pal: dict) -> dict:
    c = pal
    bg = c.get("background", c["color0"])
    fg = c.get("foreground", c["color7"])
    return {
        "primaryBackground": darken(bg, 0.78),
        "secondaryBackground": darken(bg, 0.70),
        "tertiaryBackground": darken(bg, 0.50),
        "primaryForeground": fg,
        "secondaryForeground": blend(fg, bg, 0.28),
        "tertiaryForeground": blend(fg, bg, 0.45),
        "accent": c["color1"],
        "accentSecondary": c["color6"],
        "success": c["color2"],
        "warning": c["color3"],
        "error": c["color1"],
        "info": c["color5"],
        "highlight": c["color3"],
        "border": c["color8"],
        "borderSecondary": lighten(c["color8"], 0.12),
        "selection": blend(fg, bg, 0.15) + "26",
        "hover": blend(c["color8"], bg, 0.10) + "26",
        "transparent": "#00000000",
        "iconGrey": blend(fg, bg, 0.45),
        "iconGreyInline": c["color8"],
        "iconGreyInlineDark": lighten(c["color8"], 0.12),
        "iconBlackText": darken(bg, 0.78),
        "iconFocusWide": c["color1"] + "26",
        "accentHover": darken(c["color1"], 0.10),
        "accentPressed": darken(c["color1"], 0.18),
    }


def derive_light_colors(pal: dict) -> dict:
    c = pal
    bg = c.get("background", c["color0"])
    fg = c.get("foreground", c["color7"])
    return {
        "primaryBackground": bg,
        "secondaryBackground": darken(bg, 0.03),
        "tertiaryBackground": darken(bg, 0.06),
        "primaryForeground": fg,
        "secondaryForeground": lighten(fg, 0.30),
        "tertiaryForeground": lighten(fg, 0.50),
        "accent": c["color1"],
        "accentSecondary": c["color4"],
        "success": c["color2"],
        "warning": c["color3"],
        "error": c["color1"],
        "info": c["color5"],
        "highlight": c["color3"],
        "border": darken(bg, 0.16),
        "borderSecondary": darken(bg, 0.38),
        "selection": lighten(fg, 0.65) + "1a",
        "hover": lighten(fg, 0.55) + "1a",
        "transparent": "#00000000",
        "accentHover": darken(c["color1"], 0.15),
        "accentPressed": darken(c["color1"], 0.28),
    }


# ---------------------------------------------------------------------------
# Dark XML substitutions
# ---------------------------------------------------------------------------
def dark_xml_subs(pal: dict) -> dict:
    c = pal
    c0 = c.get("background", c["color0"])
    c7 = c.get("foreground", c["color7"])
    c8 = c["color8"]
    bg = darken(c0, 0.72)
    bg_d = darken(c0, 0.80)
    bg_i = darken(c0, 0.62)
    cr = c0
    sb = lighten(c0, 0.10)
    sb2 = lighten(c0, 0.07)
    v1 = lighten(c0, 0.12)
    v4 = darken(c0, 0.06)
    ln = lighten(c0, 0.22)
    sw = lighten(c0, 0.32)
    fg = c7
    fd = blend(c7, c0, 0.28)
    fdm = blend(c7, c0, 0.42)
    return {
        "0f0f0f": bg, "#0f0f0f": bg,
        "19181a": bg_d,
        "221f22": bg_i,
        "373438": cr,
        "403e41": sb,
        "3c3a3d": sb2,
        "413f42": v1,
        "322f33": v4,
        "5b595c": ln,
        "727072": sw,
        "fcfcfa": fg,
        "c1c0c0": fd,
        "939293": fdm,
        "fc618d": c["color1"],
        "ff6188": c["color1"],
        "a9dc76": c["color2"],
        "ffd866": c["color3"],
        "fd9353": c["color4"],
        "fc9867": c["color4"],
        "ab9df2": c["color5"],
        "78dce8": c["color6"],
        "#0f0f0f00": alpha(bg, "00"),
        "#19181a59": alpha(bg_d, "59"),
        "#fcfcfa0c": alpha(fg, "0c"),
        "#fc618d26": alpha(c["color1"], "26"),
        "4c323b": blend(c["color1"], bg, 0.72),
        "4c3a36": blend(c["color4"], bg, 0.72),
        "4c4436": blend(c["color3"], bg, 0.72),
        "3f4539": blend(c["color2"], bg, 0.70),
        "38454a": blend(c["color6"], bg, 0.70),
        "403b4b": blend(c["color5"], bg, 0.72),
    }


# ---------------------------------------------------------------------------
# Light XML substitutions
# ---------------------------------------------------------------------------
def light_xml_subs(pal: dict) -> dict:
    c = pal
    c0 = c.get("background", c["color0"])
    c7 = c.get("foreground", c["color7"])
    bg = c0
    sbg = darken(c0, 0.03)
    sel = darken(c0, 0.10)
    fg = c7
    fd = lighten(c7, 0.30)
    fdm = lighten(c7, 0.45)
    ln = lighten(c7, 0.40)
    return {
        "ffffff": bg,
        "f5f5f5": sbg,
        "fafafa": darken(c0, 0.04),
        "fcfcfc": darken(c0, 0.01),
        "eeeeee": darken(c0, 0.07),
        "e0e0e0": sel,
        "bdbdbd": darken(c0, 0.25),
        "212121": fg,
        "424242": lighten(c7, 0.40),
        "616161": fd,
        "757575": fdm,
        "9e9e9e": ln,
        "d32f2f": c["color1"],
        "2e7d32": c["color2"],
        "f57f17": c["color3"],
        "e65100": c["color4"],
        "7b1fa2": c["color5"],
        "0277bd": c["color6"],
        "fff3e0": blend(c["color3"], bg, 0.90),
        "e8f5e8": blend(c["color2"], bg, 0.92),
        "ffebee": blend(c["color1"], bg, 0.93),
        "fff9c4": blend(c["color3"], bg, 0.88),
        "ffecb3": blend(c["color3"], bg, 0.88),
        "e3f2fd": blend(c["color6"], bg, 0.93),
        "#ffffff00": alpha(bg, "00"),
        "#f5f5f559": alpha(sbg, "59"),
        "f5f5f559": alpha(sbg, "59"),
    }


# ---------------------------------------------------------------------------
# Theme JSON generators
# ---------------------------------------------------------------------------
def make_dark_json(name: str, cs_file: str, cols: dict, indent: int | None = 2) -> str:
    colors_json = {
        k: cols[k]
        for k in [
            "primaryBackground", "secondaryBackground", "tertiaryBackground",
            "primaryForeground", "secondaryForeground", "tertiaryForeground",
            "accent", "accentSecondary", "success", "warning",
            "error", "info", "highlight",
            "border", "borderSecondary", "selection", "hover", "transparent",
        ]
    }
    raw = json.dumps(
        {
            "name": f"{name} Theme",
            "dark": True,
            "author": "Xscriptor",
            "editorScheme": f"/colors/{cs_file}.xml",
            "parentTheme": "Islands Dark",
            "colors": colors_json,
            "ui": DARK_UI,
            "icons": {
                "ColorPalette": {
                    "Actions.Grey": cols["iconGrey"],
                    "Actions.Red": cols["accent"],
                    "Actions.Yellow": cols["highlight"],
                    "Actions.Green": cols["success"],
                    "Actions.Blue": cols["accentSecondary"],
                    "Actions.GreyInline": cols["iconGreyInline"],
                    "Actions.GreyInline.Dark": cols["iconGreyInlineDark"],
                    "Objects.Grey": cols["iconGrey"],
                    "Objects.RedStatus": cols["accent"],
                    "Objects.Red": cols["accent"],
                    "Objects.Pink": cols["accent"],
                    "Objects.Yellow": cols["highlight"],
                    "Objects.Green": cols["success"],
                    "Objects.Blue": cols["accentSecondary"],
                    "Objects.Purple": cols["info"],
                    "Objects.BlackText": cols["iconBlackText"],
                    "Checkbox.Background.Default": cols["primaryBackground"],
                    "Checkbox.Background.Disabled": cols["tertiaryBackground"],
                    "Checkbox.Border.Default": cols["border"],
                    "Checkbox.Border.Disabled": cols["borderSecondary"],
                    "Checkbox.Focus.Thin.Default": cols["accent"],
                    "Checkbox.Focus.Wide": cols["iconFocusWide"],
                    "Checkbox.Foreground.Disabled": cols["iconGrey"],
                    "Checkbox.Background.Selected": cols["accent"],
                    "Checkbox.Border.Selected": cols["accent"],
                    "Checkbox.Foreground.Selected": cols["primaryForeground"],
                }
            },
        },
        indent=indent,
    )
    raw = raw.replace("PLACEHOLDER_accentHover", cols["accentHover"])
    raw = raw.replace("PLACEHOLDER_accentPressed", cols["accentPressed"])
    return raw


def make_light_json(name: str, cs_file: str, cols: dict, indent: int | None = 2) -> str:
    colors_json = {
        k: cols[k]
        for k in [
            "primaryBackground", "secondaryBackground", "tertiaryBackground",
            "primaryForeground", "secondaryForeground", "tertiaryForeground",
            "accent", "accentSecondary", "success", "warning",
            "error", "info", "highlight",
            "border", "borderSecondary", "selection", "hover", "transparent",
        ]
    }
    return json.dumps(
        {
            "name": f"{name} Theme",
            "dark": False,
            "author": "Xscriptor",
            "editorScheme": f"/colors/{cs_file}.xml",
            "parentTheme": "Islands Light",
            "colors": colors_json,
            "ui": LIGHT_UI,
        },
        indent=indent,
    )



# ---- Static UI blocks (generated once, reused for all themes) ----
def _build_dark_ui_template(cols: dict) -> dict:
    return {
        "*": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
            "infoForeground": "tertiaryForeground",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
            "selectionInactiveBackground": "hover",
            "borderColor": "border",
            "separatorColor": "border",
            "focusColor": "accent",
            "focusedBorderColor": "accent",
        },
        "Islands": 1,
        "Island.borderColor": "primaryBackground",
        "MainWindow.background": "secondaryBackground",
        "StatusBar.borderColor": "transparent",
        "ToolWindow.Stripe.borderColor": "transparent",
        "MainToolbar.borderColor": "transparent",
        "ToolWindow.background": "primaryBackground",
        "ToolWindow.Header.background": "primaryBackground",
        "ToolWindow.Header.inactiveBackground": "primaryBackground",
        "EditorTabs.background": "primaryBackground",
        "EditorTabs.underlinedBorderColor": "accent",
        "EditorTabs.inactiveUnderlinedTabBorderColor": "borderSecondary",
        "EditorTabs.underlinedTabBackground": "selection",
        "EditorTabs.inactiveUnderlinedTabBackground": "hover",
        "ActionButton": {
            "hoverBackground": "hover",
            "hoverBorderColor": "borderSecondary",
            "pressedBackground": "selection",
            "pressedBorderColor": "accent",
        },
        "Button": {
            "background": "tertiaryBackground",
            "foreground": "primaryForeground",
            "borderColor": "border",
            "focusedBorderColor": "accent",
            "hoverBorderColor": "borderSecondary",
            "pressedBackground": "selection",
            "disabledBackground": "secondaryBackground",
            "disabledBorderColor": "border",
            "disabledText": "tertiaryForeground",
            "default": {
                "background": "accent",
                "foreground": "primaryBackground",
                "borderColor": "accent",
                "focusedBorderColor": "accent",
                "hoverBackground": cols["accentHover"],
                "pressedBackground": cols["accentPressed"],
            },
        },
        "CheckBox": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
            "borderColor1": "border",
            "borderColor2": "borderSecondary",
            "focusedBorderColor": "accent",
            "disabledBorderColor": "border",
            "disabledText": "tertiaryForeground",
        },
        "ComboBox": {
            "background": "tertiaryBackground",
            "foreground": "primaryForeground",
            "ArrowButton": {
                "background": "tertiaryBackground",
                "iconColor": "secondaryForeground",
                "disabledIconColor": "tertiaryForeground",
            },
            "borderColor": "border",
            "focusedBorderColor": "accent",
            "hoverBorderColor": "borderSecondary",
        },
        "Component": {
            "borderColor": "border",
            "focusedBorderColor": "accent",
            "hoverIconColor": "accent",
            "pressedIconColor": "accent",
            "disabledIconColor": "tertiaryForeground",
            "infoForeground": "tertiaryForeground",
            "errorFocusColor": "error",
            "inactiveErrorFocusColor": "error",
            "warningFocusColor": "warning",
            "inactiveWarningFocusColor": "warning",
        },
        "EditorPane": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
            "caretForeground": "primaryForeground",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
            "inactiveBackground": "secondaryBackground",
            "inactiveForeground": "secondaryForeground",
        },
        "Label": {
            "foreground": "primaryForeground",
            "disabledForeground": "tertiaryForeground",
            "infoForeground": "tertiaryForeground",
            "errorForeground": "error",
            "successForeground": "success",
        },
        "Link": {
            "activeForeground": "accentSecondary",
            "hoverForeground": "accent",
            "pressedForeground": "accent",
            "visitedForeground": "info",
        },
        "List": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
            "selectionInactiveBackground": "hover",
            "selectionInactiveForeground": "primaryForeground",
            "hoverBackground": "hover",
            "dropLineColor": "accent",
        },
        "Menu": {
            "background": "tertiaryBackground",
            "foreground": "primaryForeground",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
            "disabledForeground": "tertiaryForeground",
            "acceleratorForeground": "secondaryForeground",
            "acceleratorSelectionForeground": "primaryForeground",
        },
        "MenuBar": {
            "background": "secondaryBackground",
            "foreground": "primaryForeground",
            "borderColor": "border",
            "highlight": "selection",
            "disabledBackground": "secondaryBackground",
            "disabledForeground": "tertiaryForeground",
        },
        "MenuItem": {
            "background": "tertiaryBackground",
            "foreground": "primaryForeground",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
            "disabledBackground": "tertiaryBackground",
            "disabledForeground": "tertiaryForeground",
            "acceleratorForeground": "secondaryForeground",
            "acceleratorSelectionForeground": "primaryForeground",
        },
        "Panel": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
        },
        "PopupMenu": {
            "background": "tertiaryBackground",
            "foreground": "primaryForeground",
            "borderColor": "border",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
        },
        "ProgressBar": {
            "background": "secondaryBackground",
            "foreground": "accent",
            "progressColor": "accent",
            "indeterminateStartColor": "accent",
            "indeterminateEndColor": "accentSecondary",
            "failedColor": "error",
            "failedEndColor": "error",
            "passedColor": "success",
            "passedEndColor": "success",
        },
        "ScrollBar": {
            "background": "primaryBackground",
            "Thumb": {
                "background": "border",
                "hoverBackground": "borderSecondary",
                "pressedBackground": "tertiaryForeground",
            },
            "track": "primaryBackground",
            "trackHighlight": "hover",
        },
        "Separator": {
            "separatorColor": "border",
            "foreground": "border",
        },
        "TabbedPane": {
            "background": "secondaryBackground",
            "foreground": "primaryForeground",
            "underlineColor": "accent",
            "disabledUnderlineColor": "border",
            "selectedBackground": "primaryBackground",
            "selectedForeground": "primaryForeground",
            "hoverColor": "hover",
            "focusColor": "accent",
            "contentAreaColor": "primaryBackground",
        },
        "Table": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
            "selectionInactiveBackground": "hover",
            "selectionInactiveForeground": "primaryForeground",
            "gridColor": "border",
            "sortIconColor": "secondaryForeground",
            "stripeColor": "hover",
            "dropLineColor": "accent",
            "dropLineShortColor": "accent",
        },
        "TableHeader": {
            "background": "secondaryBackground",
            "foreground": "primaryForeground",
            "cellBorder": "border",
            "separatorColor": "border",
            "bottomSeparatorColor": "border",
        },
        "TextArea": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
            "caretForeground": "primaryForeground",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
            "inactiveForeground": "secondaryForeground",
        },
        "TextField": {
            "background": "tertiaryBackground",
            "foreground": "primaryForeground",
            "caretForeground": "primaryForeground",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
            "inactiveForeground": "secondaryForeground",
            "borderColor": "border",
            "focusedBorderColor": "accent",
            "hoverBorderColor": "borderSecondary",
            "errorBorderColor": "error",
            "warningBorderColor": "warning",
        },
        "ToggleButton": {
            "background": "tertiaryBackground",
            "foreground": "primaryForeground",
            "borderColor": "border",
            "focusedBorderColor": "accent",
            "hoverBorderColor": "borderSecondary",
            "pressedBackground": "selection",
            "selectedBackground": "accent",
            "selectedForeground": "primaryBackground",
            "disabledBackground": "secondaryBackground",
            "disabledBorderColor": "border",
            "disabledText": "tertiaryForeground",
        },
        "ToolBar": {
            "background": "secondaryBackground",
            "foreground": "primaryForeground",
            "borderColor": "border",
            "floatingForeground": "primaryForeground",
            "hoverBackground": "hover",
            "pressedBackground": "selection",
        },
        "ToolTip": {
            "background": "tertiaryBackground",
            "foreground": "primaryForeground",
            "borderColor": "border",
            "infoForeground": "secondaryForeground",
            "shortcutForeground": "accent",
        },
        "Tree": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
            "selectionBackground": "selection",
            "selectionForeground": "primaryForeground",
            "selectionInactiveBackground": "hover",
            "selectionInactiveForeground": "primaryForeground",
            "selectionBorderColor": "accent",
            "dropLineColor": "accent",
            "hash": "border",
            "rowHeight": 24,
        },
        "Viewport": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
        },
        "Window": {
            "background": "primaryBackground",
            "foreground": "primaryForeground",
        },
    }


# Pre-build the UI blocks once with placeholders
# (PLACEHOLDER_accentHover/Pressed are replaced per-theme at generation time)
_placeholder = {
    "accentHover": "PLACEHOLDER_accentHover",
    "accentPressed": "PLACEHOLDER_accentPressed",
}
DARK_UI = _build_dark_ui_template(_placeholder)

LIGHT_UI = {
    "*": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
        "infoForeground": "tertiaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "selectionInactiveBackground": "hover",
        "borderColor": "border",
        "separatorColor": "border",
        "focusColor": "accent",
        "focusedBorderColor": "accent",
    },
    "Islands": 1,
    "Island.borderColor": "primaryBackground",
    "MainWindow.background": "secondaryBackground",
    "StatusBar.borderColor": "transparent",
    "ToolWindow.Stripe.borderColor": "transparent",
    "MainToolbar.borderColor": "transparent",
    "ToolWindow.background": "primaryBackground",
    "ToolWindow.Header.background": "primaryBackground",
    "ToolWindow.Header.inactiveBackground": "primaryBackground",
    "EditorTabs.background": "primaryBackground",
    "EditorTabs.underlinedBorderColor": "accent",
    "EditorTabs.inactiveUnderlinedTabBorderColor": "borderSecondary",
    "EditorTabs.underlinedTabBackground": "selection",
    "EditorTabs.inactiveUnderlinedTabBackground": "hover",
    "ActionButton": {
        "hoverBackground": "hover",
        "hoverBorderColor": "borderSecondary",
        "pressedBackground": "selection",
        "pressedBorderColor": "accent",
    },
    "Button": {
        "background": "tertiaryBackground",
        "foreground": "primaryForeground",
        "borderColor": "border",
        "focusedBorderColor": "accent",
        "hoverBorderColor": "borderSecondary",
        "pressedBackground": "selection",
        "disabledBackground": "secondaryBackground",
        "disabledBorderColor": "border",
        "disabledText": "tertiaryForeground",
        "default": {
            "background": "accent",
            "foreground": "primaryBackground",
            "borderColor": "accent",
            "focusedBorderColor": "accent",
            "hoverBackground": "PLACEHOLDER_accentHover",
            "pressedBackground": "PLACEHOLDER_accentPressed",
        },
    },
    "CheckBox": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
        "borderColor1": "border",
        "borderColor2": "borderSecondary",
        "focusedBorderColor": "accent",
        "disabledBorderColor": "border",
        "disabledText": "tertiaryForeground",
    },
    "ComboBox": {
        "background": "tertiaryBackground",
        "foreground": "primaryForeground",
        "ArrowButton": {
            "background": "tertiaryBackground",
            "iconColor": "secondaryForeground",
            "disabledIconColor": "tertiaryForeground",
        },
        "borderColor": "border",
        "focusedBorderColor": "accent",
        "hoverBorderColor": "borderSecondary",
    },
    "Component": {
        "borderColor": "border",
        "focusedBorderColor": "accent",
        "hoverIconColor": "accent",
        "pressedIconColor": "accent",
        "disabledIconColor": "tertiaryForeground",
        "infoForeground": "tertiaryForeground",
        "errorFocusColor": "error",
        "inactiveErrorFocusColor": "error",
        "warningFocusColor": "warning",
        "inactiveWarningFocusColor": "warning",
    },
    "EditorPane": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
        "caretForeground": "primaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "inactiveBackground": "secondaryBackground",
    },
    "Label": {
        "foreground": "primaryForeground",
        "disabledForeground": "tertiaryForeground",
        "infoForeground": "tertiaryForeground",
    },
    "Link": {
        "activeForeground": "accent",
        "hoverForeground": "accent",
        "pressedForeground": "accent",
        "visitedForeground": "info",
    },
    "List": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "selectionInactiveBackground": "hover",
        "hoverBackground": "hover",
    },
    "Menu": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "separatorColor": "border",
        "borderColor": "border",
    },
    "MenuBar": {
        "background": "secondaryBackground",
        "foreground": "primaryForeground",
        "borderColor": "border",
    },
    "MenuItem": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "disabledBackground": "primaryBackground",
        "disabledForeground": "tertiaryForeground",
    },
    "Panel": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
    },
    "PasswordField": {
        "background": "tertiaryBackground",
        "foreground": "primaryForeground",
        "caretForeground": "primaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "inactiveForeground": "tertiaryForeground",
        "borderColor": "border",
        "focusedBorderColor": "accent",
    },
    "PopupMenu": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
        "borderColor": "border",
    },
    "ProgressBar": {
        "background": "tertiaryBackground",
        "foreground": "accent",
        "indeterminateStartColor": "accent",
        "indeterminateEndColor": "accentSecondary",
        "failedColor": "error",
        "failedEndColor": "error",
        "passedColor": "success",
        "passedEndColor": "success",
    },
    "ScrollBar": {
        "background": "secondaryBackground",
        "Thumb": {
            "background": "borderSecondary",
            "hoverBackground": "tertiaryForeground",
            "pressedBackground": "secondaryForeground",
        },
        "track": "secondaryBackground",
    },
    "Separator": {
        "separatorColor": "border",
    },
    "TabbedPane": {
        "background": "secondaryBackground",
        "foreground": "primaryForeground",
        "hoverColor": "hover",
        "focusColor": "accent",
        "selectedBackground": "primaryBackground",
        "selectedForeground": "primaryForeground",
        "underlineColor": "accent",
        "inactiveUnderlineColor": "border",
        "contentAreaColor": "border",
    },
    "Table": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "selectionInactiveBackground": "hover",
        "gridColor": "border",
        "sortIconColor": "secondaryForeground",
        "stripeColor": "secondaryBackground",
    },
    "TableHeader": {
        "background": "secondaryBackground",
        "foreground": "primaryForeground",
        "separatorColor": "border",
        "bottomSeparatorColor": "border",
    },
    "TextArea": {
        "background": "tertiaryBackground",
        "foreground": "primaryForeground",
        "caretForeground": "primaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "inactiveForeground": "tertiaryForeground",
        "borderColor": "border",
        "focusedBorderColor": "accent",
    },
    "TextField": {
        "background": "tertiaryBackground",
        "foreground": "primaryForeground",
        "caretForeground": "primaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "inactiveForeground": "tertiaryForeground",
        "borderColor": "border",
        "focusedBorderColor": "accent",
        "hoverBorderColor": "borderSecondary",
    },
    "TitledBorder": {
        "titleColor": "primaryForeground",
    },
    "ToggleButton": {
        "background": "tertiaryBackground",
        "foreground": "primaryForeground",
        "borderColor": "border",
        "focusedBorderColor": "accent",
        "hoverBorderColor": "borderSecondary",
        "pressedBackground": "selection",
        "selectedBackground": "accent",
        "selectedForeground": "primaryBackground",
    },
    "ToolBar": {
        "background": "secondaryBackground",
        "foreground": "primaryForeground",
        "borderColor": "border",
        "floatingForeground": "primaryForeground",
        "floatingBackground": "primaryBackground",
    },
    "ToolTip": {
        "background": "tertiaryBackground",
        "foreground": "primaryForeground",
        "borderColor": "border",
        "infoForeground": "tertiaryForeground",
        "shortcutForeground": "secondaryForeground",
    },
    "Tree": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
        "selectionBackground": "selection",
        "selectionForeground": "primaryForeground",
        "selectionInactiveBackground": "hover",
        "hoverBackground": "hover",
        "rowHeight": 24,
        "paintLines": True,
        "lineColor": "border",
        "hash": "border",
    },
    "Viewport": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
    },
    "Window": {
        "background": "primaryBackground",
        "foreground": "primaryForeground",
    },
}


# ---------------------------------------------------------------------------
# XML generation helpers
# ---------------------------------------------------------------------------
def apply_xml_subs(template: str, name: str, parent: str, subs: dict) -> str:
    content = template
    content = re.sub(r'name="[^"]*"', f'name="{name} Theme"', content, count=1)
    content = re.sub(r'parent_scheme="[^"]*"', f'parent_scheme="{parent}"', content)
    content = re.sub(
        r"<property name=\"originalScheme\">.*?</property>",
        f"<property name=\"originalScheme\">{name} Theme</property>",
        content,
    )
    for old, new in sorted(subs.items(), key=lambda x: -len(x[0])):
        content = re.sub(
            r"(?<![a-fA-F0-9#])" + re.escape(old) + r"(?![a-fA-F0-9])",
            new,
            content,
            flags=re.IGNORECASE,
        )
    return content


def postprocess_light_json(text: str, cols: dict) -> str:
    """Replace placeholder accentHover/accentPressed in light UI."""
    text = text.replace("PLACEHOLDER_accentHover", cols["accentHover"])
    text = text.replace("PLACEHOLDER_accentPressed", cols["accentPressed"])
    return text


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------
def generate(output_root: Path, dark_template_xml: str, light_template_xml: str,
             indent: int | None = 2):
    palettes = load_palettes()

    themes_out = output_root / "themes"
    colors_out = output_root / "colors"
    themes_out.mkdir(parents=True, exist_ok=True)
    colors_out.mkdir(parents=True, exist_ok=True)

    theme_entries = []
    scheme_entries = []

    for name in DARK_THEMES:
        pal = palettes[name]
        sn = name.lower()
        cs = f"{name} Theme"

        cols = derive_dark_colors(pal)

        # Theme JSON
        json_path = themes_out / f"{sn}_theme.theme.json"
        json_path.write_text(make_dark_json(name, cs, cols, indent))

        # Editor XML
        xml_path = colors_out / f"{name} Theme.xml"
        xml_content = apply_xml_subs(dark_template_xml, name, "Darcula",
                                     dark_xml_subs(pal))
        xml_path.write_text(xml_content)

        theme_entries.append((f"xscriptor.{sn}.theme",
                              f"/themes/{sn}_theme.theme.json"))
        scheme_entries.append(f"/colors/{name} Theme.xml")
        print(f"  [dark]  {name}")

    for name in LIGHT_THEMES:
        pal = palettes[name]
        sn = name.lower()
        cs = f"{name} Theme"

        cols = derive_light_colors(pal)

        # Theme JSON
        json_path = themes_out / f"{sn}_theme.theme.json"
        raw = make_light_json(name, cs, cols, indent)
        json_path.write_text(postprocess_light_json(raw, cols))

        # Editor XML
        xml_path = colors_out / f"{name} Theme.xml"
        xml_content = apply_xml_subs(light_template_xml, name, "Default",
                                     light_xml_subs(pal))
        xml_path.write_text(xml_content)

        theme_entries.append((f"xscriptor.{sn}.theme",
                              f"/themes/{sn}_theme.theme.json"))
        scheme_entries.append(f"/colors/{name} Theme.xml")
        print(f"  [light] {name}")

    # Write reference plugin.xml
    tl = "\n".join(
        f'    <themeProvider id="{t[0]}" path="{t[1]}"/>' for t in theme_entries
    )
    sl = "\n    ".join(
        f'<bundledColorScheme path="{s}"/>' for s in scheme_entries
    )
    plugin_xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Reference plugin.xml - copy these entries into the real plugin.xml -->
<extensions defaultExtensionNs="com.intellij">
{tl}

    {sl}
</extensions>
"""
    (output_root / "plugin.xml").write_text(plugin_xml_content)

    print(f"\nGenerated {len(DARK_THEMES) + len(LIGHT_THEMES)} themes.")
    print(f"Output: {output_root}")


# ===========================================================================
# CLI
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Generate Xscriptor Theme files from colors.json"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory (default: scripts/output/)",
    )
    parser.add_argument(
        "--templates",
        type=Path,
        default=None,
        help="Path to folder containing dark_template.xml and light_template.xml",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write directly to src/main/resources/ (overwrites real files!)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit minified JSON (default is pretty-printed)",
    )
    args = parser.parse_args()

    # Locate XML templates
    if args.templates:
        template_dir = args.templates
    else:
        template_dir = SCRIPT_DIR / "templates"

    dark_tmpl_path = template_dir / "dark_template.xml"
    light_tmpl_path = template_dir / "light_template.xml"

    if not dark_tmpl_path.exists() or not light_tmpl_path.exists():
        print("ERROR: XML template files not found.")
        print("  Expected:", dark_tmpl_path)
        print("  Expected:", light_tmpl_path)
        print()
        print("  The templates are in scripts/templates/. They contain")
        print("  multi-language syntax highlighting rules per theme.")
        print()
        print("  To restore them from git history:")
        print("    cd xscriptor-theme")
        print("    git checkout 5a39c53 -- \\")
        print("      'src/main/resources/colors/Xscriptor Theme.xml' \\")
        print("      'src/main/resources/colors/Xscriptor Light Theme.xml'")
        print("    cp 'src/main/resources/colors/Xscriptor Theme.xml' \\")
        print("       scripts/templates/dark_template.xml")
        print("    cp 'src/main/resources/colors/Xscriptor Light Theme.xml' \\")
        print("       scripts/templates/light_template.xml")
        sys.exit(1)

    dark_template = dark_tmpl_path.read_text()
    light_template = light_tmpl_path.read_text()

    if args.apply:
        output_root = RESOURCES_DIR
    else:
        output_root = args.output

    indent = None if args.compact else 2
    generate(output_root, dark_template, light_template, indent)


if __name__ == "__main__":
    main()
