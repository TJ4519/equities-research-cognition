# Local-first architecture

Status: architectural direction for plan review. Component boundaries remain open to revision. No dependency choice in this document is implementation authority.

## The product runs in an analyst’s workspace

The first analyst should be able to work through an approved terminal agent inside a configured directory.

The directory should contain the analyst-visible methods, plans, artifacts, and episode views. A local service should own canonical identity, exact source and artifact bytes, grants, context construction, and chronology.

The terminal agent should be replaceable. Claude Code, Codex, Pi, or another compatible harness may act as the research lead. The workspace should continue to function when the chosen harness changes.

The web application should remain optional in the first product. A later web view may display shared work, exceptions, decisions, schedules, and audit. It should read and mutate the same canonical state through supported APIs.

## Working shape

```text
analyst
  |
  v
terminal agent with installed research skills
  |
  +--> local CLI and MCP tools
          |
          v
      local research service
          |
          +--> canonical SQLite state
          +--> content-addressed source and artifact store
          +--> context builder
          +--> method and skill registry
          +--> runtime adapters
          +--> native artifact adapters
          +--> local search and retrieval
          +--> replay and evaluation engine
          +--> optional Langfuse exporter
          |
          v
      replaceable child agent and tool processes

optional shared service
  +--> team identity and roles
  +--> licensed connectors
  +--> schedules and monitoring
  +--> synchronisation
  +--> shared evaluation runs
  +--> controlled method release
  +--> administrative audit
```

## Workspace directory

A first directory may resemble:

```text
research-workspace/
    AGENTS.md
    README.md
    workspace.toml

    methods/
        research-start/
        purpose-bound-deep-research/
        management-language-compare/
        statistical-analysis/
        model-inspect/
        model-update/
        challenge/
        replay/

    policies/
        source-use/
        artifact-use/
        memory/
        retention/

    perspectives/
        rendered-current-views/

    episodes/
        EP-2026-MU-Q4/
            request.md
            commission.md
            current-state.md
            decisions.md
            outputs/
            replay.md

    artifacts/
        models/
        notes/
        charts/
        data/

    evaluations/
        manifests/
        expected-views/

    .research/
        workspace.db
        objects/
        contexts/
        runs/
        indexes/
        logs/
        locks/
```

Human-readable files should help agents and people inspect the work. The local database and content-addressed objects should remain canonical.

Private source bytes, provider tokens, raw terminal histories, and large native artifacts should not be committed to Git by default.

Git should version:

- workspace instructions;
- methods and skills;
- policy definitions;
- public or synthetic evaluation manifests;
- schema migrations;
- code;
- redacted plans; and
- generated human-readable views when policy permits.

## The research lead

The terminal agent acts as a research lead.

The lead may:

- preserve the user’s exact request;
- inspect the workspace index;
- propose an interpretation;
- ask for material corrections;
- propose a plan;
- invoke installed methods;
- start bounded child work;
- inspect results;
- render useful outputs;
- propose corrections and memory entries; and
- explain the state in ordinary language.

The lead may not:

- invent source identity;
- grant itself source rights;
- add evidence to a context after the context builder seals it;
- confirm a professional object when no prior authority covers it;
- apply unsupported artifact operations;
- mark its own output relied upon;
- promote its own method; or
- write its own conclusion into active memory without a grant.

The term “God agent” should not enter code or product language. The lead coordinates work while remaining subordinate to the local service and analyst authority.

## Skills

Skills provide agent-readable procedures.

A skill should specify:

- trigger conditions;
- professional purpose;
- local-service calls;
- required reads;
- permitted outputs;
- expected user interaction;
- refusal conditions;
- common mistakes;
- audit records; and
- examples.

A skill may invoke several local tools. It should not implement its own hidden state store.

A first skill family may include:

### `research-start`

Preserve the request, recover likely prior state, propose the commission, and obtain correction where needed.

### `research-resume`

Reconstruct one active episode from canonical objects rather than terminal history.

### `source-capture`

Capture exact source material through an approved route and return source identities.

### `purpose-bound-deep-research`

Plan and perform cited research under declared evidence-use rules and exact contexts.

### `management-language-compare`

Compare exact statements across periods, speakers, and source types while preserving contradiction.

### `statistical-analysis`

Run a declared calculation over an exact dataset and retain code, environment, diagnostics, and interpretation.

### `model-inspect`

Recover structural workbook facts and propose professional-object mappings.

### `model-update`

Propose admitted operations against exact professional objects and create a candidate descendant through a supported adapter.

### `challenge`

Attack one named result from a fresh context with a declared inspection boundary.

