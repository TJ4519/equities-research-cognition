# Case A Authority and Recovery Repair 1 Receipt

Status: **candidate returned for independent verification; not merged or integrated**.

Verdict: `PASS_FOR_INDEPENDENT_VERIFICATION`.

This receipt records Worker Packet 008 only. It does not declare verified V0,
analyst validation, product readiness, native Excel compatibility, deployment
readiness, or harness promotion.

## 1. Basis and commits

- Required starting branch: `agent/case-a-authority-recovery-repair-v1`.
- Exact starting commit:
  `07db2a6b1f0e4b9f8aaca4f2bc5e5cb3192e1e43`.
- Rejected evidence ancestor:
  `3d5c3157f91361bee120c10ecd4bddfda6e16296`.
- Exact implementation commit:
  `e668d01bdc7706299f66ee845ae62c956046567a`.
- The final evidence-only head contains this receipt. Its exact SHA is returned
  with the worker handoff because a Git commit cannot contain its own SHA.
- Governing repair contract:
  `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`.
- Governing checkpoint and ledger were read from
  `origin/agent/pro-grounding` at
  `6be6f6a181444a4600fa5bddc120fed845794f9e` and were not copied or modified.

The checkout matched the required base, tracked the exact repair branch, and
was clean before work. The initial delta from the rejected evidence head
contained only the bounded repair contract and Packet 008.

## 2. Pre-edit counterexamples R1-R6

All six counterexamples were reproduced before the first edit against the
unchanged rejected product surfaces at the required repair base. PostgreSQL was
used for the database attacks.

### R1 — forged database pass and orphan candidate

Command shape:

```sh
FLYWHEEL_MODEL_CHANGE_V0=1 uv run python manage.py shell
```

The reproduction compiled an annual-target work order, parsed the captured
8-K proposal, ran the application gate, and then used `django.db.connection`
raw SQL to insert an attacker-authored decision followed by a candidate with no
calculation receipt.

Preserved result:

```text
application outcome=BLOCK reason=BLOCK_WRONG_DOCUMENT_CLASS
direct SQL validator=attacker/v0 outcome=PASS
candidate committed=true receipt_count=0
```

### R2 — repeated repair

Command shape:

```sh
FLYWHEEL_MODEL_CHANGE_V0=1 uv run python manage.py shell
```

The rejected filed-report mutation path was called twice against the same
historical block.

Preserved result:

```text
amendments=2 replacement_proposals=2 decisions=2
```

### R3 — calculation failure dead end

Command shape:

```sh
FLYWHEEL_MODEL_CHANGE_V0=1 uv run python manage.py shell
```

`adapter.apply` was forced to raise `AdapterRejected` after the 10-K repair
began, and the authenticated ordinary POST path was exercised.

Preserved result:

```text
HTTP status=500
current decision=PASS
candidate=None calculation_receipt=None
retry POST=409
ordinary retry available=false
```

### R4 — refusal loss

Command shape:

```sh
FLYWHEEL_MODEL_CHANGE_V0=1 uv run python manage.py shell
```

A valid `model-change-refusal/v0` was returned through the worker path and the
authenticated page was reconstructed from PostgreSQL.

Preserved result:

```text
view redirect=302
proposal_count=0
restart refusal present=false
restart retry action present=false
```

### R5 — classifier evidence mismatch

Commands:

```sh
git switch --detach 3d5c3157f91361bee120c10ecd4bddfda6e16296
cd prototypes/equities-research-cognition
uv run python tools/classify_loc.py
git switch agent/case-a-authority-recovery-repair-v1
```

Preserved first failure:

```text
unclassified cognition-package surface: docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md
```

The classifier was not changed or waived. Packet 009 retains ownership.

### R6 — candidate-review evidence gap

Command shape:

```sh
FLYWHEEL_MODEL_CHANGE_V0=1 uv run python manage.py shell
```

The authenticated candidate page was rendered and inspected. The candidate
section lacked the exact 10-K filename and locator, original and candidate
digests with filenames, the named synthetic use, an explicit unchanged-original
statement, and the equal-value annual-document explanation.

