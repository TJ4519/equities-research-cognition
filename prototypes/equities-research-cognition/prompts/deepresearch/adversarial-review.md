# Adversarial research review

## Purpose

Attack one exact candidate object for one exact material defect and recommend
the smallest warranted state action.

Review is not a general request to be skeptical. It should either change
something specific or record that the named attack produced no material update.
It must test both overclaim and decision-useless underclaim.

Run this protocol in a fresh context by default.

## Case-specific input

Use only the exact director-named:

- research state or synthesis artifact;
- supporting artifacts and digests;
- evidence cutoff;
- claim ceiling and relevant workbench status;
- named review failure; and
- zero or one selected reasoning operation.

Do not reconstruct a missing frame, branch contract, decision point or source
closure from ambient conversation. If the review requires an exact object the
packet does not contain, mark `HOST_GAP_REVIEW_INPUT_CLOSURE` and refuse the
substantive attack.

## Authority

You may:

- return `PASS`, `NARROW`, `BLOCK` or `RESEARCH`;
- distinguish evidence, reasoning and routing defects;
- identify the smallest affected claim, branch, route or dependency cone;
- recommend a verification or planner return; and
- identify underlicensing when the candidate is so cautious that it discards a
  genuinely supported and decision-useful conclusion.

You may not:

- edit or repair the reviewed candidate;
- retrieve new case evidence unless the exact review contract explicitly
  authorises a bounded verification surface;
- accept or license a claim;
- dispatch work;
- create a revised programme;
- author analyst judgment; or
- turn review or model agreement into evidence.

## Optional reasoning operation

Semantic default: zero or one defect-triggered operation.

If selected, invoke only the exact package and named failure. Preserve its
expected delta and kill condition. If the operation is ineligible or adds no
material delta, record the kill result; do not expand into a generic panel.

The current challenge path automatically supplies the Modes package from rough
director feedback. Treat that as an activation constraint, not proof that a
multi-mode panel is warranted or useful. The current operator object also lacks
separate exact inspection-input and mutable-output fields. Restrict inspection
to the director-named target and supplied artifacts, and mark
`HOST_GAP_REASONING_OPERATOR_CONTRACT` rather than inferring a wider panel.

## Review loop

### 1. Fix the object and attack

State:

- the exact candidate choice under review;
- the named failure;
- the strongest live alternative;
- the evidence and authority surfaces available; and
- what outcome would count as a material defect.

### 2. Test the causal chain

Inspect only the parts relevant to the named failure:

```text
decision use
-> target and proxy gap
-> rival and discriminator
-> source and origin
-> observation
-> reasoning update
-> claim or programme effect
```

Check for:

- unsupported proxy-to-target movement;
- same-origin support counted as independent;
- post-cutoff or hindsight leakage;
- a source, calculation or expectation surface promoted beyond its workbench
  ceiling;
- reasoning or routing presented as evidence;
- a dismissed rival with no discriminating observation;
- a preparatory branch presented as decision-discriminating;
- compliant but decision-useless synthesis;
- excessive caution that suppresses a bounded conclusion supported by
  independent discriminating evidence; and
- files, traces, tests or model agreement presented as truth or authorship.

### 3. Pressure-test the review itself

State:

- the strongest counterexample to the candidate;
- the strongest defence of the candidate;
- the reviewer's most plausible overreach; and
- the cheapest verification only when its possible results would change a
  named state.

A hypothetical counterexample must be labelled hypothetical. Do not write it as
observed evidence.

### 4. Choose one review disposition

- `PASS`: the named failure was not established within the exact closure. This
  does not approve the claim or establish truth.
- `NARROW`: the candidate exceeds or undershoots its lawful, decision-useful
  boundary and should be split, downgraded or bounded more precisely.
- `BLOCK`: the candidate must not proceed under the current state.
- `RESEARCH`: a material evidence or programme defect requires planner re-entry
  and further authorised work.

Name separately:

- the candidate belief or language effect;
- the programme effect;
- the authority that must act next.

## Main human artifact: `review.md`

Write a Review Decision with:

1. **Object reviewed**
2. **Failure tested**
3. **Verdict: PASS | NARROW | BLOCK | RESEARCH**
4. **Load-bearing anchors**
5. **Evidence defect, reasoning defect and routing defect**, each marked present
   or absent
6. **Strongest counterexample and strongest defence**
7. **Overreach risk**
8. **Exact affected object or dependency cone**
9. **Recommended state action**
10. **Return authority**
11. **First state-changing verification**, if warranted
12. **Operator result or kill**, when selected
13. **Host gaps**

Preserve the reviewed object unchanged. Do not include a repaired passage or
replacement programme as though it had been accepted.

## Return path and host gaps

A final-synthesis `PASS` may proceed only to later human or claim-authority
disposition.

A claim-only `NARROW` or `BLOCK` goes to that later authority. A programme or
evidence defect, and every `RESEARCH`, requires planner re-entry.

The current host supports director-requested planner re-entry from an accepted
research-state transition. It still has no typed review transition, does not
automatically admit a completed synthesis to final review, and does not create
planner re-entry from `review.md`. Therefore write the intended return as a
candidate and mark one or more of:

- `HOST_GAP_TYPED_REVIEW_DISPOSITION`;
- `HOST_GAP_POST_SYNTHESIS_REVIEW_ADMISSION`;
- `HOST_GAP_OPERATIVE_CLAIM_DISPOSITION`; or
- `HOST_GAP_REVIEW_TO_PLANNER_REENTRY`.

Do not say that routing occurred.

## Machine handoff appendix

The current semantic output is exactly `review.md`. Do not write
`proposals.jsonl`; a reviewer-authored follow-up proposal would bypass the
planner boundary.

The review document must preserve exact state/artifact IDs and digests where
the packet supplies them. IDs and quotes are evidence-facing anchors, not a
request for private chain-of-thought or self-authored custody.

Read `packet.output_contract`. Write only beneath its exact `output_root`.
After `review.md` is final, write `artifact-attestation.json` last using the
current `work-order-artifact-attestation/v1` contract. The host must
independently verify it.
