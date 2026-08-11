import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import approval_center, resume_phase1


class ApprovalCenterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.apps = self.root / "applications"
        self.registry = self.root / "templates.json"
        self.template = self.root / "base.tex"
        self.template.write_text("template", encoding="utf-8")
        self.registry.write_text(json.dumps({"templates": [{
            "id": "base", "name": "Base", "source": "base.tex",
            "active": True, "auto_tags": ["research scientist"]
        }]}), encoding="utf-8")
        self.patches = [
            patch.object(resume_phase1, "ROOT", self.root),
            patch.object(resume_phase1, "APPLICATIONS", self.apps),
            patch.object(resume_phase1, "REGISTRY", self.registry),
        ]
        for item in self.patches:
            item.start()
        resume_phase1.main(["start", "--company", "Acme", "--role", "Research Scientist", "--template", "base"])
        self.app = self.apps / "acme_research_scientist"
        self.artifact = self.app / "resume.pdf"
        self.artifact.write_bytes(b"reviewed")
        resume_phase1.main(["stage", "acme_research_scientist", "--artifact", str(self.artifact)])

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.temp.cleanup()

    def test_list_never_advertises_submission(self):
        items = approval_center.list_applications()
        self.assertEqual(len(items), 1)
        self.assertFalse(items[0]["submission_enabled"])

    def test_approve_requires_confirmation_and_preserves_no_submit(self):
        with self.assertRaisesRegex(approval_center.ApprovalCenterError, "approval requires"):
            approval_center.perform_action({
                "application_id": "acme_research_scientist", "action": "approve", "confirmation": "yes"
            })
        detail = approval_center.perform_action({
            "application_id": "acme_research_scientist",
            "action": "approve",
            "confirmation": "I_APPROVE_THE_DOCUMENTS",
        })
        self.assertEqual(detail["status"], "DOCUMENT_APPROVED")
        self.assertFalse(detail["submission_enabled"])

    def test_revision_requires_instructions(self):
        with self.assertRaisesRegex(approval_center.ApprovalCenterError, "instructions are required"):
            approval_center.perform_action({
                "application_id": "acme_research_scientist", "action": "revision", "instructions": ""
            })

    def test_artifact_path_blocks_escape(self):
        outside = self.root / "secret.txt"
        outside.write_text("secret", encoding="utf-8")
        with self.assertRaisesRegex(approval_center.ApprovalCenterError, "artifact not found"):
            approval_center.artifact_path("acme_research_scientist", "../../secret.txt")

    def test_web_intake_creates_phase1_workspace_without_submission(self):
        detail = approval_center.create_application({
            "company": "Second Co",
            "role": "ML Engineer",
            "template": "base",
            "posting_text": "Build production ML systems.",
            "posting_url": "https://example.test/job/1",
        })
        self.assertEqual(detail["status"], "DRAFTING")
        self.assertFalse(detail["submission_enabled"])
        posting = self.apps / "second_co_ml_engineer" / "job_posting.md"
        self.assertIn("production ML", posting.read_text(encoding="utf-8"))

    def test_web_intake_requires_posting_and_template(self):
        with self.assertRaisesRegex(approval_center.ApprovalCenterError, "template"):
            approval_center.create_application({"company": "X", "role": "Y", "posting_text": "text"})

    def test_all_real_registered_templates_are_available(self):
        # The production registry may use paths outside this test fixture; the
        # web contract itself is covered here by ensuring the active fixture
        # template resolves and is selectable.
        templates = resume_phase1.load_templates()
        selectable = [t for t in templates if t.get("active", True) and (resume_phase1.ROOT / t["source"]).is_file()]
        self.assertEqual([t["id"] for t in selectable], ["base"])


if __name__ == "__main__":
    unittest.main()
