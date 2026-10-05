# Live E2E matrix

All rows below were executed on Studionet against `0xC20fCbfE9fCF97624ED45cd17cF3Ec98cA82dEc2`. The machine-readable receipts and post-state reads are in `live-0xc20fcbfe9fcf97624ed45cd17cf3ec98ca82dec2.json`.

| Scenario | Wallet/action | Required observable result |
|---|---|---|
| Deployment isolation | deployer deploys only | PASS — deployer absent from roles; source parity true |
| Happy path | authority creates study; site consents; public caller confirms | PASS — `ELIGIBILITY_CONFIRMED` |
| Failure / fail closed | confirmation before assessment | PASS — `REVIEW_INCOMPLETE` |
| Material conflict | authority proposes changed risk terms; site invokes consensus | PASS — `RECONSENT_REQUIRED`, then `BLOCKED_PENDING_RECONSENT` |
| Recovery | site records current-revision consent with new artifact | PASS — final status `ELIGIBLE`, reconsent count `1` |
| Adversarial role | wrong wallet records consent or proposes revision | PASS — `SITE_ONLY` and `AUTHORITY_ONLY` |
| Adversarial evidence/state | reused artifact and wrong global revision | PASS — `ARTIFACT_ALREADY_USED` and `CONSENT_MUST_TARGET_CURRENT` |
| Lifecycle | authority closes study | PASS — subsequent write returned `STUDY_NOT_ACTIVE`; reads remain available |

Every recorded write has sender, method/arguments, transaction hash, explorer URL, `FINALIZED` status, `MAJORITY_AGREE`, decoded return, and relevant post-state. The non-material and forced provider-failure branches remain direct GenVM tests because live inference cannot honestly be forced to fail on demand.
