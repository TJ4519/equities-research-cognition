# Case A outcome-complete implementation receipt

## 1. Verdict

`PARTIAL_DEPENDENCY`

Packet 005's public/synthetic vertical is outcome-complete on its worker branch:
the focused suites, PostgreSQL guards, real NTM/Codex run, bounded
LibreOfficeDev calculation, restart projection, and rollback checks pass. The
repository-wide classifier still stops on the tracked binary workbook before
it can classify the tree. That defect is assigned to Packet 007 and was not
modified here, so integrated V0 acceptance remains dependent on that branch.

## 2. Exact base, branch, result, and ancestry

- Dispatch head: `dee299679562db02f051997f244868e86d6e0a0e`.
- Authoritative product-code ancestor:
  `1798427cadad65e286e8e124b261dfb31903fec0`.
- Branch: `agent/case-a-outcome-complete-v0`.
- Implementation result commit:
  `cf5685383654c00513825fc451b60221bc0117e9`.
- `git merge-base --is-ancestor 1798427cadad65e286e8e124b261dfb31903fec0
  cf5685383654c00513825fc451b60221bc0117e9` exited 0.
- The dispatch delta before implementation contained only the authorised
  checkpoint, ledger, dispatch receipt, and Packets 005–007.
- The evidence-only commit containing this receipt is reported separately in
  the worker return, avoiding an impossible self-referential commit hash.

## 3. Changed-file and ownership audit

The implementation commit changes exactly 25 Packet 005-owned files; this
receipt is the twenty-sixth owned path. No Packet 006/007 surface, governing
checkpoint/ledger, stale packet, dependency manifest, protected fixture,
deployment surface, or analyst record changed.

```text
prototypes/equities-research-cognition/agents/model_change_v0.md
prototypes/equities-research-cognition/harness/ntm/adapter.py
prototypes/equities-research-cognition/product/campaign/management/commands/seed_model_change_v0_case_a.py
prototypes/equities-research-cognition/product/campaign/migrations/0005_model_change_v0.py
prototypes/equities-research-cognition/product/campaign/migrations/0006_model_change_v0_guards.py
prototypes/equities-research-cognition/product/campaign/model_change/__init__.py
prototypes/equities-research-cognition/product/campaign/model_change/adapter.py
prototypes/equities-research-cognition/product/campaign/model_change/forms.py
prototypes/equities-research-cognition/product/campaign/model_change/projections.py
prototypes/equities-research-cognition/product/campaign/model_change/services.py
prototypes/equities-research-cognition/product/campaign/model_change/urls.py
prototypes/equities-research-cognition/product/campaign/model_change/views.py
prototypes/equities-research-cognition/product/campaign/models.py
prototypes/equities-research-cognition/product/campaign/services.py
prototypes/equities-research-cognition/product/config/settings.py
prototypes/equities-research-cognition/product/config/urls.py
prototypes/equities-research-cognition/product/templates/model_change/episode.html
prototypes/equities-research-cognition/product/templates/model_change/index.html
prototypes/equities-research-cognition/scenarios/adversarial/fixtures/model_change_v0/case_a_10k.txt
prototypes/equities-research-cognition/scenarios/adversarial/fixtures/model_change_v0/case_a_8k.txt
prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_migrations.py
prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_models.py
prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_runtime.py
prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_services.py
prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_ui.py
prototypes/equities-research-cognition/docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md
```

## 4. Canonical records and stable-interface map

The additive schema implements `ResearchJob`, `ModelChangeEpisode`,
`ArtifactManifestVersion`, `ConceptualObjectVersion`, `ObjectDisposition`,
`SourceDocumentVersion`, `SourceAssertion`, `ModelChangeProposal`,
`AdmissibilityDecision`, `CalculationReceipt`, `Amendment`,
`InvalidationEvent`, `ArtifactDisposition`, and `CorrectionRecord`.
`ArtifactVersion` adds nullable candidate parentage and pass authority.