No counterexample diverged from Packet 008.

## 3. Bounded repair

Migration `campaign.0007_model_change_v0_repair_1` installs
`campaign_model_change_expected_admission_v1(proposal uuid)`. It derives the
validator, outcome, reason, and closure from canonical PostgreSQL rows. It is
target-specific: the annual target blocks the earnings-release 8-K and passes
the filed annual 10-K; the preliminary earnings-flash target passes the 8-K.

The migration also installs:

- `model_change_decision_guard_v1`, rejecting any inserted validator, outcome,
  reason, or closure that differs from the canonical function;
- a replacement `model_change_candidate_guard`, which recomputes the canonical
  pass and verifies current proposal, episode, campaign, parent, digest,
  manifest, object, assertion, and invalidation custody;
- `model_change_receipt_guard_v1`, rejecting receipt/pass/candidate/episode/
  manifest/closure/input/output/formula mismatches;
- deferred `model_change_candidate_complete_v1`, requiring one exact receipt
  for every candidate at transaction commit;
- one-candidate-per-pass and one-filed-repair-per-block uniqueness;
- `model_change_outcome_guard_v1`, binding runtime/refusal outcomes to an exact
  work order and calculation outcomes to the exact current wrong-source block;
  and
- append-only outcome enforcement plus the inherited append-only guards for
  amendments, replacement proposals, decisions, receipts, invalidations,
  dispositions, and corrections.

Application admission calls the same PostgreSQL function. One repair service
owns locking, currentness, deterministic repair identity, amendment,
replacement, pass, adapter work, candidate, receipt, and invalidation in one
transaction. Identical sequential or concurrent requests return the same exact
chain; conflicting or stale requests refuse.

Adapter failure rolls the transaction back before appending a
`CALCULATION_FAILURE`. Runtime failures and bounded refusals append exact
outcomes. Restart projects one legal next action. Model-change artifact
collection targets only the current finalized attempt, so a failed predecessor
and its output root remain evidence without blocking a successor retry.

## 4. Migration evidence

The final clean-database command used a separately named PostgreSQL database so
the pre-existing unrecorded local development tables remained untouched:

```sh
FLYWHEEL_DB_NAME=flywheel_case_a_repair_1_20260818 \
  uv run python manage.py migrate
```

Result: zero through `campaign.0007_model_change_v0_repair_1` and all other
project migrations applied successfully. `showmigrations --plan` reported every
entry through 0007 as `[X]`.

Migration-hostile tests prove:

- 0004 legacy campaign rows survive upgrade through 0007;
- a complete valid seeded V0 episode at 0006 preserves exact episode and
  starting-artifact digests;
- a false `attacker/v0` pass plus orphan candidate at 0006 makes 0007 fail with
  `refusing model-change repair migration with forged or orphaned candidate authority`;
- a forged outcome insert is rejected, while a valid runtime outcome is
  direct-SQL update/delete protected;
- an empty reverse to 0004 succeeds; and
- populated reverse to 0006 refuses before destructive operations while the
  canonical tables and rows remain present.

No migration history was rewritten. Migrations 0005 and 0006 are unchanged.

## 5. Hostile and regression evidence

Final commands from `prototypes/equities-research-cognition`:

```sh
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
FLYWHEEL_DB_NAME=flywheel_case_a_repair_1_20260818 \
  uv run python manage.py showmigrations --plan
uv run python -W error manage.py test \
  scenarios.adversarial.test_model_change_v0_models \
  scenarios.adversarial.test_model_change_v0_services \
  scenarios.adversarial.test_model_change_v0_runtime \
  scenarios.adversarial.test_model_change_v0_ui \
  scenarios.adversarial.test_model_change_v0_migrations \
  scenarios.adversarial.test_model_change_v0_repair_1 -v 2
uv run python -W error manage.py test \
  scenarios.adversarial.test_owned_job_bound_execution \
  scenarios.adversarial.test_workbook_capability_spike -v 1
uv run python -W error manage.py test scenarios.adversarial -v 1
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
git diff --check
```

Results:

