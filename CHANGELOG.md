# Changelog

## 2026-08-23

- Migrate all customizations to xscriptor-colors

## 2026-07-19
- Updated `colors.md` with refined palettes (darker backgrounds for X, Lahabana, Tokio; adjusted Oslo foreground; added `background`/`foreground` fields).
- Added `colors.json` as the canonical machine-readable palette source for cross-platform consistency.
- Updated `generate_themes.py` to read from `colors.json` and use `background`/`foreground` fields when present.
- Extended JetBrains plugin compatibility to build `262.*` (IntelliJ 2026.2+).