| Contract interface | Implementation symbol |
| --- | --- |
| Begin or resume owned work | `JobService.begin_or_resume` |
| Inspect target and propose meaning | `ObjectService.inspect` |
| Confirm/amend meaning or authorise method | `ObjectService.disposition` |
| Capture exact document bytes | `EvidenceService.capture` |
| Assert a located value | `EvidenceService.assert_value` (`assert_` compatibility alias; `assert` is a Python keyword) |
| Compile immutable work | `WorkCompiler.compile` |
| Parse typed worker output | `ProposalParser.parse` |
| Apply deterministic admission | `AdmissibilityGate.evaluate` |
| Create and calculate child candidate | `CandidateService.create` |
| Record bounded synthetic use | `DispositionService.record` |
| Append amendment and invalidations | `InvalidationService.amend` / `repair_wrong_source` |
| Resume canonical state | `ProjectionService.resume` |
| Seed exact correction example | `CorrectionService.seed` |

Host facts own all identities, bytes, digests, locators, document classes,
closure, adapter facts, calculation evidence, legal transitions, and
invalidations. The worker supplies only the bounded proposal. Human-attributed
records remain separate for meaning, method/source rule, repair, and synthetic
disposition.

## 5. Migrations and SQL guards

- `0005_model_change_v0` is additive: new tables, nullable candidate linkage,
  and the candidate role; it renames, deletes, or backfills nothing.
- `0006_model_change_v0_guards` installs PostgreSQL update/delete refusal on all
  fourteen new canonical tables, append-only protection for model-change work
  orders, and a candidate insert trigger that joins pass, proposal, episode,
  owner, campaign, object, source assertion, parent, manifest, closure, and
  invalidation facts.
- Final isolated fresh database reached `campaign.0006`; PostgreSQL reported
  both `model_change_candidate_guard` and
  `model_change_workorder_append_only`.
- Isolated upgrade first installed the predecessor, inserted legacy campaign
  `e148e296-6f6e-4991-959d-edeadb085756`, then migrated to head. The row title
  remained `Representative legacy row`; `ResearchJob` count remained zero.
- Empty reverse from `0006` to `0004` succeeded.
- Populated reverse exited 1 before destructive operations with
  `refusing destructive model-change reverse while canonical facts exist`.
- Focused migration tests: 3 passed. Direct SQL candidate-without-pass,
  canonical-row update, and model-change work-order rewrite tests all pass by
  observing database refusal.

## 6. Feature flag and legacy compatibility

`MODEL_CHANGE_V0` defaults false and must be explicitly enabled. With the flag
off against populated live data, one episode, one candidate, and one
calculation receipt remained readable through the canonical models; the legacy
`/campaigns/` route and row remained available; model-change projection
returned `FEATURE_DISABLED`; no history was deleted. Existing protocol
launcher tests prove `--search` remains present outside `model_change_v0`.

## 7. Typed protocol, packet, and cognition identity

- Protocol: `model-change-v0/2026-08-17`.
- Frozen protocol SHA-256:
  `e30c45af7a0bdfc7689bc4072cda21d5b42a64ad112859c08352f845a512731f`.
- Work packet: `research-work-order/v1` plus exact episode, object, artifact,
  manifest, assertion, closure, materialised-input, and protocol fields.
- Network policy: `closed_captured_sources`.
- The model-change Codex launcher omits `--search`; existing protocol launchers
  retain it.
- Runtime: NTM 1.0.0, Codex 0.144.6, model `gpt-5.6-sol`, exactly one Codex
  pane. Langfuse was optional and supplied no authority or required trace.
- Final live order:
  `64eb2d61-d443-46df-b565-135333ccead6`, digest
  `f0881b3d554c2c540dccd701b0c3eb316330829bdf9fda61732f3d949e7495bc`,
  closure
  `f82e93ddef4476a91da8cff5a6b7376e6146ccce70808e5535c811790d67c439`.

## 8. Captured sources

Both fixtures say `37,378` USD millions but remain distinct exact captures.

| Class | Artifact SHA-256 | Assertion ID | Assertion SHA-256 |
| --- | --- | --- | --- |
| Captured 8-K earnings release | `c3916adc89f9f2a4952aeb058dd21addb38399e1d85590ccf7c532ae128da2d0` | `c2b370dc-2a08-446b-9900-6629ae619847` | `374775f3b8263912d29f2fbc3afed009ba2cb23a50643739a7482b11ea8802d3` |
| Captured 10-K annual report | `b67bdc1c5169ec181f57946d2afa7daf756a71b6d80e17f818fba5dcc3b81bdf` | `5bcbec92-47a7-4cd9-bb5a-f7b193cfb6d0` | `1e3d99c007b58ea19db6387d9aa5bc8787619a2a564ecf3310eb5cc7e3d30c89` |