- system check: pass, zero warnings;
- migration drift: none;
- focused repair floor: **44/44 passed**;
- adjacent owned-job and workbook-capability floor: **19/19 passed**;
- complete adversarial discovery: 162 tests found, 157 executed; the sole setup
  error is Packet 009's expected classifier dependency, so five architecture
  budget methods do not execute;
- runtime module alone after the live-found retry repair: **9/9 passed**;
- boundary checker: pass;
- `git diff --check`: pass; and
- classifier first failure remains exactly
  `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`.

Raw-SQL hostile coverage includes false pass, false validator, false reason,
false closure, stale proposal, candidate for a block, orphan candidate at
commit, wrong receipt pass/manifest/candidate/episode/closure/input/output/
formula state, duplicate candidate, outcome custody, and append-only repair
relationships. Legal annual 10-K and preliminary 8-K controls pass.

Repair coverage includes sequential and concurrent convergence, conflicting
assertion/profile/idempotency, stale block refusal, exact duplicate candidate
return, apply/calculate/compare rollback, formula-error non-dispositionability,
launch/readiness/collection failure, bounded refusal, stale worker output,
successor collection, restart, and feature-flag rollback.

## 6. Fresh real joined NTM/Codex episode

The live database contains an entirely fresh success episode. No prior worker
output or canonical row was reused.

- NTM: `1.14.0`, commit `6ffd0a06eb73a698ded0ade2df14185417869eae`.
- Codex CLI: `0.144.6`.
- Model: `gpt-5.6-sol`.
- Network policy: `closed_captured_sources`; the launcher omitted search.
- NTM session: `flywheel-c0866051ba524a6d8809`.
- Observed worker population during execution: one Codex pane, zero other
  agents.
- Job: `ce35586e-208c-4c7c-b40e-26aa6a4337ad`.
- Episode: `52295d86-ed1e-49d9-8d04-98b6798b7380`, digest
  `a997f0327c155cd7a387dde35c184ad53165383fa04397252bc5c266b379ea6f`.
- Work order: `2dc8b64c-ceb9-44fe-a6a4-ed44f09fb642`, digest
  `ff4cafa98400614cbd86362763caf2ad8c89ab6d394707630faa1e8993ee8861`.
- Logical role: `af37f0fa-c80b-4383-8347-1f17ad6f6c39`.
- Closure:
  `231d1416a1c82336ed6a48fcaf173dbf719820523b31ab651181422395eaba13`.
- Launch-to-custody time: 339.814 seconds.
- One launch and one tracked send completed. Intermediate non-success status
  polls were retained; the final completion observation succeeded.

Sealed artifacts:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `model-change-output.json` | 751 | `e9af85b1899818c379a6ad80987fccbb36a5e7d77101a92e0434c00a53c15a87` |
| `run-acknowledgement.json` | 743 | `607e7072e66aac548514c7d367ad812e2012a5efd772062df6f5d80c06c9781d` |
| `artifact-attestation.json` | 555 | `7b89e7923151716d4c60048a14ad6677702ec32060ad64b907c7bf637740b36f` |

Captured equal-value sources:

| Class | Filename | Artifact SHA-256 | Assertion | Assertion SHA-256 |
| --- | --- | --- | --- | --- |
| 8-K earnings release | `case_a_8k.txt` | `c3916adc89f9f2a4952aeb058dd21addb38399e1d85590ccf7c532ae128da2d0` | `b43fb01e-94b7-4b21-831c-5d9b77329e39` | `e4a87c198e30802ea6810694fd8e86e1526cae507404038b9bf121fbb6a5dee9` |
| filed annual 10-K | `case_a_10k.txt` | `b67bdc1c5169ec181f57946d2afa7daf756a71b6d80e17f818fba5dcc3b81bdf` | `1edfd1ab-2b01-457f-9e2a-ccd30e18e069` | `3fa537784ad94a6eb3abc83c812a2795f14083d9ad63e5d701e6b8de5fdb027d` |

Canonical chain:

- model proposal `1bbaf17c-3d9c-4bc2-9986-be6a8daac9d9`, digest
  `af7fa09e10504548ebca20f9746b479d8ffe69b8247bb5705d856525a46d778d`;
