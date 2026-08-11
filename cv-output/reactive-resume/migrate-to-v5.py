#!/usr/bin/env python3
"""Convert the repository's Jian Zhao resume from the old mixed schema to RR v5."""

import json
from copy import deepcopy
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "jian-zhao.json"
BACKUP = HERE / "jian-zhao.pre-v5-fix.json"


SECTION_DEFAULTS = {
    "profiles": ("messenger-logo", "Profiles"),
    "experience": ("briefcase", "Professional and Research Experience"),
    "education": ("graduation-cap", "Education"),
    "projects": ("code-simple", "Projects"),
    "skills": ("compass-tool", "Core Competencies"),
    "languages": ("translate", "Languages"),
    "interests": ("football", "Interests"),
    "awards": ("trophy", "Awards"),
    "certifications": ("certificate", "Honors & Certifications"),
    "publications": ("books", "Selected Publications"),
    "volunteer": ("hand-heart", "Volunteer"),
    "references": ("phone", "References"),
}


def website(item):
    old = item.get("url", {})
    return {
        "url": old.get("href", ""),
        "label": old.get("label", ""),
        "inlineLink": False,
    }


def base_item(item):
    return {"id": item["id"], "hidden": not item.get("visible", True)}


def convert_item(section, item):
    out = base_item(item)
    if section == "experience":
        out.update(company=item["company"], position=item.get("position", ""),
                   location=item.get("location", ""), period=item.get("date", ""),
                   website=website(item), description=item.get("summary", ""), roles=[])
    elif section == "education":
        out.update(school=item["institution"], degree=item.get("studyType", ""),
                   area=item.get("area", ""), grade=item.get("score", ""),
                   location=item.get("location", ""), period=item.get("date", ""),
                   website=website(item), description=item.get("summary", ""))
    elif section == "skills":
        out.update(icon="", iconColor="", name=item["name"],
                   proficiency=item.get("description", ""), level=item.get("level", 0),
                   keywords=item.get("keywords", []))
    elif section == "languages":
        out.update(language=item["name"], fluency=item.get("description", ""),
                   level=item.get("level", 0))
    elif section == "publications":
        out.update(title=item["name"], publisher=item.get("publisher", ""),
                   date=item.get("date", ""), website=website(item),
                   description=item.get("summary", ""))
    elif section == "certifications":
        out.update(title=item["name"], issuer=item.get("issuer", ""),
                   date=item.get("date", ""), website=website(item),
                   description=item.get("summary", ""))
    elif section == "references":
        out.update(name=item["name"], position=item.get("description", ""),
                   website=website(item), phone="", description=item.get("summary", ""))
    else:
        raise ValueError(f"Unsupported populated section: {section}")
    return out


def section(source, key):
    old = source.get("sections", {}).get(key, {})
    icon, default_title = SECTION_DEFAULTS[key]
    return {
        "icon": icon,
        "items": [convert_item(key, item) for item in old.get("items", [])],
        "title": old.get("name", default_title),
        "hidden": not old.get("visible", bool(old)),
        "columns": old.get("columns", 1),
        "keepTogether": False,
        "startOnNewPage": False,
    }


def convert(source):
    basics = source["basics"]
    old_summary = source["sections"]["summary"]
    data = {
        "basics": {
            "name": basics.get("name", ""),
            "email": basics.get("email", ""),
            "phone": basics.get("phone", ""),
            "website": {
                "url": basics.get("url", {}).get("href", ""),
                "label": basics.get("url", {}).get("label", ""),
            },
            "headline": basics.get("headline", ""),
            "location": basics.get("location", ""),
            "customFields": [
                {
                    "id": field["id"],
                    "icon": "",
                    "text": f'{field.get("name", "")}: {field.get("value", "")}',
                    "link": "",
                }
                for field in basics.get("customFields", [])
            ],
        },
        "picture": {
            "url": basics.get("picture", {}).get("url", ""),
            "size": basics.get("picture", {}).get("size", 80),
            "hidden": basics.get("picture", {}).get("effects", {}).get("hidden", True),
            "rotation": 0,
            "aspectRatio": basics.get("picture", {}).get("aspectRatio", 1),
            "borderColor": "rgba(0, 0, 0, 0.5)",
            "borderWidth": 0,
            "shadowColor": "rgba(0, 0, 0, 0.5)",
            "shadowWidth": 0,
            "borderRadius": basics.get("picture", {}).get("borderRadius", 0),
        },
        "summary": {
            "icon": "article",
            "title": old_summary.get("name", "Summary"),
            "hidden": not old_summary.get("visible", True),
            "columns": old_summary.get("columns", 1),
            "content": old_summary.get("content", ""),
            "keepTogether": False,
            "startOnNewPage": False,
        },
        "sections": {key: section(source, key) for key in SECTION_DEFAULTS},
        "customSections": [],
        "metadata": {
            "page": {
                "gapX": 4, "gapY": 6, "format": "a4", "locale": "en-US",
                "marginX": 14, "marginY": 12, "hideIcons": False,
                "hideSectionIcons": True, "hideLinkUnderline": False,
            },
            "notes": "Jian Zhao resume — Reactive Resume v5 schema",
            "design": {
                "level": {"icon": "star", "type": "circle"},
                "colors": {
                    "text": "rgba(26, 26, 26, 1)",
                    "primary": "rgba(26, 86, 219, 1)",
                    "background": "rgba(255, 255, 255, 1)",
                },
            },
            "layout": {
                "pages": [{
                    "main": ["summary", "experience", "education"],
                    "sidebar": ["skills", "publications", "certifications", "languages", "references"],
                    "fullWidth": False,
                }],
                "sidebarWidth": 35,
            },
            "template": "kakuna",
            "styleRules": [],
            "stylesheet": {
                "mode": "semantic",
                "source": {"text": "@version 1;\n", "languageVersion": 1},
                "applied": {"text": "@version 1;\n", "languageVersion": 1},
            },
            "typography": {
                "body": {"fontSize": 10, "fontFamily": "IBM Plex Serif", "lineHeight": 1.5, "fontWeights": ["400", "500"]},
                "heading": {"fontSize": 14, "fontFamily": "IBM Plex Serif", "lineHeight": 1.5, "fontWeights": ["600"]},
            },
        },
    }
    return data


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if "picture" in source and "summary" in source:
        print(f"{SOURCE.name} is already in the Reactive Resume v5 shape; no changes made")
        return
    if not BACKUP.exists():
        BACKUP.write_text(json.dumps(deepcopy(source), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SOURCE.write_text(json.dumps(convert(source), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Converted {SOURCE.name}; original preserved as {BACKUP.name}")


if __name__ == "__main__":
    main()
