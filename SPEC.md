# ConsentDeltaGate specification

## Proof obligation card

| Field | Binding definition |
|---|---|
| Exact claim | An authority-authenticated child consent revision either does or does not materially change participant-facing risk, procedure, withdrawal-right, or data-use terms relative to its direct parent. |
| What falsifies it | A cited parent/child section pair demonstrates a material change while the recorded transition says `NO_RECONSENT_REQUIRED`, or all four dimensions are unchanged while it says `RECONSENT_REQUIRED`. |
| Sufficient evidence | The complete canonical parent and child documents stored on-chain, each containing bounded typed sections and an SHA-256 digest. |
| Insufficient evidence | A URL, summary, claimant assertion, missing section, ungrounded citation, malformed model output, or unavailable inference. These normalize to `UNKNOWN`. |
| Authoritative source | The study authority wallet is authoritative only for publishing that study's versioned consent text. The contract does not assert regulatory approval or medical truth. |
| Nondeterministic part | Semantic comparison of four narrowly enumerated participant-impact dimensions. |
| Validator duty | Independently compare the same sealed parent/child documents and agree on the four consequence-bearing categorical fields. |
| Deterministic derivation | Any `UNKNOWN` => `UNRESOLVED`; else any `MATERIAL` => `RECONSENT_REQUIRED`; else `NO_RECONSENT_REQUIRED`. Subject eligibility is a bounded traversal of assessed version edges. |
| Temporal scope | Documents are immutable snapshots. A subject's confirmation is valid only for the current revision sequence and becomes stale when a child revision is proposed. |

## Roles and trust boundary

- The deployment wallet receives no role and has no privileged method.
- Any reviewer wallet can create a separate study and becomes authority only for that study.
- Creation requires a distinct site wallet. Only that site may record pseudonymous consent artifacts.
- Any wallet may invoke assessment and eligibility confirmation; neither action lets it choose the result.
- Subject identity and signed forms stay off-chain. Only 32-byte commitments are persisted.

## State machine

```text
authority create study + V1 baseline
        |
        v
site records subject consent ----> ELIGIBLE ----> confirmation(V1)
        |                               |
        | authority proposes V2        | confirmation becomes stale
        v                               v
PENDING transition -- consensus --> UNRESOLVED -- retry --> assessed
                                      |                 |
                          REVIEW_INCOMPLETE       +------+------+
                                                  |             |
                                      NO_RECONSENT_REQUIRED   RECONSENT_REQUIRED
                                                  |             |
                                               ELIGIBLE      BLOCKED
                                                                |
                                              site records V2 consent
                                                                |
                                                             ELIGIBLE
```

Only a current, assessed lineage can accept consent. A new revision cannot be appended until the prior edge is resolved, so unresolved evidence cannot be bypassed by creating later versions.

## Why this architecture is distinct

This is a version-graph interlock with lazy per-subject invalidation. It has no sensor stream, time-window aggregation, event queue, escrow, release authority, payout, or binary oracle. Consensus labels a single immutable graph edge; deterministic traversal applies that edge to every subject independently. The consequential write is a revision-bound eligibility confirmation.

## Safety invariants

1. Deployer is not authority by deployment.
2. Authority and site must be different wallets.
3. Only authority-authenticated documents enter a study lineage.
4. Parent must be the current head; document digests cannot repeat in a study.
5. Unknown or malformed semantic evidence fails closed and remains retryable.
6. Model output cannot directly confirm eligibility.
7. A material edge blocks every subject consented before that edge.
8. Only the site can cure a block by recording a fresh, unique consent artifact.
9. Confirmation is scoped to the current revision and automatically goes stale after a proposal.
10. Traversal is bounded by `MAX_REVISIONS = 16`.

## Non-claims

The contract does not prove participant identity, signature validity, clinical correctness, regulator approval, or that the authority uploaded every applicable document. It proves provenance and state transitions inside the declared study boundary.