- PostgreSQL decision `b2a30a4a-02ab-4250-b3fa-0bbf32d91772`, digest
  `517326dd1dfec8eb2af640cdafe179ba33020868083199479eb4ade6f3b9aebd`,
  `BLOCK_WRONG_DOCUMENT_CLASS`;
- filed-report amendment `e88ec6ba-a99b-4a7c-99e8-0108e388e3dd`, digest
  `48716c35b4389f5604d58f7156ed63f68c7cedf56f9d486d1a5a3d09f35fec3c`;
- replacement proposal `14937e2f-3510-40a6-b2a6-6ef083eb5441`, digest
  `ec57300c3319e16c153b0689feeac32b6d7d9f2c9271dd547c63efd16ed3333f`;
- replacement closure
  `1ce69bc3b49f2accac129461eaca05f5d988e5ced28f3d34e50265833cb337b8`;
- pass `d6b970cd-ae1b-4c56-a87e-09edd6017608`, digest
  `fcc5aa40e17da929629a24d0f61b41bd00e802cc2050f93f930fe4b48261b6fc`;
- candidate `75445955-6a62-493a-b165-54708a1e15f8`, SHA-256
  `a2fc4ceafa7eb13c30e921b7d21725a9106a311b59e442f13ffefe4a70db193b`;
- exact unchanged parent SHA-256
  `e06961d93384754fd31faf6f14a11a70052722af5be0f3c652c23b859697c98b`;
- operation-receipt digest
  `f8e4e4602a7ad76e9128da54d9e5c63ba1b828be14beeecbe82234464760394a`;
- calculation receipt `5a855ea8-cab7-40bb-9033-d9f94db3ee71`, digest
  `baa1e1f1f97448ed982e51dfcc9ba4caba3fbb47267d2fe6dc4885bef8a3f0e1`;
- synthetic disposition `37833f2f-d27a-472f-8fdf-b1af7d301b9a`, digest
  `d4a35d1d59c9af9488fe5b9aa6d6ea161649859b1c417908edd4d8a06d602366`;
  and
- correction seed `cd057173-f277-4ac2-a885-d9e33d4426be`, digest
  `710495f1df79393e0ef7c7767434bbce9e4926b88ffd558bfa2aef70db9ee965`.

The engine was
`soffice:8efdf2c4d54044cdf37ee82e2f240bc550e556c120ace81da3cb831f1a6d5b77`,
LibreOfficeDev `26.8.0.0.alpha0 2c87e51eeaa2b413ff4ae097b2705eea1995d8e5`.
Warnings and formula errors were empty. The two consequences were:

- `Model!B6`: `0.469475528652782` to `0.488511011110669`;
- `Valuation!B5`: `3.2520325203252` to `3.21044464658355`.

After the NTM session was stopped, PostgreSQL-only restart recovered the exact
candidate and disposition. The authenticated route returned 200 and contained
the complete review evidence.

## 7. Separate recoverable-failure episode

Episode `e692e015-5401-4196-a1ab-d9f322d47f17`, digest
`ad915d152994f472581834e1838a3c2e47cd514b1316520f880e11e7671707be`,
used session `flywheel-b4680f029b9b46bebd15`.

The forced pinned-control launch failure created no proposal or candidate and
persisted:

- first order `6ca39904-cb7d-4bee-8632-5f2c6ab92c1d`, digest
  `06fe3b426f6e0dc3a7a62148c072ad9fc426a535d0b4b88eb141648482a0ef3b`;
- runtime outcome `ca568faa-de60-41de-9f23-a067ea0f9f9b`, digest
  `8a2872835f9067ee1b62dbef4e5116c1a48e2d944d81af1e8bb1d14d1ab031aa`;
- restart action `RETRY_WORK`.

The first real successor produced exact files but exposed the rejected shared
collector's predecessor-output-root blockage. It became a second retained
runtime outcome, `1050164b-c1ba-4d8e-b820-abc4185a1f25`, digest
`aa69acffa223abe1acffbdb0db6df612ac27fd1e19720f82f7defb17085a6f1e`.
The bounded current-attempt collector repair was then regression-tested and a
second successor completed:

