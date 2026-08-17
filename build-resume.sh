#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_FILE="$SCRIPT_DIR/cv-output/main_example-jian.tex"
OUTPUT_DIR="$SCRIPT_DIR/cv-output"

if ! command -v lualatex >/dev/null 2>&1; then
  echo "ERROR: lualatex was not found in PATH." >&2
  echo "Install TeX Live, MacTeX, TinyTeX, or MiKTeX and try again." >&2
  exit 1
fi

if [[ ! -f "$SOURCE_FILE" ]]; then
  echo "ERROR: Resume source not found: $SOURCE_FILE" >&2
  exit 1
fi

echo "Building main_example-jian.pdf..."
lualatex --interaction=nonstopmode --halt-on-error \
  --output-directory="$OUTPUT_DIR" "$SOURCE_FILE"
lualatex --interaction=nonstopmode --halt-on-error \
  --output-directory="$OUTPUT_DIR" "$SOURCE_FILE"

echo
echo "PDF created: $OUTPUT_DIR/main_example-jian.pdf"
