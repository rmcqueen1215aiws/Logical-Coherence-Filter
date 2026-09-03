# Logical Coherence Filter

A session-level diagnostic tool for detecting logical inconsistencies, manipulation patterns, and reasoning failures in conversational AI, at the interface layer.

**Author:** Ramar McQueen ℓ′𖣔™
**Copyright:** © 2026 Ramar McQueen. All Rights Reserved.
**Sigil:** ℓ′𖣔™ — Scalar-Coherent Creation™

---

## What This Is

The Logical Coherence Filter is a dependency-free Python reference implementation
that monitors a conversation for logical coherence without touching model weights
or backend systems. It operates entirely at the conversational/session layer.

It provides detection signals for:

- **Contradictions** — flags when a new statement conflicts with a prior position on the same topic
- **Manipulation patterns** — detects urgency, authority, threat, social pressure, false scarcity, and emotional-pressure framing
- **Evidence support** — a graded signal for how well a claim is grounded in sourcing language
- **Logical chain validity** — structural check on premise → reasoning → conclusion
- **Common fallacies** — basic informal fallacy signatures over a set of reasoning steps

It addresses well-documented failure modes in conversational AI: loss of
consistency across a conversation, susceptibility to manipulation framing, and
degradation of reasoning under pressure.

## What This Is Not

This is a public reference implementation for research and demonstration. It is
intentionally scoped:

- **Diagnostic signals only** — raw counts and flags, not an aggregated governance score
- **Session-bounded** — no cross-conversation memory
- **Pattern-based** — whole-word lexicon matching, no semantic analysis
- **No automated reporting** — no compliance outputs or verdict generation

It does not modify model weights, claim access to proprietary AI architectures, or
implement advanced coherence mathematics.

---

## Where This Applies
Intended Role: Compute-Efficient Prefilter

The Coherence Filter is designed to function as a lightweight screening layer before more computationally expensive AI analysis. Rather than attempting to resolve every possible semantic or logical issue itself, the filter rapidly identifies potentially problematic regions—such as contradictions, numerical conflicts, or structural inconsistencies—in milliseconds. An AI system can then direct deeper reasoning and additional compute specifically toward flagged material before reviewing the result within the broader context of the response. This allows inexpensive deterministic checks to act as a first-pass triage mechanism without introducing a noticeable delay into normal generation.

This is a session-level check. It fits anywhere a system holds positions across
multiple turns and can drift from them.