The packet named a read-only `spikes/.../minimal_model.xlsx` path that is not
present at the dispatch head. The actual tracked authoritative fixture is
`scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`, SHA-256
`e06961d93384754fd31faf6f14a11a70052722af5be0f3c652c23b859697c98b`.
It was reused read-only; the mismatch is recorded rather than silently widened.

## 9. Admission evidence

- Model-authored 8-K proposal:
  `8100b0ab-15d7-439b-bb3e-5cc8f8dbf5b3`, digest
  `f8add8cfe5216629bc468479dad26b5a02d4bf8dce515ee2cd4e71256d4f481a`.
- Decision `f210cc52-b8db-461f-9e28-f01496d001c6` returned
  `BLOCK_WRONG_DOCUMENT_CLASS` and candidate count was exactly zero.
- Attributed amendment `dc0a8462-dc12-4db2-95b3-e508ceea69be` created
  host-derived 10-K proposal `ad1b3e80-a6a9-47d4-948a-84fbeadff21f` with a new
  closure and exact `PASS` decision
  `aa2ed48b-17aa-437a-af0f-ce89c1c26ede`.
- Separate transfer test proves the same 8-K assertion passes for
  `FY2025_PRELIMINARY_EARNINGS_FLASH_REVENUE`; no global recency, filing, GAAP,
  or 10-K preference rule was introduced.
- Invented ID, wrong digest, stale closure, unsupported structure, cross-owner,
  and invalidated-ancestor tests refuse before mutation.

## 10. Candidate and calculation evidence

- Candidate `6ca1ce36-3937-4d3b-ae53-041d0bb5eed6` is a child of the exact
  starting artifact and is linked to the exact replacement pass.
- Candidate SHA-256:
  `0d95b3336e8f75c3526014e7bf35069d7e6dbbdd854d6b677eb66e1433283d1b`.
- Operation-receipt SHA-256:
  `81ea047f053ff98da0e7c0cd2aad0fa6313360c5bdd9700a5b2089dcc2c8075e`.
- Calculation receipt `98ba6c4d-1220-4ed5-9d8a-997ddfe3c3cb`, digest
  `a6c287eda126e777365adf5cf203e7a44d69dd9bfcd712a23d54ad5cfa9f1a83`.
- Engine identity:
  `soffice:8efdf2c4d54044cdf37ee82e2f240bc550e556c120ace81da3cb831f1a6d5b77`;
  version `LibreOfficeDev 26.8.0.0.alpha0
  2c87e51eeaa2b413ff4ae097b2705eea1995d8e5`.
- Input digest is the unchanged original
  `e06961d93384754fd31faf6f14a11a70052722af5be0f3c652c23b859697c98b`;
  output digest equals the candidate digest.
- `Model!B6`: `0.469475528652782` → `0.488511011110669` under formula
  `B5/B4-1`.
- `Valuation!B5`: `3.2520325203252` → `3.21044464658355` under formula
  `B4/Model!B5`.
- Warnings: none. Formula errors: none. The process ran only through the audited
  explicit calculation grammar in `harness/ntm/adapter.py`, with `shell=False`,
  a pinned binary, isolated profile/environment, bounded arguments, and timeout.

## 11. Amendment, invalidation, disposition, and correction

The source repair appends rather than edits. It creates exact invalidations for
the blocked proposal and decision:

- proposal invalidation digest
  `72a0eaeb5f9d9d48052bfb4a1310982f7651568483e654f318d192fc32c918c8`;
- decision invalidation digest
  `55b6ec4e3dc39b1ff22902d450004581dc44be2a41f9ed6dc5b09fd227b508c8`.

