# ConsentDeltaGate

Clinical-trial consent versions can change after subjects enroll. ConsentDeltaGate stores authority-authenticated revisions, uses GenLayer consensus to classify a narrow semantic delta, and deterministically prevents eligibility confirmation until a site records re-consent when required.

There is no frontend and no financial flow. The deployment wallet has no contract role.

## Contract flow

1. Wallet A calls `create_study(study_ref, wallet_B, baseline_json)` and becomes that study's authority.
2. Wallet B records a pseudonymous subject commitment and consent artifact digest.
3. Wallet A proposes an immutable child revision whose parent must be the current head.
4. Any wallet calls `assess_transition`. Consensus returns only four bounded semantic categories.
5. Deterministic code derives the edge outcome and subject status.
6. If material, Wallet B records a fresh current-revision consent; any wallet can then confirm eligibility.

Reviewers can create their own study with their own two wallets. They do not need the original deployer.

## Source of truth

The complete structured documents are written on-chain by the study authority. The AI is never asked to discover a source or trust a URL. It compares the exact parent and child snapshots, and material conclusions require grounded section IDs. See [SPEC.md](SPEC.md) and [verification/TEST_RESOURCE_MANIFEST.json](verification/TEST_RESOURCE_MANIFEST.json).

## Local verification

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

Direct GenVM tests cover happy path, material conflict, fail-closed retry, stale-parent conflict, replay, role attacks, hostile document text, citation grounding, and deterministic derivation.

## Live evidence status

The source-identical contract is deployed at [`0xC20f...dEc2`](https://explorer-studio.genlayer.com/address/0xC20fCbfE9fCF97624ED45cd17cF3Ec98cA82dEc2). A complete two-wallet Studionet lifecycle, including genuine consensus, material blocking, re-consent recovery, adversarial failures and terminal closure, is documented in [verification/studionet-e2e.md](verification/studionet-e2e.md). Machine-readable receipts and post-state reads are retained beside it. No private key or API token is committed.