### `research-correct`

Apply an attributed amendment to current work and create a candidate evaluation case.

### `research-inspect`

Explain sources, contexts, derivations, artifacts, decisions, and unresolved matters.

### `research-replay`

Run a baseline or counterfactual replay and compare the result.

## The local CLI

The CLI should work without a terminal agent. It provides a stable interface for agents, people, tests, and automation.

A possible command surface is:

```text
research init
research doctor
research status

research start
research resume <episode>
research show <object>
research search <query>

research source capture <path-or-url>
research source inspect <source>
research assertion propose <source>
research evidence decide <assertion> --for <object> --use <purpose>

research context build <action>
research context inspect <context>

research run <method> --episode <episode>
research run inspect <run>

research artifact inspect <artifact>
research artifact diff <parent> <candidate>
research artifact open <artifact>

research decide <object>
research correct <object>
research memory propose <object>

research explain <claim-or-artifact>
research lineage <object>
research replay <case>
research compare <baseline> <candidate>
research verify <proof-pack>
```

The first release should implement a much smaller coherent subset. The full surface helps test whether component boundaries are complete.

Every command should support machine-readable output. Human-readable terminal views should remain concise.

## MCP surface

A local MCP server may expose the same operations to terminal agents.

The MCP interface should favour a few composable tools rather than dozens of thin aliases.

Possible tools include:

- `workspace_get_state`;
- `commission_propose`;
- `commission_confirm`;
- `source_capture`;
- `source_search`;
- `evidence_use_propose`;
- `context_build`;
- `method_run`;
- `artifact_propose_operation`;
- `decision_record`;
- `correction_record`;
- `lineage_explain`;
- `replay_run`; and
- `evaluation_compare`.

Write tools should require exact object identifiers and expected versions. The service should reject stale writes.

A tool description may teach the agent correct use. Host checks must enforce known invalid states.

## Canonical local state

A local SQLite database is the leading first choice because it provides transactions, relations, migrations, search integration, and portable backup without requiring a server.

The decision remains subject to review. The design should support later PostgreSQL synchronisation without treating the local store as a disposable cache.

The database should own:

- workspace and mandate identity;
- actors and local roles;
- episodes;
- perspectives;
- subjects;
- commissions;
- source versions and assertions;
- entitlement and policy references;
- professional objects and artifact bindings;
- evidence-use decisions;
- context builds;
- methods and skills;
- runs and derivations;
- claims, values, and proposals;
- artifact versions and operations;
- grants and decisions;
- corrections;
- active memory;
- evaluation cases;
- replay runs; and
- synchronisation state.

Append-only history should be used where later work must reconstruct what existed at a previous cutoff. Mutable convenience indexes may be rebuilt from the append-only objects.

## Content-addressed objects

Large and sensitive bytes should live in a content-addressed store beneath `.research/objects/` or an approved external store.

An object reference should record:

- digest;
- media type;
- size;
- encryption state;
- storage location;
- retention rule;
- source or artifact relation; and
- verification time.

The store should protect against path traversal, symlink substitution, partial writes, and silent mutation.

Atomic writes should use a temporary file, digest verification, fsync where required, and rename into the content-addressed path.

A licence may permit transient access but prohibit retention. In that case, the source record should preserve identity, access route, permitted uses, and a lawful locator without pretending retained bytes exist.

## Context builder

The context builder is the central service.

It receives:

- confirmed commission;
- action specification;
- prior perspective;
- candidate evidence;
- evidence-use decisions;
- method version;
- skill version;
- artifact inputs;
- model and tool policy;
- budget; and
- evidence cutoff.

It returns a sealed context build.

A context build should include:

```text
instruction.md
commission.json
context-manifest.json
prior-state/
evidence/
artifacts/
methods/
output/
```

The builder should:

1. resolve exact object versions;
2. evaluate deterministic grants and policy;
3. materialise only the permitted population;
4. record excluded objects and reasons;
5. freeze method and skill versions;
6. create the output root;
7. hash the manifest;
8. apply file and tool restrictions; and
9. issue a context identity.

The child process should not be able to add new evidence to the manifest. A search-capable action should use a capture tool that returns new source identities to the host. The host may then construct another context or extend work through an explicit transition.

## Context economy

The research lead should carry a thin index rather than every source and artifact.

The index may include:

- active episodes;
- current confirmed commissions;
- relevant perspectives;
- important artifacts;
- open decisions;
- recent corrections;
- available methods; and
- concise search handles.

The local search system should retrieve candidate objects by subject, time, professional object, source, decision, and semantic similarity.

