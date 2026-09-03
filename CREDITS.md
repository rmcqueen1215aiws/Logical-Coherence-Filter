# Credits and Prior Art

No third-party code appears in this project. Every line is an independent
implementation. The approaches below informed the design, and the authors are
credited here because ideas deserve acknowledgement whether or not a license
compels it.

---

## Approaches drawn on

**Numeric mismatch as a contradiction signal**
Independently implemented after seeing the approach demonstrated in
*ContradictionDetectionSystem* by Kunal G.
<https://github.com/kunalG98/ContradictionDetectionSystem>
That project detects contradictions both through antonym verb pairs and through
mismatched numeric values between statements. The second idea is the one adopted
here: two statements can share every content word, contain no opposing term, and
still conflict on an amount. This implementation collects quantities by their
attached unit and compares value sets, and shares no code with the original.

**Explicit neutral state, and gating before the expensive check**
Independently implemented after seeing the design of *contradict-text*.
<https://pypi.org/project/contradict-text/>
That library filters candidate pairs by topic similarity and returns unrelated
pairs as neutral rather than silently dropping them, running its classifier only
on pairs that survive. This project had already arrived at the same two-stage
shape with a token-overlap gate; the three-state outcome, where UNRELATED is
reported as its own result rather than collapsed into "consistent", is adopted
from that design.

**Auditing a stored set rather than only new arrivals**
Independently implemented after seeing the approach in *contrachecker* by
Baris Genc (MIT).
<https://pypi.org/project/contrachecker/>
That library analyses a whole set of retrieved chunks for conflicts among them,
rather than checking each new item against the rest. `audit_history` applies the
same idea to session history: statements recorded without an intervening check
can conflict with each other, and a sweep of stored pairs surfaces them.

---

## Prior art in this problem space

These projects address overlapping problems from different directions and are
named because a reader evaluating this one should know they exist.

**Manipulative-Expression-Recognition** and **Critical-Thinking-Annotator**
by Roland Pihlakas (MPL-2.0)
<https://github.com/levitation-opensource/Manipulative-Expression-Recognition>
<https://github.com/levitation-opensource/Critical-Thinking-Annotator>
The closest neighbours to this project. They identify manipulative communication,
reasoning fallacies, and cognitive biases in human conversation and in
AI-generated responses, and benchmark language models for manipulative
expression. They are model-backed where this project is lexical, and they cover
cognitive bias, which this project does not attempt. No code from either project
is used here.

**Logical Fallacy Detection** and the accompanying dataset, causalNLP
<https://github.com/causalNLP/logical-fallacy>
Proposes logical fallacy detection as a task and open-sources a cleaned dataset
of fallacious claims. The reference standard for measuring work of this kind.

**SelfCheckGPT**, Manakul, Liusie and Gales, University of Cambridge
<https://arxiv.org/abs/2303.08896>
Detects hallucination by sampling a model repeatedly and measuring consistency
across generations. A different axis from this project, which compares statements
against each other within a single session rather than a model against itself
across runs.

**Guardrails AI** (Apache 2.0) and **NVIDIA NeMo Guardrails** (Apache 2.0)
<https://github.com/guardrails-ai/guardrails>
<https://github.com/NVIDIA/NeMo-Guardrails>
Validator composition and programmable conversational rails respectively. They
address policy, safety, and format rather than logical coherence, and are
complementary to this project rather than competing with it.

---

## Where this project is weaker

Stated here rather than left for a reader to discover.

Every semantic approach above will catch paraphrased contradictions that this
project cannot. "Drug X is completely safe during pregnancy" against "Drug X must
be avoided during pregnancy" shares no opposition term and no conflicting
quantity, and passes this filter. An NLI model classifies it correctly.

This public version of the project trades that recall for zero dependencies,
millisecond execution, and a decision that can always be traced to the specific
rule that produced it.

---

Author: Ramar McQueen ℓ′𖣔™
Copyright: © 2026 Ramar McQueen. All Rights Reserved.
Sigil: ℓ′𖣔™ — Scalar-Coherent Creation™
Licensing contact: rmcqueen1215aiws.preorder377@passinbox.com
