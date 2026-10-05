# Local verification result

- Date: 2026-10-05 (Asia/Bangkok)
- Command: `pytest -q`
- Result: `7 passed in 0.69s`
- Execution layer: direct GenVM contract harness (`gltest.direct`)

Covered cases:

1. deployment wallet has no implicit role;
2. happy path and revision-bound eligibility confirmation;
3. material change blocks an already-consented subject;
4. site-only re-consent restores eligibility;
5. unknown evidence fails closed and can be retried;
6. stale parent and artifact replay conflicts are rejected;
7. unauthorized authority/site actions are rejected;
8. hostile document text cannot change the closed output schema;
9. citations must reference section IDs present in both snapshots;
10. consequence derivation is deterministic.

This is reproducible local evidence, not a claim of Studionet execution. Live transaction evidence remains explicitly pending in `LIVE_MATRIX.md` until deployment.
