#!/usr/bin/env python3
"""
Switch the Reactive Resume template style without re-importing.

Usage:
    python switch-template.py rhyhorn       # clean, modern (default)
    python switch-template.py chikorita     # ATS-friendly, minimal
    python switch-template.py onyx          # dark, bold
    python switch-template.py kakuna        # compact, two-column
    python switch-template.py bronzor       # classic
    python switch-template.py pikachu       # colorful
    python switch-template.py gengar        # dark sidebar
    python switch-template.py ditto         # minimal

Available templates:
    rhyhorn     - Clean modern layout (best for industry AI roles)
    chikorita   - ATS-optimized minimal (best for ATS-heavy portals)
    onyx        - Dark elegant (best for design-forward companies)
    kakuna      - Compact two-column
    bronzor     - Classic professional
    pikachu     - Colorful creative
    gengar      - Dark sidebar
    ditto       - Ultra-minimal
"""

import json
import sys
import shutil
from pathlib import Path

TEMPLATES = ["rhyhorn", "chikorita", "onyx", "kakuna", "bronzor", "pikachu", "gengar", "ditto"]
JSON_FILE = Path(__file__).parent / "jian-zhao.json"


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in TEMPLATES:
        print(__doc__)
        print(f"\nCurrent template:", end=" ")
        data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
        print(data["metadata"]["template"])
        sys.exit(1)

    template = sys.argv[1]
    data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    old = data["metadata"]["template"]

    if old == template:
        print(f"Already using template: {template}")
        sys.exit(0)

    # Backup
    backup = JSON_FILE.with_suffix(f".{old}.bak.json")
    shutil.copy(JSON_FILE, backup)

    data["metadata"]["template"] = template
    JSON_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Switched: {old} → {template}")
    print(f"Backup saved: {backup.name}")
    print(f"\nRe-import jian-zhao.json into Reactive Resume to apply the new style.")


if __name__ == "__main__":
    main()
