#!/usr/bin/env python3
"""Local Phase 1 state and approval controls for generated resume packages.

This tool deliberately has no submit/apply-to-website operation. It prepares a
private application workspace, records generated artifacts, and requires an
explicit, hash-bound document approval before a package can be handed off.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "resume_templates.json"
APPLICATIONS = ROOT / "documents" / "applications"
ALLOWED_TRANSITIONS = {
    "DRAFTING": {"AWAITING_DOCUMENT_APPROVAL", "REJECTED"},
    "AWAITING_DOCUMENT_APPROVAL": {"DOCUMENT_APPROVED", "REVISION_REQUESTED", "REJECTED"},
    "REVISION_REQUESTED": {"AWAITING_DOCUMENT_APPROVAL", "REJECTED"},
    "DOCUMENT_APPROVED": {"REVISION_REQUESTED"},
    "REJECTED": set(),
}


class Phase1Error(Exception):
    pass


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value):
    value = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    if not value:
        raise Phase1Error("company and role must contain letters or numbers")
    return value


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise Phase1Error(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise Phase1Error(f"invalid JSON in {path}: {exc}") from exc


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_templates():
    data = read_json(REGISTRY)
    templates = data.get("templates")
    if not isinstance(templates, list):
        raise Phase1Error("template registry must contain a templates list")
    return templates


def template_by_id(template_id):
    for template in load_templates():
        if template.get("id") == template_id and template.get("active", True):
            source = ROOT / template["source"]
            if not source.is_file():
                raise Phase1Error(f"template source does not exist: {source}")
            return template
    raise Phase1Error(f"unknown or inactive template: {template_id}")


def auto_template(role):
    role_words = set(re.findall(r"[a-z0-9]+", role.lower()))
    candidates = []
    for template in load_templates():
        if not template.get("active", True):
            continue
        score = 0
        for tag in template.get("auto_tags", []):
            tag_words = set(re.findall(r"[a-z0-9]+", tag.lower()))
            score += len(role_words & tag_words)
            if tag.lower() in role.lower():
                score += 3
        candidates.append((score, template["id"], template))
    if not candidates:
        raise Phase1Error("no active resume templates are registered")
    selected = max(candidates, key=lambda item: (item[0], item[1]))[2]
    return template_by_id(selected["id"])


def application_dir(application_id):
    path = (APPLICATIONS / application_id).resolve()
    root = APPLICATIONS.resolve()
    if root not in path.parents:
        raise Phase1Error("invalid application id")
    return path


def load_manifest(application_id):
    path = application_dir(application_id) / "generation_manifest.json"
    return path, read_json(path)


def transition(manifest, target):
    current = manifest.get("status")
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise Phase1Error(f"invalid state transition: {current} -> {target}")
    manifest["status"] = target
    manifest["updated_at"] = utc_now()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(path, app_dir):
    resolved = path.resolve()
    if app_dir.resolve() not in resolved.parents:
        raise Phase1Error(f"artifact must be inside {app_dir}: {path}")
    if not resolved.is_file():
        raise Phase1Error(f"artifact does not exist: {path}")
    return {
        "path": str(resolved.relative_to(app_dir.resolve())).replace("\\", "/"),
        "sha256": sha256(resolved),
        "bytes": resolved.stat().st_size,
    }


def command_templates(_args):
    templates = []
    for registered in load_templates():
        item = dict(registered)
        item["available"] = (ROOT / item["source"]).is_file()
        templates.append(item)
    print(json.dumps({"templates": templates}, indent=2, ensure_ascii=False))


def command_start(args):
    template = auto_template(args.role) if args.template == "auto" else template_by_id(args.template)
    application_id = f"{slugify(args.company)}_{slugify(args.role)}"
    app_dir = application_dir(application_id)
    manifest_path = app_dir / "generation_manifest.json"
    if manifest_path.exists() and not args.replace:
        raise Phase1Error(f"application already exists: {application_id}; use --replace intentionally")
    app_dir.mkdir(parents=True, exist_ok=True)

    posting_text = ""
    if args.posting_file:
        posting_path = Path(args.posting_file).resolve()
        if not posting_path.is_file():
            raise Phase1Error(f"posting file does not exist: {posting_path}")
        posting_text = posting_path.read_text(encoding="utf-8")
    elif args.posting_text:
        posting_text = args.posting_text
    if posting_text:
        (app_dir / "job_posting.md").write_text(posting_text.rstrip() + "\n", encoding="utf-8")

    now = utc_now()
    manifest = {
        "schema_version": 1,
        "application_id": application_id,
        "company": args.company,
        "role": args.role,
        "posting_url": args.posting_url or "",
        "template": template,
        "status": "DRAFTING",
        "created_at": now,
        "updated_at": now,
        "facts_sources": [
            ".claude/skills/job-application-assistant/01-candidate-profile.md",
            "CLAUDE.md",
            "cv/main_example-jian.tex"
        ],
        "artifacts": [],
        "approval": None,
        "submission_enabled": False
    }
    write_json(manifest_path, manifest)
    write_json(app_dir / "approval.json", {
        "application_id": application_id,
        "decision": "PENDING",
        "document_hashes": [],
        "submission_approval": "NOT_AVAILABLE_IN_PHASE_1"
    })
    print(json.dumps({"application_id": application_id, "directory": str(app_dir), "template": template["id"], "status": "DRAFTING"}, indent=2))


def command_stage(args):
    manifest_path, manifest = load_manifest(args.application_id)
    app_dir = manifest_path.parent
    records = [artifact_record(Path(item), app_dir) for item in args.artifact]
    required_suffixes = {".tex", ".docx", ".pdf"}
    if not any(Path(record["path"]).suffix.lower() in required_suffixes for record in records):
        raise Phase1Error("at least one resume source or PDF artifact is required")
    target = "AWAITING_DOCUMENT_APPROVAL"
    transition(manifest, target)
    manifest["artifacts"] = records
    manifest["approval"] = None
    write_json(manifest_path, manifest)
    write_json(app_dir / "approval.json", {
        "application_id": args.application_id,
        "decision": "PENDING",
        "requested_at": utc_now(),
        "document_hashes": records,
        "submission_approval": "NOT_AVAILABLE_IN_PHASE_1"
    })
    print(json.dumps({"application_id": args.application_id, "status": target, "artifacts": records}, indent=2))


def command_approve(args):
    if args.confirm != "I_APPROVE_THE_DOCUMENTS":
        raise Phase1Error("approval requires --confirm I_APPROVE_THE_DOCUMENTS")
    manifest_path, manifest = load_manifest(args.application_id)
    if manifest.get("status") != "AWAITING_DOCUMENT_APPROVAL":
        raise Phase1Error("documents can only be approved from AWAITING_DOCUMENT_APPROVAL")
    app_dir = manifest_path.parent
    for record in manifest.get("artifacts", []):
        path = app_dir / record["path"]
        if not path.is_file() or sha256(path) != record["sha256"]:
            raise Phase1Error(f"artifact changed after staging; re-stage and review it: {record['path']}")
    transition(manifest, "DOCUMENT_APPROVED")
    approval = {
        "application_id": args.application_id,
        "decision": "APPROVED",
        "approved_at": utc_now(),
        "approved_by": args.approved_by,
        "note": args.note or "",
        "document_hashes": manifest["artifacts"],
        "submission_approval": "NOT_AVAILABLE_IN_PHASE_1"
    }
    manifest["approval"] = approval
    write_json(manifest_path, manifest)
    write_json(app_dir / "approval.json", approval)
    print(json.dumps({"application_id": args.application_id, "status": "DOCUMENT_APPROVED", "submission_enabled": False}, indent=2))


def command_revision(args):
    manifest_path, manifest = load_manifest(args.application_id)
    transition(manifest, "REVISION_REQUESTED")
    manifest["approval"] = None
    write_json(manifest_path, manifest)
    write_json(manifest_path.parent / "approval.json", {
        "application_id": args.application_id,
        "decision": "REVISION_REQUESTED",
        "requested_at": utc_now(),
        "instructions": args.instructions,
        "document_hashes": [],
        "submission_approval": "NOT_AVAILABLE_IN_PHASE_1"
    })
    print(json.dumps({"application_id": args.application_id, "status": "REVISION_REQUESTED"}, indent=2))


def command_reject(args):
    manifest_path, manifest = load_manifest(args.application_id)
    transition(manifest, "REJECTED")
    manifest["approval"] = None
    write_json(manifest_path, manifest)
    write_json(manifest_path.parent / "approval.json", {
        "application_id": args.application_id,
        "decision": "REJECTED",
        "rejected_at": utc_now(),
        "reason": args.reason or "",
        "document_hashes": [],
        "submission_approval": "NOT_AVAILABLE_IN_PHASE_1"
    })
    print(json.dumps({"application_id": args.application_id, "status": "REJECTED"}, indent=2))


def command_show(args):
    _path, manifest = load_manifest(args.application_id)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


def build_parser():
    parser = argparse.ArgumentParser(description="Phase 1 resume generation state and approval guard")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("templates", help="list registered resume templates")
    p.set_defaults(func=command_templates)

    p = sub.add_parser("start", help="create a private application workspace")
    p.add_argument("--company", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--template", default="auto")
    p.add_argument("--posting-file")
    p.add_argument("--posting-text")
    p.add_argument("--posting-url")
    p.add_argument("--replace", action="store_true")
    p.set_defaults(func=command_start)

    p = sub.add_parser("stage", help="hash artifacts and request human document approval")
    p.add_argument("application_id")
    p.add_argument("--artifact", action="append", required=True)
    p.set_defaults(func=command_stage)

    p = sub.add_parser("approve-documents", help="approve unchanged staged documents")
    p.add_argument("application_id")
    p.add_argument("--confirm", required=True)
    p.add_argument("--approved-by", default="candidate")
    p.add_argument("--note")
    p.set_defaults(func=command_approve)

    p = sub.add_parser("request-revision", help="return a package for revision")
    p.add_argument("application_id")
    p.add_argument("--instructions", required=True)
    p.set_defaults(func=command_revision)

    p = sub.add_parser("reject", help="reject an application package")
    p.add_argument("application_id")
    p.add_argument("--reason")
    p.set_defaults(func=command_reject)

    p = sub.add_parser("show", help="show an application manifest")
    p.add_argument("application_id")
    p.set_defaults(func=command_show)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except Phase1Error as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