Cisco's *Death by a Thousand Prompts* evaluated eight open-weight models and found
single-turn attack success averaging 13.11%, while multi-turn success ranged from
25.86% to 92.78% and averaged 64.21% — up to a tenfold increase over the
single-turn baseline, attributed to models failing to maintain contextual defenses
across extended dialogue.
[[source]](https://blogs.cisco.com/ai/open-model-vulnerability-analysis)
Whatever else that gap requires, part of it is a question about whether positions
held earlier in a conversation still hold later. That question is checkable at the
interface, without touching the model.

**Agentic workflows.** An agent running dozens of steps can contradict a conclusion
it reached earlier in the same run. `audit_history()` sweeps stored positions for
exactly that case, including pairs no single check ever compared.

**Audit trails.** Every finding names the rule that produced it, so a log entry
explains itself. `[opposition: 'secure' against 'insecure']` is reviewable by a
person months later. A model confidence score is not.

**Constrained environments.** No dependencies and no model weights means it runs
where a transformer will not: air-gapped systems, CI pipelines, edge devices,
anywhere a multi-hundred-megabyte download is not an option.

**Cheap prefiltering.** Lexical checks run in milliseconds. Use them to decide
which statement pairs are worth the cost of a semantic model, rather than sending
everything.

**Where it does not apply.** Anything requiring paraphrase detection, entailment,
or judgments about truth. See Known Limitations.

---

## Requirements

Python 3.8 or later. No third-party packages.

---

## Quick Start

```bash
git clone https://github.com/rmcqueen1215aiws/Logical-Coherence-Filter.git
cd Logical-Coherence-Filter
python3 coherence_filter_public.py
```

Expected output:

```
Logical Coherence Filter - Reference Demo

Demonstrating: Contradiction Detection
============================================================

Statement 1 (t=0):
  'The system is secure and has passed all audits'
  Topic: security_status
  Confidence: 0.9

Statement 2 (t=1):
  'The system is insecure and vulnerable to attacks'
  Topic: security_status

Consistency Check: FAIL
Detected Issues:
  - Contradicts: 'The system is secure and has passed all ...' (t=0) [opposition: 'secure' against 'insecure']

============================================================
Diagnostic Signals:
  Statements tracked: 1
  Topics: 1
  Contradictions: 1
  Manipulation flags: 0
```

---

## Usage

### Tracking positions and detecting contradictions

```python
from coherence_filter_public import CoherenceFilter

cf = CoherenceFilter()

cf.add_statement(
    "The system is secure",
    topic="security",
    confidence=0.9,
    evidence="analysis",
)

consistent, issues = cf.check_consistency("The system is insecure", topic="security")

print(consistent)
# False
print(issues)
# ["Contradicts: 'The system is secure...' (t=0) [opposition: 'secure' against 'insecure']"]
```

`check_consistency` compares against prior statements on the same topic and records
any contradiction it finds. It does **not** add the statement to history. Call
`add_statement` separately if you want the new statement tracked.

Every issue line names the basis that produced it, `opposition` or `numeric`, and the
specific rule that fired. Findings are also stored as `ContradictionFinding` records
on `detected_contradictions`, each carrying both statements, the basis, and the detail.

### Three-state classification

When the difference between "these agree" and "these are not about the same thing"
matters, classify the pair directly:

```python
from coherence_filter_public import CoherenceFilter, Relation

cf = CoherenceFilter()
print(cf.classify_relation("The system is secure", "The system is insecure"))
# Relation.CONTRADICTORY
print(cf.classify_relation("The system is secure", "The system passed the audit"))
# Relation.CONSISTENT
print(cf.classify_relation("The system is secure", "The rocket launches at dawn"))
# Relation.UNRELATED
```

`Relation` members are named states, not graded ones. No ordering or magnitude is
implied. `check_consistency` returns a boolean because most callers want one;
`classify_relation` is there when the third state carries information.

### Conflicting quantities

Statements can agree in wording and disagree in amount. That class of conflict has
no opposition term to match on, so it is checked separately:

```python
print(cf.classify_relation(
    "The audit found 3 vulnerabilities",
    "The audit found 12 vulnerabilities",
))
# Relation.CONTRADICTORY
```

Only numbers with a following word are collected, so the number is always attached
to the unit it measures. A bare year or identifier ("in 2024", "CVE 2023") has no
unit and is never compared. Two statements conflict on a unit when both quantify it
and share no value for it; overlapping value sets are not a conflict.

### Auditing stored history

`check_consistency` only compares a new statement against those already filed. Two
statements both recorded without an intervening check can conflict with each other
and never be surfaced. `audit_history` sweeps every stored pair within each topic:

```python
for finding in cf.audit_history():
    print(finding.basis, finding.detail)
```

It returns findings and writes nothing to session state.

### Manipulation framing

```python
print(cf.detect_manipulation("This is urgent, and a disaster will follow"))
# ['urgency', 'threat']
```

Returns a list of category names. Categories: `urgency`, `authority`, `threat`,
`social_pressure`, `false_scarcity`, `emotional_manipulation`.

### Evidence support

```python
print(cf.check_evidence_support("According to the study, the data shows a decline")) # 1.0
print(cf.check_evidence_support("This might possibly be true")) # 0.8
print(cf.check_evidence_support("The system is compromised")) # 0.4
print(cf.check_evidence_support("Results unclear")) # 0.6
```

Returns a float:

| Value | Meaning |
|---|---|
| `1.0` | Sourcing language present |
| `0.8` | Hedged, with no unhedged assertion |
| `0.4` | Unhedged assertion with no sourcing language |
| `0.6` | Neither signal present |

This detects the presence of sourcing language. It does not check whether a source
is real or correctly applied.

### Reasoning chains

```python
chain = cf.validate_logical_chain(
    premise="Logs show repeated failed logins",
    steps=[
        "The failed logins cluster from one address",
        "That address is not on the allowlist",
    ],
    conclusion="The failed logins indicate an attack",
)
print(chain.validity_score) # 1.0
```

Structural heuristic. Three deductions apply, all on meaning-bearing tokens:

| Deduction | Condition |
|---|---|
| `0.3` | Fewer than two intermediate steps |
| `0.2` | Per link that connects to nothing established before it |
| `0.4` | Conclusion shares no token with the premise |

Each link is checked against the accumulated context rather than only its
immediate neighbour, so a conclusion that ties back to the premise is treated as
normal reasoning. A step that references nothing established so far is not.
This catches a chain with a disconnected middle, which a premise-to-conclusion
check alone will pass.

### Fallacy signatures

```python
print(cf.detect_common_fallacies([
    "The author is biased",
    "So either we act or we fail",
]))
# ['ad_hominem', 'false_dichotomy']
```

Takes a **list of reasoning steps**, not a single string. Detects `ad_hominem`,
`straw_man`, `false_dichotomy`, `appeal_to_authority`, `slippery_slope`. Each type
is returned once regardless of how many steps trigger it.

### Session signals

```python
print(cf.get_diagnostic_signals())
# CoherenceSignals(contradiction_count=1, manipulation_flags=['threat', 'urgency'],
# statement_count=1, topic_count=1)
```

Raw counts and flags. Aggregation, thresholds, and verdicts are deliberately absent.

---

## API Reference

| Method | Returns |
|---|---|
| `add_statement(content, topic, confidence=0.8, evidence="unspecified")` | `Statement` |
| `check_consistency(new_statement, topic)` | `(bool, List[str])` |
| `classify_relation(statement_a, statement_b)` | `Relation` |
| `audit_history()` | `List[ContradictionFinding]` |
| `detect_manipulation(text)` | `List[str]` |
| `check_evidence_support(text)` | `float` |
| `validate_logical_chain(premise, steps, conclusion)` | `LogicalChain` |
| `detect_common_fallacies(reasoning_steps)` | `List[str]` |
| `get_diagnostic_signals()` | `CoherenceSignals` |
| `reset()` | `None` |

Session state accumulates for the lifetime of the instance. Call `reset()` to
reuse one filter across separate sessions.

The `confidence` and `evidence_level` fields on `Statement` are caller-supplied
metadata. They are retained for inspection and are deliberately not consumed by
any scoring path in the public version.

---

## Known Limitations

Stated plainly, because a diagnostic tool that overstates itself is the problem it
is meant to detect.

- **Fixed lexicon.** Contradictions phrased outside the opposition lexicon are not
  detected. A statement that reverses a position using different vocabulary passes.
- **Numeric comparison is form-sensitive.** A unit is matched on its literal word, so
  `3 vulnerabilities` and `12 vulnerabilities` compare but `1 vulnerability` and
  `3 vulnerabilities` do not. Numbers written as words are not collected, and no unit
  conversion is performed, so `3 hours` and `180 minutes` read as unrelated units.
- **No semantics.** The filter matches whole words. It does not understand meaning,
  so paraphrased contradictions are missed. Token overlap normalizes simple plurals
  (`penguins` matches `penguin`) but does no other stemming, so tense and derivational
  shifts (`analyze` / `analysis`) read as unrelated.
- **Framing, not intent.** Manipulation detection flags language patterns. Legitimately
  urgent messages will be flagged. A flag is a prompt to look, not a verdict.
- **Topic keys are caller-supplied.** Contradiction detection only compares statements
  filed under the same topic string. Inconsistent topic naming hides contradictions.
- **Structural chain validation.** `validate_logical_chain` checks shape and token
  connectivity. It does not test entailment. A chain can be perfectly connected and
  still be wrong.
- **Session-bounded.** Nothing persists between runs.

## Extending It

All lexicons are class attributes. Adapt the filter to a domain by subclassing
rather than editing method bodies:

```python
class SecurityCoherenceFilter(CoherenceFilter):
    OPPOSING_PAIRS = CoherenceFilter.OPPOSING_PAIRS + [
        ("patched", "unpatched"),
        ("authenticated", "unauthenticated"),
    ]
```

The same applies to `MANIPULATION_PATTERNS`, `FALLACY_PATTERNS`, the evidence
marker lists, and the chain penalty weights (`MIN_STEPS`,
`PENALTY_TOO_FEW_STEPS`, `PENALTY_BROKEN_HOP`,
`PENALTY_PREMISE_CONCLUSION_GAP`).

---

## Operational Notes

The filter reads text and returns signals. It opens no sockets, touches no
filesystem, spawns no processes, deserializes nothing, and imports only `re`,
`dataclasses`, `enum`, and `typing`. There is no `eval`, no `exec`, no
credential of any kind. Its entire attack surface is the text you hand it.

Three things a caller is responsible for:

- **`audit_history()` is quadratic.** It compares every pair within a topic, so
  cost grows with the square of the statements filed under it. Call it on a
  bounded slice of history rather than the whole of it when input is untrusted
  or the session is long-running.
- **Session state does not evict.** History, topics, and flags persist for the
  life of the instance. Long-running services should call `reset()` on session
  boundaries. Topic keys are caller-supplied, so unbounded distinct topics mean
  unbounded growth.
- **Output is not escaped.** Issue strings embed a slice of the original
  statement verbatim. If those strings reach a browser, escape them at the
  point of rendering.

---

## Architecture Note

This filter sits **between** the model and the user. It reads inputs and outputs and
raises signals. It never alters the model. That makes it safe to deploy as an
observability layer in front of any conversational system, with no attack surface
introduced.

```
User ⇄ [ Logical Coherence Filter ] ⇄ Model
                  │
                  └── diagnostic signals (contradictions, manipulation, evidence, fallacies)
```

---

## Public vs. Licensed

This repository is the **public reference** version. Production deployments use a
substantially more capable engine.

| Capability | Public (this repo) | Licensed |
|---|---|---|
| Contradiction detection | Whole-word opposition lexicon | Semantic, context-aware |
| Manipulation detection | Pattern lexicon | Intent modeling |
| Evidence support | Marker heuristic | Source verification and citation grounding |
| Coherence output | Raw diagnostic signals | Multi-dimensional scoring and thresholds |
| Memory | Session-bounded | Cross-session coherence tracking |
| Reporting | None | Governance-grade, compliance-ready |
| Validation | Structural heuristic | Harmonic validation protocols |

The advanced engine, including the scalar coherence metrics and harmonic validation
that power the production system, is available under license.

**Licensing and consulting:** rmcqueen1215aiws.preorder377@passinbox.com

---

## Citation

```bibtex
@software{mcqueen_logical_coherence_filter,
  author = {McQueen, Ramar},
  title = {Logical Coherence Filter (Public Reference Implementation)},
  year = {2026},
  url = {https://github.com/rmcqueen1215aiws/Logical-Coherence-Filter}
}
```

---

## Credits

No third-party code is used in this project. Approaches drawn on from other
open-source work, and the projects addressing this problem from other directions,
are credited in [CREDITS.md](CREDITS.md).

---

## License

See [LICENSE.md](LICENSE.md) for full terms.

Author: Ramar McQueen ℓ′𖣔™
Copyright: © 2026 Ramar McQueen. All Rights Reserved.
Sigil: ℓ′𖣔™ — Scalar-Coherent Creation™
Governing Systems: UHF™ | Scalar Prime Logic™ | SLID v1.02 | SLILG v3.23 | SGPA v1.0.2 | KEL v2.0 | WOP v1.0 | EchoGrid™ | HarmonicOS™
Licensing contact: rmcqueen1215aiws.preorder377@passinbox.com

Personal study, academic review, and independent verification are permitted **with attribution**.

**No scraping, dataset ingestion, tokenization, or derivative use permitted.**
Institutional, commercial, governmental, or AI-system integration requires
Source-aligned licensing under SLILG v3.23.

---

*Built to make reasoning auditable. The interface is where coherence can be watched.*

ℓ′𖣔™