- recovered order `cad58a37-1673-4b10-b0c7-a4a4664b15d2`, digest
  `84d152cf23b9c2a11276262cc0220f7b940bda78eba896634baa2db1ed08cf32`;
- closure
  `6ada738ad8c913d57f44df98d9fd842d8e4945fc3e65e221f3459deb75578391`;
- model proposal `3884b94c-6d96-4bf6-be55-ff36032c063f`, digest
  `ac1cb81614d2a85354a5546993273e9010111feeaf5b7387bfd4848adabd0ced`;
- canonical block `f118aa8e-a517-41ff-bba9-fea3086e235a`, digest
  `42cf28172c2888c3cc001284393852c5a1cbe666bdcc5e1dd4fda9e1340006af`;
- sealed output/acknowledgement/attestation SHA-256 values
  `e7b49685086ea323cfce61944903514f7ae8a62287cce51aa5218268704ca3ab`,
  `c3f1bdf646e7267db7558a22697ba1af7fbbc48d3337074daef0e84790e2bbc0`,
  and `4d1819a6d39e9916679d87d81979f76b827071db4c911384f0fcc7bdda739893`.

Restart recovered the block, selected no stale technical outcome, retained both
prior outcomes in history, and exposed the ordinary filed-report action. The
session was stopped.

## 8. UI and rollback evidence

Authenticated response assertions require and pass for:

- exact 10-K issuer, filing date, filename, locator, value, and unit;
- original and candidate filenames and SHA-256 values;
- the named synthetic use;
- the explicit unchanged-original statement;
- the equal numeric value but wrong annual-document explanation;
- the target change and exactly two declared consequences;
- adapter profile, engine identity/version, warnings, and formula errors; and
- ordinary runtime, refusal, calculation-failure, and retry language.

Assertions reject `USE_CANDIDATE`, approval or reliance language, raw reason
codes, raw JSON/schema fields, source-ID inputs, NTM controls, trace IDs, and
Casebook vocabulary. Disposition remains exactly `SIMULATE_NAMED_USE`,
`REJECT`, or `REWORK`.

Restart is exercised after block, runtime failure, refusal, calculation
failure, successful repair, disposition, and invalidation. With the feature
flag off against the live database, counts remained unchanged at two episodes,
one candidate, one calculation receipt, and two outcomes; projection returned
`FEATURE_DISABLED`. Populated reverse refuses and empty reverse succeeds.

## 9. Exact changed files

- `docs/pro/evidence/CASE_A_REPAIR_1_RECEIPT.md`
- `prototypes/equities-research-cognition/product/campaign/migrations/0007_model_change_v0_repair_1.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/forms.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/projections.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/services.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/views.py`
- `prototypes/equities-research-cognition/product/campaign/models.py`
- `prototypes/equities-research-cognition/product/templates/model_change/episode.html`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_migrations.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_repair_1.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_runtime.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_services.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_ui.py`

No prompt, skill, harness, fixture, classifier, direct-Excel, governing,
deployment, issue, PR, ledger, checkpoint, or rejected migration changed.

## 10. Unresolved facts and claim ceiling

- Packet 009's classifier dependency remains open and is the exact first
  complete-suite failure.
- Direct Excel remains suspended and unclaimed.
- LibreOfficeDev is evidence for one bounded profile only.
- No cold analyst observation was performed, so workflow validity, usability,
  review burden, and analyst value remain unknown.
- No harness failure attribution, intervention, evaluation, promotion, or
  release object was created. The correction is one seed only.

The claim ceiling is one reviewable public/synthetic Case A repair candidate on
the worker branch: canonical PostgreSQL admission, guarded and atomic
candidate/receipt repair, recoverable runtime/refusal/calculation states,
complete ordinary-language candidate evidence, restart/rollback, and fresh
real worker evidence. Independent verification, integration, analyst
validation, investment correctness, arbitrary workbook support, native Excel,
tenant security, production readiness, deployment, and harness promotion are
not established.