Synthetic disposition `a653c83d-a1d2-44b8-b3ae-e1b96e5cb909` records
`SIMULATE_NAMED_USE`, digest
`cc1ff443b56e4f80121be85a1ab6798fac5915b5d74b6dfa750e7dac8339d7f5`.
Correction seed `5b8a4cc3-f8cc-4224-bf59-ba89b169cc20`, digest
`a6d82d31236d8153c5f959303e28f4e7ed572f3ea2c9fd7c17066118139e0a69`,
joins the block, reason, amendment, replacement, both assertions, candidate,
episode, protocol, and adapter profile. It does not attribute failure or
promote a harness change.

## 12. Restart projection

Restart used only PostgreSQL canonical facts: no NTM pane, terminal state,
Langfuse trace, or process memory was consulted. It recovered candidate
`6ca1ce36-3937-4d3b-ae53-041d0bb5eed6`, disposition
`a653c83d-a1d2-44b8-b3ae-e1b96e5cb909`, two proposals, two decisions, and two
invalidation events. The authenticated HTTP restart returned 200 at the exact
job/episode route and rendered the original, candidate, both consequences,
synthetic disposition, and history.

## 13. Product journey and burden measures

The joined ordinary-language route is `/jobs/<job>/model-change/<episode>/`.
The seeded entry plus five consequential submissions cover meaning, method,
run, filed-report repair/candidate creation, and synthetic disposition. The
rendered page contains no reason code, packet schema, logical-role ID, trace ID,
Casebook term, raw JSON, NTM control, workbench, or source-ID input.

- Final worker launch-to-custody duration: 261.796 seconds.
- Consequential submissions: 5.
- Runtime interruptions in the final run: 0.
- Restart reconstruction errors: 0.
- Scripted synthetic disposition latency after receipt creation: 0.006 seconds;
  this is orchestration evidence, not an analyst-review burden measure.
- Sanitised HTTP rendering was verified through Django's authenticated client.
  No screenshot is claimed; screenshot evidence was not needed to establish
  canonical state and was not substituted for it.

## 14. Commands, tests, warnings, and failures

Commands were run from `prototypes/equities-research-cognition`.

| Evidence | Result |
| --- | --- |
| `uv run python -W error manage.py check --fail-level WARNING` | pass, zero warnings |
| `uv run python manage.py makemigrations --check --dry-run` | pass, no drift |
| `uv run python manage.py showmigrations --plan` | plan recorded; configured development DB was behind and was not used as upgrade evidence |
| `...test_model_change_v0_models -v 2` | 6 passed |
| `...test_model_change_v0_services -v 2` | 5 passed |
| `...test_model_change_v0_runtime -v 2` | 5 passed |
| `...test_model_change_v0_ui -v 2` | 6 passed |
| `...test_model_change_v0_migrations -v 2` | 3 passed |
| All five focused modules together | 25 passed |
| `...test_owned_job_bound_execution -v 1` | 16 passed |
| `...test_workbook_capability_spike -v 1` | 3 passed |
| `uv run python tools/check_boundary.py` | pass |
| `git diff --check` | pass |
| `uv run python tools/classify_loc.py` | expected Packet 007 dependency failure: UTF-8 decode of tracked binary workbook |
| `...test scenarios.adversarial -v 1` | 137 executed; one classifier setup error; 142 discovered |

The first live attempt stopped at Codex repository trust and retained an empty
sealed directory. The second exposed NTM's startup-readiness race and also
retained no admitted output. The bounded repairs add launcher-scoped trust,
wait through startup, and require the exact three output files before completion
can seal. The third and final runs succeeded. Codex reported optional MCP
startup warnings for unavailable local integrations; neither was used and
neither entered authority or artifacts.

## 15. Live NTM/Codex join

- NTM session: `flywheel-ffd2a49673b6488f8aba`.
- Logical role: `997160c5-4857-41bd-9744-ad3a88c899e1`.
- One launch, one tracked send, one worker, exact completion observation.
- Sealed artifacts:
  - `model-change-output.json`: 752 bytes, SHA-256
    `61272835604d191297683daf2f852c9876bd5327bb2e03078ee8441e6def0196`;
  - `run-acknowledgement.json`: 744 bytes, SHA-256
    `e7efcbead8e6d9ead093c7b01e88a279898774c222a40d1e2728dabff60dd7d9`;
  - `artifact-attestation.json`: 556 bytes, SHA-256
    `db05d29fdd605d390210a84054ec553e72724b72c9cc84f2393a96c13163aa34`.
