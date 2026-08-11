#!/usr/bin/env python3
"""Local-only Phase 2 approval center for resume application packages."""

import argparse
import json
import mimetypes
import secrets
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import unquote, urlparse

try:
    from tools import resume_phase1
except ImportError:  # Direct execution: python tools/approval_center.py
    import resume_phase1


ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = ROOT / "approval_center"


class ApprovalCenterError(Exception):
    pass


def safe_application_dir(application_id):
    if not application_id or application_id != resume_phase1.slugify(application_id):
        raise ApprovalCenterError("invalid application id")
    return resume_phase1.application_dir(application_id)


def list_applications():
    root = resume_phase1.APPLICATIONS
    if not root.is_dir():
        return []
    items = []
    for manifest_path in root.glob("*/generation_manifest.json"):
        try:
            manifest = resume_phase1.read_json(manifest_path)
        except resume_phase1.Phase1Error:
            continue
        items.append({
            "application_id": manifest.get("application_id", manifest_path.parent.name),
            "company": manifest.get("company", ""),
            "role": manifest.get("role", ""),
            "status": manifest.get("status", "UNKNOWN"),
            "template": manifest.get("template", {}).get("name", ""),
            "updated_at": manifest.get("updated_at", ""),
            "artifact_count": len(manifest.get("artifacts", [])),
            "submission_enabled": False,
        })
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)


def application_detail(application_id):
    _path, manifest = resume_phase1.load_manifest(application_id)
    manifest = dict(manifest)
    manifest["submission_enabled"] = False
    return manifest


def artifact_path(application_id, relative_path):
    app_dir = safe_application_dir(application_id).resolve()
    candidate = (app_dir / unquote(relative_path)).resolve()
    if app_dir not in candidate.parents or not candidate.is_file():
        raise ApprovalCenterError("artifact not found")
    return candidate


def perform_action(payload):
    if not isinstance(payload, dict):
        raise ApprovalCenterError("request body must be an object")
    application_id = str(payload.get("application_id", ""))
    action = payload.get("action")
    safe_application_dir(application_id)
    try:
        if action == "start":
            raise ApprovalCenterError("start must use create_application")
        elif action == "approve":
            resume_phase1.command_approve(SimpleNamespace(
                application_id=application_id,
                confirm=payload.get("confirmation", ""),
                approved_by="candidate",
                note=str(payload.get("note", "")),
            ))
        elif action == "revision":
            instructions = str(payload.get("instructions", "")).strip()
            if not instructions:
                raise ApprovalCenterError("revision instructions are required")
            resume_phase1.command_revision(SimpleNamespace(
                application_id=application_id,
                instructions=instructions,
            ))
        elif action == "reject":
            resume_phase1.command_reject(SimpleNamespace(
                application_id=application_id,
                reason=str(payload.get("reason", "")),
            ))
        else:
            raise ApprovalCenterError("unknown action")
    except resume_phase1.Phase1Error as exc:
        raise ApprovalCenterError(str(exc)) from exc
    return application_detail(application_id)


def create_application(payload):
    if not isinstance(payload, dict):
        raise ApprovalCenterError("request body must be an object")
    company = str(payload.get("company", "")).strip()
    role = str(payload.get("role", "")).strip()
    template = str(payload.get("template", "")).strip()
    posting_text = str(payload.get("posting_text", "")).strip()
    posting_url = str(payload.get("posting_url", "")).strip()
    if not company or not role:
        raise ApprovalCenterError("company and role are required")
    if not template:
        raise ApprovalCenterError("a resume template must be selected")
    if not posting_text and not posting_url:
        raise ApprovalCenterError("paste the job description or provide its URL")
    try:
        resume_phase1.command_start(SimpleNamespace(
            company=company,
            role=role,
            template=template,
            posting_file=None,
            posting_text=posting_text,
            posting_url=posting_url,
            replace=False,
        ))
    except resume_phase1.Phase1Error as exc:
        raise ApprovalCenterError(str(exc)) from exc
    application_id = f"{resume_phase1.slugify(company)}_{resume_phase1.slugify(role)}"
    return application_detail(application_id)


class ApprovalHandler(BaseHTTPRequestHandler):
    server_version = "ResumeApprovalCenter/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("approval-center: " + fmt % args + "\n")

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, disposition="inline"):
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Disposition", f'{disposition}; filename="{path.name}"')
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/session":
                return self.send_json(200, {"token": self.server.approval_token, "submission_enabled": False})
            if parsed.path == "/api/applications":
                return self.send_json(200, {"applications": list_applications()})
            if parsed.path == "/api/templates":
                templates = []
                for registered in resume_phase1.load_templates():
                    item = dict(registered)
                    item["available"] = (resume_phase1.ROOT / item["source"]).is_file()
                    templates.append(item)
                return self.send_json(200, {"templates": templates})
            if parsed.path.startswith("/api/applications/"):
                application_id = parsed.path.removeprefix("/api/applications/")
                return self.send_json(200, application_detail(application_id))
            if parsed.path.startswith("/files/"):
                parts = parsed.path.split("/", 3)
                if len(parts) != 4:
                    raise ApprovalCenterError("invalid artifact path")
                return self.send_file(artifact_path(parts[2], parts[3]))
            ui_path = "index.html" if parsed.path == "/" else parsed.path.lstrip("/")
            candidate = (UI_ROOT / ui_path).resolve()
            if UI_ROOT.resolve() not in candidate.parents or not candidate.is_file():
                return self.send_json(404, {"error": "not found"})
            return self.send_file(candidate)
        except (ApprovalCenterError, resume_phase1.Phase1Error) as exc:
            self.send_json(404, {"error": str(exc)})

    def do_POST(self):
        if self.path not in ("/api/action", "/api/applications"):
            return self.send_json(404, {"error": "not found"})
        token = self.headers.get("X-Approval-Token", "")
        if not secrets.compare_digest(token, self.server.approval_token):
            return self.send_json(403, {"error": "invalid approval session token"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                raise ApprovalCenterError("invalid request size")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            detail = create_application(payload) if self.path == "/api/applications" else perform_action(payload)
            self.send_json(200, {"ok": True, "application": detail})
        except (ApprovalCenterError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})


def build_parser():
    parser = argparse.ArgumentParser(description="Run the local Phase 2 resume approval center")
    parser.add_argument("--host", default="127.0.0.1", choices=("127.0.0.1", "localhost"))
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="open the local page in the default browser")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), ApprovalHandler)
    server.approval_token = secrets.token_urlsafe(32)
    url = f"http://{args.host}:{server.server_port}"
    print(f"AI job application studio: {url}")
    print("Local-only. Phase 2 cannot submit applications.")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
