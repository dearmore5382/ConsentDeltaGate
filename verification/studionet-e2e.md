# Studionet E2E evidence

Contract: [`0xC20f...dEc2`](https://explorer-studio.genlayer.com/address/0xC20fCbfE9fCF97624ED45cd17cF3Ec98cA82dEc2)

- Source parity: **PASS** (`8be48ff7d3d6036f45e47a67e995659922bb4e7d7491e03e86f6485dd78a52de`)
- Authority: `0x736A168247e3f0C52F7907c9a8fDac572DF9c8bB`
- Trial site: `0xA63DE24e30C88FB1019E8956654730316e36eDBE`
- Deployment wallet: deployment only; it is not stored as a role
- All 16 recorded writes: **FINALIZED / MAJORITY_AGREE**

## Lifecycle proof

1. Same-wallet role creation rejected: [`INVALID_STUDY`](https://explorer-studio.genlayer.com/tx/0xadddfa3cef52737fe7e2232b0be5f936bb5815239a17ccd6c0729ffbf496986f).
2. Authority created study 1: [`create_study`](https://explorer-studio.genlayer.com/tx/0xf160b1b77406ca0088d480678793667558f0c9c286da926ce96dc45079f20542).
3. Wrong wallet rejected: [`SITE_ONLY`](https://explorer-studio.genlayer.com/tx/0x08750ec622f64860e82ace6a99c2a04ad48521f81f3a2602637285802fd3dab7).
4. Wrong revision rejected: [`CONSENT_MUST_TARGET_CURRENT`](https://explorer-studio.genlayer.com/tx/0xa4e65539c484549ccb77e5da7d3a6c71e373cad59f5a4dd9474214ce94917cd0).
5. Site recorded baseline consent: [`CONSENT_RECORDED`](https://explorer-studio.genlayer.com/tx/0x1ce603e0988ab94ce543870f2aaa7b5d13053af56ec660d9913d4a0ae06e48a0).
6. Baseline eligibility confirmed: [`ELIGIBILITY_CONFIRMED`](https://explorer-studio.genlayer.com/tx/0xdb2a94afd367ca8ce6d2eaf1f73e27455182e37e9fd8fa84abfc53c28c190e1e).
7. Authority proposed material revision 2: [`propose_revision`](https://explorer-studio.genlayer.com/tx/0xc75dd02d9d60591fa10dbe0313e7f318d80ae0dc0df8a9d9cb41be183118a7c1).
8. Before assessment, confirmation failed closed: [`REVIEW_INCOMPLETE`](https://explorer-studio.genlayer.com/tx/0x93629004923579b34c3a9e94726e97b714a70b9c275c7c48c5cdf00d8f085c05).
9. Site could not impersonate authority: [`AUTHORITY_ONLY`](https://explorer-studio.genlayer.com/tx/0x7690aa7e96dd293e7578c5e899fef1f4201409b0a69a0cc8381652042a8d9020).
10. Genuine nondeterministic consensus classified the new cardiac risk: [`RECONSENT_REQUIRED`](https://explorer-studio.genlayer.com/tx/0x79e42c7a9c61d68cb8042c79d2d557c2facf0ff598259ef2d3126c4342813a3b).
11. Deterministic consequence blocked the subject: [`BLOCKED_PENDING_RECONSENT`](https://explorer-studio.genlayer.com/tx/0xe561f61a8009c965e82cf5a62514b33c73b49d919a60a76f7d3c13d0330346c3).
12. Reusing the V1 artifact was rejected: [`ARTIFACT_ALREADY_USED`](https://explorer-studio.genlayer.com/tx/0xd2572dd848c72274baa1c5ea6cd0a9a49abb1330c474497ec2c67a22dab28d2e).
13. Site recorded a fresh V2 consent: [`CONSENT_RECORDED`](https://explorer-studio.genlayer.com/tx/0x64826cfc177880aad4345fbc41e49133ab78bcac4b845e1f8e5227d8affffeaf).
14. Eligibility was restored and confirmed: [`ELIGIBILITY_CONFIRMED`](https://explorer-studio.genlayer.com/tx/0xf48a517b4cb8ff9884304c1e08658ce580169d901aa5ee2e59ab6eaccc1751ed).
15. Authority closed the study: [`STUDY_CLOSED`](https://explorer-studio.genlayer.com/tx/0x8b4753181d9cefdf2e41e8033798974a54287abd9946a76fb4805d363bdb18f5).
16. A post-close write was rejected: [`STUDY_NOT_ACTIVE`](https://explorer-studio.genlayer.com/tx/0x25792d64d969b7bbc17da42986516552b6bc5a929380f5e589cd77ecaf11df4d).

## Final audited state

- Study: `CLOSED`, current sequence `1`.
- Revision: `ASSESSED`, `risk_change=MATERIAL`, outcome `RECONSENT_REQUIRED`, citations `RISK-1` in both snapshots.
- Subject: `ELIGIBLE`, confirmed for current revision, `reconsent_count=1`.

The full arguments, receipts and post-state readbacks are preserved in [`live-0xc20...json`](live-0xc20fcbfe9fcf97624ed45cd17cf3ec98ca82dec2.json).
