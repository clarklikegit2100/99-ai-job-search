import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import resume_phase1


class ResumePhase1Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.apps = self.root / "applications"
        self.registry = self.root / "templates.json"
        self.template = self.root / "base.tex"
        self.template.write_text("template", encoding="utf-8")
        self.registry.write_text(json.dumps({"templates": [{
            "id": "jian-moderncv",
            "source": "base.tex",
            "active": True,
            "auto_tags": ["research scientist"]
        }]}), encoding="utf-8")
        self.patches = [
            patch.object(resume_phase1, "ROOT", self.root),
            patch.object(resume_phase1, "APPLICATIONS", self.apps),
            patch.object(resume_phase1, "REGISTRY", self.registry),
        ]
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.temp.cleanup()

    def start(self):
        return resume_phase1.main([
            "start", "--company", "Acme", "--role", "Research Scientist",
            "--template", "jian-moderncv", "--posting-text", "A real posting"
        ])

    def test_start_creates_private_manifest_with_submission_disabled(self):
        self.assertEqual(self.start(), 0)
        path = self.apps / "acme_research_scientist" / "generation_manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "DRAFTING")
        self.assertFalse(manifest["submission_enabled"])
        self.assertEqual(manifest["template"]["id"], "jian-moderncv")

    def test_auto_template_requires_an_available_source(self):
        self.assertEqual(resume_phase1.main([
            "start", "--company", "Acme", "--role", "Research Scientist",
            "--template", "auto"
        ]), 0)
        manifest = json.loads((self.apps / "acme_research_scientist" / "generation_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["template"]["id"], "jian-moderncv")

    def test_approval_is_bound_to_staged_hash(self):
        self.assertEqual(self.start(), 0)
        app = self.apps / "acme_research_scientist"
        artifact = app / "resume.pdf"
        artifact.write_bytes(b"approved bytes")
        self.assertEqual(resume_phase1.main([
            "stage", "acme_research_scientist", "--artifact", str(artifact)
        ]), 0)
        artifact.write_bytes(b"changed after review")
        self.assertEqual(resume_phase1.main([
            "approve-documents", "acme_research_scientist",
            "--confirm", "I_APPROVE_THE_DOCUMENTS"
        ]), 1)
        manifest = json.loads((app / "generation_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "AWAITING_DOCUMENT_APPROVAL")

    def test_approval_requires_exact_confirmation_phrase(self):
        self.assertEqual(self.start(), 0)
        app = self.apps / "acme_research_scientist"
        artifact = app / "resume.pdf"
        artifact.write_bytes(b"approved bytes")
        resume_phase1.main(["stage", "acme_research_scientist", "--artifact", str(artifact)])
        self.assertEqual(resume_phase1.main([
            "approve-documents", "acme_research_scientist", "--confirm", "yes"
        ]), 1)

    def test_valid_approval_does_not_enable_submission(self):
        self.assertEqual(self.start(), 0)
        app = self.apps / "acme_research_scientist"
        artifact = app / "resume.pdf"
        artifact.write_bytes(b"approved bytes")
        resume_phase1.main(["stage", "acme_research_scientist", "--artifact", str(artifact)])
        self.assertEqual(resume_phase1.main([
            "approve-documents", "acme_research_scientist",
            "--confirm", "I_APPROVE_THE_DOCUMENTS"
        ]), 0)
        manifest = json.loads((app / "generation_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "DOCUMENT_APPROVED")
        self.assertFalse(manifest["submission_enabled"])

    def test_rejected_package_is_terminal(self):
        self.assertEqual(self.start(), 0)
        self.assertEqual(resume_phase1.main([
            "reject", "acme_research_scientist", "--reason", "not a fit"
        ]), 0)
        manifest = json.loads((self.apps / "acme_research_scientist" / "generation_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "REJECTED")
        self.assertEqual(resume_phase1.main([
            "request-revision", "acme_research_scientist", "--instructions", "retry"
        ]), 1)


if __name__ == "__main__":
    unittest.main()