Retrieval should return references and compact descriptions first. The lead or a skill should request exact material only when the work requires it.

Child contexts should contain the minimum complete population for one consequential act. Minimum should not mean small at the expense of missing material. The context manifest should explain inclusion.

Persistent sessions may retain useful branch-local evidence. A checkpoint should still write claims, questions, sources, partial artifacts, and next work into canonical state. Session persistence should never be the only memory.

## Runtime adapters

A runtime adapter launches and observes one child process.

The first adapter should prefer a direct process interface over a terminal user interface.

It should retain:

- executable identity;
- arguments;
- environment policy;
- working directory;
- effective user;
- process ID and process group;
- start time;
- stdout and stderr;
- exit status or signal;
- cancellation result;
- output population;
- persistent configuration changes; and
- context identity.

NTM may remain useful for human-operated persistent sessions. It should not be the only supported execution contract.

The runtime layer should support:

- Codex CLI;
- Claude Code;
- another approved terminal agent;
- direct Python or shell tools;
- deterministic calculation processes; and
- later remote workers through the same run contract.

A runtime marked complete without a known process result and expected output population should fail closed.

## Methods and actions

The analyst may state an open request. The planner should select only supported methods and actions.

A method registry should describe:

- professional purpose;
- applicable subjects;
- required inputs;
- supported source rights;
- tool needs;
- output types;
- context policy;
- expected checks;
- human decisions;
- cost class;
- stopping conditions;
- known limits; and
- evaluation coverage.

A method may invoke several actions.

A supported action should name:

- exact objective;
- context build;
- permitted tools;
- output contract;
- budget;
- refusal conditions;
- expected audit records; and
- consequence ceiling.

Open-ended planning does not permit imaginary capabilities.

## Native artifact adapters

Artifact adapters should share one contract while preserving native differences.

An adapter should support:

- inspection;
- structural projection;
- professional-object binding;
- proposed operations;
- candidate descendant creation;
- validation;
- diff;
- open in native tool; and
- replay.

### Workbook adapter

The first workbook adapter may support a narrow declared profile.

It should record:

- workbook bytes and digest;
- sheets, names, tables, cells, formulas, styles, comments, and links where supported;
- calculation mode;
- cached values;
- dependency edges;
- macros and unsupported features;
- proposed operations;
- calculation engine;
- descendant bytes; and
- changed values and formulas.

A model may propose which structural object represents a professional object. An authorised mapping should govern consequential writes.

### Document adapter

A document adapter may support claims, citations, sections, figures, and amendments while preserving the original.

### Data and statistical adapter

A data adapter should preserve input files, cleaning code, environment, random seed, output tables, diagnostics, and interpretation claims.

### Chart adapter

A chart adapter should preserve the exact data population, transformations, specification, labels, units, renderer, and output.

## Search and source capture

Discovery and support require different access.

A discovery process may search broadly within the mandate. It may return leads, candidate source identities, questions, and contradictions.

A support process may receive only assertions permitted for the claim, calculation, artifact operation, or memory entry under review.

Search results should become exact captured source versions before they support professional work.

The source service should preserve:

- operating identity;
- connector or browser route;
- source rights;
- capture time;
- exact content or lawful immutable reference;
- provider metadata;
- parsing state; and
- later amendment.

The system should distinguish:

- unavailable;
- access denied;
- not searched;
- not found within declared scope;
- captured but not admitted;
- retained identity only; and
- captured and permitted for a stated use.

## Permissions and authority

The local service should evaluate general grants rather than one generic approval field.

A grant covers:

```text
actor or policy
permitted action
exact object or object class
purpose
validity period
conditions
delegation
precedence
revocation effect
```

A licence restriction outranks team preference. Team policy may narrow an individual grant. An analyst may create an exception only when the mandate permits it.

A user action should say what it does.

Useful actions may read:

```text
Use this workbook candidate for the internal post-results model.
Confirm that this row represents FY2025 consolidated GAAP revenue.
Permit the preliminary earnings-release value until the annual filing appears.
Keep this claim provisional.
Add this corrected meaning to the Micron model context.
Propose this repeated procedure for evaluation.
```

The interface should not expose the grant schema unless the user asks for audit detail.

## Memory

The workspace should keep four separate bodies of memory.

### Archive

Exact sources, runs, artifacts, decisions, and historical perspectives.

### Active perspective

Claims, assumptions, methods, questions, artifact references, and decisions permitted to affect current work.

### Procedural methods

Authorised skills, source rules, calculations, and working procedures with scope and evaluation evidence.

### Evaluation cases

Historical or synthetic cases used to compare later interventions.

