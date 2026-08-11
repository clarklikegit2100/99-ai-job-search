# /approval-center - Open the Local Resume Approval Center

Start the unified Phase 1 intake and Phase 2 candidate approval interface. This command is local-only and
must never deploy, publish, tunnel, or expose the approval center to another
device or network interface.

## Steps

1. Confirm `tools/approval_center.py` and `approval_center/index.html` exist.
2. Start `python tools/approval_center.py` in a retained background session.
3. Wait for the exact localhost URL printed by the server.
4. Open that URL in the local browser once.
5. Tell the candidate that closing the retained process stops the center.

If the default port is busy, retry once with an unused high port:

```text
python tools/approval_center.py --port <port>
```

## Safety rules

- Bind only to `127.0.0.1` or `localhost`.
- Never use `0.0.0.0`, a LAN address, a tunnel, or a hosted deployment.
- Never add a submission button or infer submission approval from document
  approval.
- The interface may create a Phase 1 workspace, select a registered template,
  approve staged hashes, request revisions, or reject a package. It may not
  upload or submit an application.
- Do not edit application manifests directly; all decisions must pass through
  the Phase 1 state and hash guards.
