"""
Logical Coherence Filter (Public Reference Implementation)

Author: Ramar McQueen ℓ′𖣔™
© 2025 Ramar McQueen. All Rights Reserved.

Authored 2025. Released 2026 under SLID v1.02 / SLILG v3.23.

Framework Protection:
ℓ′𖣔™ | Scalar-Coherent Creation™

Governing Systems:
UHF™ | Scalar Prime Logic™ | SLID v1.02 | SLILG v3.23 | SGPA v1.0.2 |
KEL v2.0 | WOP v1.0 | EchoGrid™ | HarmonicOS™

IMPORTANT:
This is a REFERENCE implementation intended for research,
discussion, and demonstration purposes only.

PUBLIC VERSION - Diagnostic signals and detection patterns.
It provides detection capabilities but NOT operational governance,
scoring systems, or compliance reporting.

This operates strictly at the conversational/session layer
and does NOT modify model weights or backend systems.

See README.md for scope and known limitations.
See LICENSE.md for full terms.
Licensing contact: rmcqueen1215aiws.preorder377@passinbox.com
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Pattern, Tuple

# -------------------------
# SHARED LEXICONS
# -------------------------

# A number followed by the word it measures: "3 vulnerabilities", "12 hours".
# A bare number with no following word carries no unit and is ignored, which
# keeps years and identifiers ("in 2024", "CVE 2023") out of comparison.
NUMBER_PATTERN: Pattern = re.compile(r"\b(\d+(?:\.\d+)?)\s+([a-z]+)")

# Tokens too common to carry meaning when comparing two statements.
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "at", "by",
    "for", "with", "is", "are", "was", "were", "be", "been", "being", "it",
    "its", "this", "that", "these", "those", "has", "have", "had", "not",
    "no", "as", "from", "will", "can", "all", "any", "we", "you", "they",
}

# (positive_term, negating_term) pairs used for opposition detection.
# Extend by subclassing and overriding CoherenceFilter.OPPOSING_PAIRS.
DEFAULT_OPPOSING_PAIRS: List[Tuple[str, str]] = [
    ("is", "is not"),
    ("can", "cannot"),
    ("should", "should not"),
    ("will", "will not"),
    ("valid", "invalid"),
    ("secure", "insecure"),
    ("safe", "unsafe"),
    ("consistent", "inconsistent"),
    ("possible", "impossible"),
    ("qualified", "unqualified"),
    ("able", "unable"),
    ("true", "false"),
]

# -------------------------
# DATA STRUCTURES
# -------------------------

@dataclass
class Statement:
    """
    Individual statement with metadata for tracking.

    NOTE: `confidence` and `evidence_level` are caller-supplied metadata.
    They are retained for inspection and are deliberately NOT consumed by
    any scoring path in the public version, which reports raw signals
    rather than weighted judgments.
    """
    content: str
    timestamp: int
    topic: str
    confidence: float
    evidence_level: str


class Relation(Enum):
    """
    Structural relation between two statements.

    Three states rather than two. A pair that shares no subject matter is
    UNRELATED, which is a different fact about the pair than CONSISTENT
    and is reported as such rather than collapsed into it.

    These are named states, not graded ones. No ordering or magnitude is
    implied and none should be inferred.
    """
    CONSISTENT = "consistent"
    CONTRADICTORY = "contradictory"
    UNRELATED = "unrelated"


@dataclass
class ContradictionFinding:
    """
    A recorded structural conflict between two statements.

    `basis` names which check fired, so every finding is traceable to the
    rule that produced it rather than to an unexplained determination.
    """
    earlier: Statement
    later: Statement
    basis: str
    detail: str


@dataclass
class LogicalChain:
    """Reasoning chain validation structure"""
    premise: str
    reasoning_steps: List[str]
    conclusion: str
    validity_score: float


@dataclass
class CoherenceSignals:
    """
    Diagnostic signals (not operational scores).

    NOTE: Production systems require aggregation logic,
    threshold definitions, and governance protocols.
    """
    contradiction_count: int
    manipulation_flags: List[str]
    statement_count: int
    topic_count: int

# -------------------------
# CORE FILTER
# -------------------------

class CoherenceFilter:
    """
    Session-level logical coherence diagnostic tool.

    Provides detection signals for:
    - Statement contradictions
    - Manipulation patterns
    - Evidence support levels
    - Logical chain validity
    - Common informal fallacies

    PUBLIC VERSION LIMITATIONS:
    - Diagnostic signals only (no governance scoring)
    - Session-bounded (no cross-conversation memory)
    - Pattern-based (no semantic analysis)
    - No automated reporting or compliance outputs

    Lexicons are class attributes. Subclass and override them to adapt
    the filter to a domain without touching method bodies.
    """

    OPPOSING_PAIRS = DEFAULT_OPPOSING_PAIRS

    MANIPULATION_PATTERNS: Dict[str, List[str]] = {
        "urgency": [
            r"\burgent\b", r"\bimmediately\b", r"\bright now\b",
            r"\bemergency\b", r"\bact now\b", r"\bbefore it'?s too late\b",
            r"\brunning out of time\b",
        ],
        "authority": [
            r"\bofficial\b", r"\bclassified\b", r"\bauthorized\b",
            r"\bsecret\b", r"\bexperts? agree\b", r"\btrust me\b",
        ],
        "threat": [
            r"\bcatastroph\w*", r"\bdisaster\b", r"\blife or death\b",
            r"\bor else\b", r"\byou'?ll regret\b", r"\bend of the world\b",
        ],
        "social_pressure": [
            r"\beveryone knows\b", r"\bobviously\b", r"\bclearly\b",
            r"\bno one seriously\b",
        ],
        "false_scarcity": [
            r"\bonly chance\b", r"\blast opportunity\b", r"\blast chance\b",
            r"\bwon'?t come again\b",
        ],
        "emotional_manipulation": [
            r"\byou must\b", r"\byou have to\b", r"\bobligation\b",
            r"\bthink of the\b", r"\bhow could you\b", r"\bif you really\b",
            r"\byou'?d be a fool\b",
        ],
    }

    FALLACY_PATTERNS: Dict[str, List[str]] = {
        "ad_hominem": [
            r"\b(stupid|incompetent|biased|dishonest)\b",
            r"\byou'?re just\b", r"\bonly an idiot\b", r"\bwhat would you know\b",
        ],
        "straw_man": [
            r"\b(they claim|they believe)\b.*\b(but really|actually)\b",
            r"\bso you'?re saying\b", r"\bwhat you really mean\b",
        ],
        "false_dichotomy": [
            r"\beither\b.*\bor\b",
            r"\bif you'?re not\b.*\byou'?re\b",
        ],
        "appeal_to_authority": [
            r"\b(expert says|studies show)\b.*\bproves\b",
        ],
        "slippery_slope": [
            r"\bnext thing you know\b", r"\bwhere does it end\b",
            r"\bslippery slope\b",
        ],
    }

    EVIDENCE_MARKERS = [
        "according to", "research shows", "documented", "verified",
        "confirmed", "measured",
    ]
    SPECULATION_MARKERS = [
        "might", "could", "possibly", "potentially", "appears", "seems",
        "maybe", "probably",
    ]
    STRONG_CLAIM_MARKERS = [
        "is", "will", "must", "definitely", "certainly", "always", "never",
    ]

    # Chain-validation tunables.
    MIN_STEPS = 2
    PENALTY_TOO_FEW_STEPS = 0.3
    PENALTY_BROKEN_HOP = 0.2
    PENALTY_PREMISE_CONCLUSION_GAP = 0.4

    def __init__(self):
        self.conversation_history: List[Statement] = []
        self.topic_positions: Dict[str, List[Statement]] = {}
        self.detected_contradictions: List[ContradictionFinding] = []
        self.manipulation_flags: List[str] = []
        self._compiled: Dict[str, Dict[str, List[Pattern]]] = {
            "manipulation": {
                k: [re.compile(p) for p in v]
                for k, v in self.MANIPULATION_PATTERNS.items()
            },
            "fallacy": {
                k: [re.compile(p) for p in v]
                for k, v in self.FALLACY_PATTERNS.items()
            },
        }

    def reset(self) -> None:
        """
        Clear all session state.

        Statement history, topic positions, recorded contradictions, and
        accumulated manipulation flags persist for the lifetime of the
        instance. Call this to reuse one filter across separate sessions
        instead of constructing a new one.
        """
        self.conversation_history.clear()
        self.topic_positions.clear()
        self.detected_contradictions.clear()
        self.manipulation_flags.clear()

    # -------------------------
    # INTERNAL TEXT HELPERS
    # -------------------------

    @staticmethod
    def _contains_term(text: str, term: str) -> bool:
        """
        Whole-word containment test.

        Word boundaries matter here. A plain substring test reports
        'secure' inside 'insecure' and 'is' inside 'this', which
        produces false contradictions between agreeing statements.
        """
        return re.search(rf"\b{re.escape(term)}\b", text.lower()) is not None

    @classmethod
    def _polarity(cls, text: str, positive: str, negative: str) -> Tuple[bool, bool]:
        """
        Determine whether a statement asserts or negates a term.

        The negating phrase is removed before testing for the positive
        term, so 'is not' is never also counted as 'is'.

        Returns:
            (asserts_positive, asserts_negative)
        """
        lowered = text.lower()
        has_negative = cls._contains_term(lowered, negative)
        stripped = re.sub(rf"\b{re.escape(negative)}\b", " ", lowered)
        has_positive = cls._contains_term(stripped, positive)
        return has_positive, has_negative

    @staticmethod
    def _content_tokens(text: str) -> set:
        """
        Meaning-bearing tokens, stopwords removed.

        A depluralized form is added alongside each token so that
        'penguins' overlaps 'penguin' and 'mammals' overlaps 'mammal'.
        Without it, a chain that shifts between singular and plural
        reads as disconnected. Both forms are kept rather than
        replaced, so no real word is destroyed by the stripping.
        """
        tokens = set()
        for word in re.findall(r"[a-z]+", text.lower()):
            if word in STOPWORDS:
                continue
            tokens.add(word)
            if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
                tokens.add(word[:-1])
        return tokens

    def _match_categories(self, text: str, group: str) -> List[str]:
        """Return every category in a compiled pattern group that matches."""
        lowered = text.lower()
        return [
            category
            for category, patterns in self._compiled[group].items()
            if any(p.search(lowered) for p in patterns)
        ]

    # -------------------------
    # STATEMENT TRACKING
    # -------------------------

    def add_statement(
        self,
        content: str,
        topic: str,
        confidence: float = 0.8,
        evidence: str = "unspecified"
    ) -> Statement:
        """
        Add statement to conversation tracking.

        Returns:
            The recorded Statement.
        """
        statement = Statement(
            content=content,
            timestamp=len(self.conversation_history),
            topic=topic,
            confidence=confidence,
            evidence_level=evidence
        )
        self.conversation_history.append(statement)
        self.topic_positions.setdefault(topic, []).append(statement)
        return statement

    # -------------------------
    # CONTRADICTION DETECTION
    # -------------------------

    def check_consistency(
        self,
        new_statement: str,
        topic: str
    ) -> Tuple[bool, List[str]]:
        """
        Check if a new statement contradicts previous positions on a topic.

        Contradictions found are recorded in `detected_contradictions`.
        The statement itself is NOT added to history. Call `add_statement`
        separately if you want it tracked.

        NOTE: Whole-word opposition matching over a fixed lexicon.
        Contradictions phrased without those terms are not detected.

        Returns:
            (is_consistent, list_of_contradiction_descriptions)
        """
        contradictions: List[str] = []

        candidate = Statement(
            content=new_statement,
            timestamp=len(self.conversation_history),
            topic=topic,
            confidence=0.5,
            evidence_level="unverified"
        )

        for prev in self.topic_positions.get(topic, []):
            finding = self._compare(prev, candidate)
            if finding is not None:
                self.detected_contradictions.append(finding)
                contradictions.append(self._describe(finding))

        return len(contradictions) == 0, contradictions

    def _compare(self, earlier: Statement, later: Statement) -> Optional[ContradictionFinding]:
        """Build a finding for a conflicting pair, or None if they do not conflict."""
        detail = self._opposition_conflict(earlier.content, later.content)
        basis = "opposition"
        if detail is None:
            detail = self._numeric_conflict(earlier.content, later.content)
            basis = "numeric"
        if detail is None:
            return None
        if not (self._content_tokens(earlier.content) & self._content_tokens(later.content)):
            return None
        return ContradictionFinding(earlier=earlier, later=later, basis=basis, detail=detail)

    @staticmethod
    def _describe(finding: ContradictionFinding) -> str:
        """Render a finding as a single traceable line."""
        preview = finding.earlier.content[:40]
        return (
            f"Contradicts: '{preview}...' (t={finding.earlier.timestamp}) "
            f"[{finding.basis}: {finding.detail}]"
        )

    def audit_history(self) -> List[ContradictionFinding]:
        """
        Compare every stored pair within each topic.

        `check_consistency` only ever compares a new statement against those
        already filed. A conflict between two statements that were both
        recorded without an intervening check is therefore never surfaced.
        This sweeps the stored history and reports those pairs.

        Findings are returned, not counted or aggregated. Nothing is written
        to session state.

        COST: compares every pair within a topic, so work grows with the
        square of the statements filed under it. Roughly 320,000 comparisons
        for 800 statements on one topic. On untrusted or long-running input,
        call this on a bounded slice of history rather than the whole of it.
        """
        findings: List[ContradictionFinding] = []
        for statements in self.topic_positions.values():
            for index, earlier in enumerate(statements):
                for later in statements[index + 1:]:
                    finding = self._compare(earlier, later)
                    if finding is not None:
                        findings.append(finding)
        return findings

    def classify_relation(self, statement_a: str, statement_b: str) -> Relation:
        """
        Classify the structural relation between two statements.

        Order of determination:
          1. No shared meaning-bearing token -> UNRELATED. The pair is not
             about the same thing, so no claim about agreement is made.
          2. An opposition-lexicon conflict, or a numeric conflict on a
             shared unit -> CONTRADICTORY.
          3. Otherwise -> CONSISTENT.

        Returns a named state. Nothing is scored, ranked, or weighted.
        """
        if not (self._content_tokens(statement_a) & self._content_tokens(statement_b)):
            return Relation.UNRELATED

        if self._opposition_conflict(statement_a, statement_b) is not None:
            return Relation.CONTRADICTORY

        if self._numeric_conflict(statement_a, statement_b) is not None:
            return Relation.CONTRADICTORY

        return Relation.CONSISTENT

    def _opposition_conflict(self, s1: str, s2: str) -> Optional[str]:
        """
        Whole-word opposition conflict, or None.

        Returns the pair that fired so the finding can name its own basis.
        """
        for positive, negative in self.OPPOSING_PAIRS:
            pos_1, neg_1 = self._polarity(s1, positive, negative)
            pos_2, neg_2 = self._polarity(s2, positive, negative)
            if (pos_1 and neg_2) or (neg_1 and pos_2):
                return f"'{positive}' against '{negative}'"
        return None

    @staticmethod
    def _numeric_claims(text: str) -> Dict[str, set]:
        """
        Map each measured unit to the values asserted for it.

        'The audit found 3 vulnerabilities' yields {'vulnerabilities': {3.0}}.
        Only numbers with a following word are collected, so a bare year or
        identifier contributes nothing to compare.
        """
        claims: Dict[str, set] = {}
        for value, unit in NUMBER_PATTERN.findall(text.lower()):
            if unit in STOPWORDS:
                continue
            claims.setdefault(unit, set()).add(float(value))
        return claims

    def _numeric_conflict(self, s1: str, s2: str) -> Optional[str]:
        """
        Conflicting quantities asserted for the same unit, or None.

        Two statements conflict on a unit when both quantify it and share
        no value for it. Overlapping value sets are not a conflict.

        This catches a class the opposition lexicon cannot reach: statements
        that agree in wording and disagree in amount.
        """
        left = self._numeric_claims(s1)
        right = self._numeric_claims(s2)
        for unit in sorted(set(left) & set(right)):
            if left[unit].isdisjoint(right[unit]):
                shown_left = ", ".join(self._format_value(v) for v in sorted(left[unit]))
                shown_right = ", ".join(self._format_value(v) for v in sorted(right[unit]))
                return f"{unit}: {shown_left} against {shown_right}"
        return None

    @staticmethod
    def _format_value(value: float) -> str:
        """Render a collected value without trailing float noise."""
        return str(int(value)) if value.is_integer() else str(value)

    def _detect_contradiction(self, s1: str, s2: str) -> bool:
        """
        Whether two statements structurally conflict.

        Retained as a boolean convenience over `classify_relation`. Use
        `classify_relation` when the distinction between CONSISTENT and
        UNRELATED matters.
        """
        return self.classify_relation(s1, s2) is Relation.CONTRADICTORY

    # -------------------------
    # MANIPULATION DETECTION
    # -------------------------

    def detect_manipulation(self, text: str) -> List[str]:
        """
        Detect linguistic manipulation patterns.

        NOTE: Fixed pattern lexicon. Flags framing, not intent, and
        will fire on legitimately urgent language. A flag is a prompt
        to look, not a verdict.

        Returns:
            List of detected manipulation category names
        """
        flags = self._match_categories(text, "manipulation")
        for flag in flags:
            if flag not in self.manipulation_flags:
                self.manipulation_flags.append(flag)
        return flags

    # -------------------------
    # EVIDENCE VALIDATION
    # -------------------------

    def check_evidence_support(self, text: str) -> float:
        """
        Score statement for evidence support.

        NOTE: Marker-based. Detects the presence of sourcing language,
        not whether a source is real or correctly applied.

        Returns:
            1.0 sourcing language present
            0.8 hedged, with no unhedged assertion
            0.4 unhedged assertion with no sourcing language
            0.6 neither signal present
        """
        has_evidence = any(self._contains_term(text, m) for m in self.EVIDENCE_MARKERS)
        has_speculation = any(self._contains_term(text, m) for m in self.SPECULATION_MARKERS)
        has_strong_claims = any(self._contains_term(text, m) for m in self.STRONG_CLAIM_MARKERS)

        if has_evidence:
            return 1.0
        elif has_speculation and not has_strong_claims:
            return 0.8
        elif has_strong_claims and not has_evidence:
            return 0.4
        else:
            return 0.6

    # -------------------------
    # LOGICAL CHAIN VALIDATION
    # -------------------------

    def validate_logical_chain(
        self,
        premise: str,
        steps: List[str],
        conclusion: str
    ) -> LogicalChain:
        """
        Validate reasoning chain from premise to conclusion.

        NOTE: Structural heuristic, not entailment checking. Three
        deductions apply, all on meaning-bearing tokens:

          -0.3 fewer than two intermediate steps
          -0.2 per link that introduces nothing connected to anything
                established before it
          -0.4 conclusion shares no token with the premise

        Each link is checked against the accumulated context, not only
        against its immediate neighbor. A conclusion that ties back to
        the premise is normal reasoning and is not penalized, while a
        step that references nothing established so far is.
        """
        score = 1.0

        if len(steps) < self.MIN_STEPS:
            score -= self.PENALTY_TOO_FEW_STEPS

        seen = self._content_tokens(premise)
        for link in list(steps) + [conclusion]:
            tokens = self._content_tokens(link)
            if not (tokens & seen):
                score -= self.PENALTY_BROKEN_HOP
            seen |= tokens

        if not self._semantic_overlap(premise, conclusion):
            score -= self.PENALTY_PREMISE_CONCLUSION_GAP

        # Rounded so binary float artifacts (0.29999999999999993) do not surface.
        score = round(max(0.0, min(1.0, score)), 2)

        return LogicalChain(premise, steps, conclusion, score)

    def _semantic_overlap(self, a: str, b: str) -> bool:
        """
        Shared meaning-bearing tokens between two strings.

        Stopwords are excluded. Without that, a shared 'the' registers
        as a connection and the penalty never applies.
        """
        return bool(self._content_tokens(a) & self._content_tokens(b))

    # -------------------------
    # FALLACY DETECTION
    # -------------------------

    def detect_common_fallacies(self, reasoning_steps: List[str]) -> List[str]:
        """
        Detect common informal fallacies across a set of reasoning steps.

        NOTE: Surface pattern matching over a small taxonomy.
        Each distinct fallacy type is returned once.

        Returns:
            List of detected fallacy type names
        """
        found: List[str] = []
        for step in reasoning_steps:
            for fallacy_type in self._match_categories(step, "fallacy"):
                if fallacy_type not in found:
                    found.append(fallacy_type)
        return found

    # -------------------------
    # DIAGNOSTIC SIGNALS
    # -------------------------

    def get_diagnostic_signals(self) -> CoherenceSignals:
        """
        Get diagnostic signals (not operational scores).

        NOTE: This provides raw signals only. Production systems require
        aggregation logic, threshold definitions, governance protocols,
        and compliance reporting.
        """
        return CoherenceSignals(
            contradiction_count=len(self.detected_contradictions),
            manipulation_flags=sorted(set(self.manipulation_flags)),
            statement_count=len(self.conversation_history),
            topic_count=len(self.topic_positions)
        )

# -------------------------
# USAGE EXAMPLE
# -------------------------

def demo() -> None:
    """Basic demonstration of contradiction detection"""

    print("Logical Coherence Filter - Reference Demo\n")
    print("Demonstrating: Contradiction Detection")
    print("=" * 60)

    cf = CoherenceFilter()

    cf.add_statement(
        "The system is secure and has passed all audits",
        topic="security_status",
        confidence=0.9,
        evidence="verified"
    )

    print("\nStatement 1 (t=0):")
    print("  'The system is secure and has passed all audits'")
    print("  Topic: security_status")
    print("  Confidence: 0.9")

    consistent, issues = cf.check_consistency(
        "The system is insecure and vulnerable to attacks",
        topic="security_status"
    )

    print("\nStatement 2 (t=1):")
    print("  'The system is insecure and vulnerable to attacks'")
    print("  Topic: security_status")

    print(f"\nConsistency Check: {'PASS' if consistent else 'FAIL'}")

    if issues:
        print("Detected Issues:")
        for issue in issues:
            print(f"  - {issue}")

    signals = cf.get_diagnostic_signals()

    print("\n" + "=" * 60)
    print("Diagnostic Signals:")
    print(f"  Statements tracked: {signals.statement_count}")
    print(f"  Topics: {signals.topic_count}")
    print(f"  Contradictions: {signals.contradiction_count}")
    print(f"  Manipulation flags: {len(signals.manipulation_flags)}")


if __name__ == "__main__":
    demo()