Model outputs enter the archive by default. They should not enter the active perspective or procedural methods by default.

A local search index may cover all four stores while preserving their different authority.

## Replay engine

The replay engine should support:

- source replay;
- context replay;
- deterministic derivation replay;
- evidential re-derivation;
- artifact replay;
- memory replay;
- authority replay; and
- counterfactual comparison.

The engine should export a proof pack and a readable explanation.

A replay may run locally. A shared evaluation service may later run several models or workspace versions against protected cases.

## Langfuse and observability

The workspace should emit trace identifiers carrying:

- mandate;
- episode;
- context build;
- method;
- run;
- derivation;
- artifact operation; and
- evaluation case where applicable.

Langfuse may receive prompts, responses, tools, latency, cost, and errors.

The local service should retain enough execution evidence to operate when Langfuse is unavailable.

Observability should help answer:

- which model and tool performed the work;
- what the process could see;
- where time and cost accumulated;
- where a refusal or error occurred; and
- which run produced the stored result.

Audit should answer the separate questions of source, derivation, authority, and replay.

## Security and privacy

The first product should assume the workspace may contain sensitive models, notes, licensed sources, and client decisions.

The plan must settle:

- encryption at rest;
- key ownership;
- backup and recovery;
- secure deletion where licences require it;
- local user isolation;
- sandboxing of child processes;
- network controls;
- connector credentials;
- redaction for exported evaluation cases;
- prevention of cross-mandate retrieval;
- source-retention restrictions;
- trace redaction; and
- cloud synchronisation policy.

A local terminal agent often has broad file access. The product cannot claim strong isolation without an enforceable process and filesystem boundary.

A first individual-user version may begin with an explicit trust model rather than pretending to provide enterprise isolation.

## Optional shared service

The shared service should be added only when the local workflow proves repeated value.

Possible responsibilities include:

- organisation and team identity;
- role and grant policy;
- connector management;
- source entitlement checks;
- shared methods and skills;
- method release channels;
- evaluation runners;
- schedule and monitoring orchestration;
- cross-machine object synchronisation;
- shared audit views;
- usage and cost controls; and
- administrative retention.

The service should synchronise immutable object versions and decisions. It should not overwrite local history silently.

Conflicts should create explicit competing versions or require a decision.

## Relation to the existing repository

The existing repository may contribute:

- Django authentication and ownership concepts;
- append-only object practices;
- exact artifact custody;
- frozen work specifications;
- provisional result handling;
- human dispositions;
- restart retrieval;
- output attestation;
- hostile checks; and
- Langfuse correlation.

The new workspace should not inherit automatically:

- campaign as the universal product object;
- NTM as the only runtime;
- raw candidate JSON as a useful professional result;
- worker-authored source identity;
- campaign pages as the analyst interface;
- mandatory planner, worker, reviewer, synthesis, and judgment roles;
- filesystem output roots as the canonical state; or
- the narrow workbook source check as the product centre.

A later plan should compare three implementation paths:

1. extend the existing Django package with a local mode and new domain objects;
2. build a separate local workspace kernel that reuses selected modules; or
3. build the local kernel cleanly and keep the Django application as an optional shared service.

The comparison should consider migration cost, conceptual leakage, local installation, security, testability, and speed to the first useful episode.

## First coherent vertical

The first vertical should prove the workspace rather than one gate.

It should include:

```text
local workspace initialisation
-> exact prior perspective and artifacts
-> broad analyst request
-> proposed and corrected commission
-> source capture
-> purpose-specific context builds
-> one research method
-> one challenge
-> one native artifact or durable note
-> one analyst correction
-> one scoped use decision
-> one active-memory proposal
-> one inference-state replay
-> a second episode using the corrected state
```

The exact artifact remains open. A research note plus one reproducible calculation may prove more of the workspace sooner than a full Excel integration. A workbook action may still be required when the first analyst’s useful work depends upon it.

## Architecture questions still open

- Should the first code live beside the Django package or in a new package within the same repository?
- Should the local service expose HTTP, a Unix socket, direct library calls, or more than one route?
- Which MCP implementation provides the smallest stable vendor-neutral surface?
- Which sandbox can constrain terminal-agent child processes on the first supported operating systems?
- How should licensed transient sources participate in replay when bytes cannot be retained?
- Which vector and lexical search stack works locally without obscuring exact citations?
- How should a local workspace synchronise encrypted objects with a shared service?
- Which workbook engine can provide a supportable calculation contract?
- Which first methods deserve implementation before broad planning exists?
- How much of the current Django schema can be migrated without retaining the wrong product nouns?