- Typed parsing and deterministic admission occurred only after those bytes
  were sealed, stored, and attested. No raw trace or secret is included here.

## 16. External dependencies

- Packet 007: unresolved. `classify_loc.py` reads the tracked XLSX as UTF-8 and
  fails. Packet 005 did not change classifier code or its tests.
- Packet 006/direct Excel: unresolved and not claimed. This slice calculates
  through a pinned LibreOfficeDev build; it does not execute, automate, or
  claim compatibility with native Excel.

## 17. Rollback evidence

- Predecessor: `dee299679562db02f051997f244868e86d6e0a0e`.
- Migration head: `campaign.0004` predecessor → `campaign.0006` current.
- Flag default: false; explicit live enablement used
  `FLYWHEEL_MODEL_CHANGE_V0=1`.
- Flag-off future entry returns `FEATURE_DISABLED`; new routes return 404.
- Populated tables remain readable and unchanged with the flag off.
- Populated destructive reverse refuses; empty reverse succeeds.
- Stale proposals, decisions, candidates, calculations, and dispositions are
  excluded/refused through exact invalidation tests.
- A retired profile returns `UNSUPPORTED_PROFILE` for future work while the
  existing candidate and calculation receipt remain present.
- Legacy routes and representative legacy rows remain available. No history is
  deleted.

## 18. Unresolved facts and severity

| Fact | Severity | Effect |
| --- | --- | --- |
| Packet 007 binary classifier is not integrated | S2 dependency | Blocks integrated V0 acceptance, not Packet 005 focused behaviour |
| Packet 006 direct-Excel result is absent | Deferred dependency | No Excel execution or compatibility claim |
| Packet named a missing spike fixture path | Documentation mismatch | Actual tracked bounded fixture is explicitly recorded and read-only |
| No cold analyst observation or screenshot | Product-evidence gap | No usability, review-burden, or product-fit inference |
| No tenant model or production security review | Out of scope | Only authenticated owner isolation is proven |

## 19. S1/S2 closure and claim ceiling

| Closure | Level | Status | Evidence |
| --- | --- | --- | --- |
| Owner/job/episode/campaign custody | S1 | Closed for this slice | ORM isolation, no cross-owner disclosure, SQL candidate join |
| Candidate only after exact current pass | S1 | Closed | ORM clean, PostgreSQL trigger, zero-candidate block, invalidation refusal |
| Closed captured-source execution | S1 | Closed | no `--search`, exact materialisation, acknowledgement, sealed attestation |
| Process boundary | S1 | Closed | NTM and calculation grammars only; `shell=False`; boundary checker passes |
| Immutable history and rollback | S1 | Closed | append-only ORM/SQL, invalidation, populated reverse refusal, flag-off read |
| Source-to-target decision | S2 | Closed mechanically | annual 8-K block, annual 10-K pass, preliminary 8-K pass |
| Workbook consequence path | S2 | Closed mechanically | unchanged parent, one target patch, LibreOfficeDev, two consequences |
| Ordinary restartable interaction | S2 | Closed mechanically | five actions, authenticated 200 restart, canonical history projection |
| Integrated LOC classifier | S2 dependency | Open | Packet 007 binary decode failure |

The claim ceiling is one runnable public/synthetic Case A vertical on the worker
branch with the exact joined mechanics and evidence above. It does not establish
independent verification, integration, analyst usefulness, reduced burden,
professional correctness, permission to rely, arbitrary workbook support,
structural modelling, native Excel compatibility, tenant security, investment
quality, production readiness, deployment readiness, or harness promotion.

## 20. Recommended PRO disposition

Accept the Packet 005 implementation as the outcome-complete candidate and
retain the `PARTIAL_DEPENDENCY` programme verdict until Packet 007 is reconciled.
The strongest acceptance reason is the real joined worker-to-block-to-repair-to-
calculated-candidate-to-restart evidence under exact custody. The strongest
repair reason is that the repository-wide classifier still cannot traverse the
tracked binary fixture. Kill this slice only if independent verification finds
a candidate-after-pass or closed-source custody bypass; current hostile tests
and live evidence found neither.
