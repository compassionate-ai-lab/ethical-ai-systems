"""Educational companion to Ethical AI Systems (revised expanded edition, 2026).

Standard library only. This module evaluates proposed policies; it does
not provide authentication, concurrent transaction safety, durable budget
storage or tamper-evident logging. Production enforcement belongs outside
the model.

Run: python ethical_ai_toolkit.py
"""
from __future__ import annotations

__version__ = "1.0.0"
from dataclasses import dataclass, field, asdict
from decimal import Decimal, InvalidOperation
from math import isfinite
from statistics import mean
from typing import Mapping, Sequence

INDEX_WEIGHTS = {
    "cage": .08, "traps": .10, "bias": .16,
    "hostility": .10, "diversity": .10,
    "collection": .10, "transparency": .12,
    "anonymisation": .08, "augmentation": .06,
    "oversight": .10,
}
FLOOR = 40.0
RELEASE_THRESHOLD = 75.0


def finite_number(value, lo, hi, name):
    if (isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value) or not lo <= value <= hi):
        raise ValueError(f"invalid {name}")
    return float(value)


def check_scores(scores, not_applicable=()):
    excluded = set(not_applicable)
    if not excluded <= set(INDEX_WEIGHTS):
        raise ValueError("unknown N/A index")
    expected = set(INDEX_WEIGHTS) - excluded
    if not expected or set(scores) != expected:
        raise ValueError(
            "score keys must match applicable indexes")
    for key, value in scores.items():
        finite_number(value, 0, 100, key)


def composite(scores, not_applicable=()):
    """Renormalise only documented, approved N/A exclusions."""
    check_scores(scores, not_applicable)
    weight = sum(INDEX_WEIGHTS[k] for k in scores)
    return round(sum(INDEX_WEIGHTS[k] * scores[k]
                     for k in scores) / weight, 2)


@dataclass
class Assessment:
    scores: Mapping[str, float]
    not_applicable: tuple[str, ...] = ()
    floor: float = FLOOR
    threshold: float = RELEASE_THRESHOLD
    evidence_complete: bool = False
    mandatory_gates_passed: bool = False

    def __post_init__(self):
        self.scores = dict(self.scores)
        self.not_applicable = tuple(self.not_applicable)
        self._validate()

    def _validate(self):
        check_scores(self.scores, self.not_applicable)
        finite_number(self.floor, 0, 100, "floor")
        finite_number(self.threshold, 0, 100, "threshold")
        if (type(self.evidence_complete) is not bool
                or type(self.mandatory_gates_passed)
                is not bool):
            raise ValueError("gates must be booleans")

    @property
    def composite(self):
        self._validate()
        return composite(self.scores, self.not_applicable)

    @property
    def blocking(self):
        self._validate()
        return sorted(k for k, v in self.scores.items()
                      if v < self.floor)

    @property
    def release(self):
        # A passing numerical score never overrides missing
        # evidence
        # or a failed legal, rights, authorisation or safety
        # gate.
        return (not self.blocking
                and self.composite >= self.threshold
                and self.evidence_complete
                and self.mandatory_gates_passed)

    def summary(self):
        state = "POLICY PASS" if self.release else "HOLD"
        return f"{state}: composite {self.composite:.2f}"


# Impact: 0 low, 1 moderate, 2 high.
# Reversibility: 0 full, 1 partial, 2 irreversible.
MAX_RUNG = {0: {0: 4, 1: 3, 2: 1},
            1: {0: 3, 1: 2, 2: 1},
            2: {0: 1, 1: 1, 2: 1}}
RUNG_NAMES = {0: "suggest", 1: "approve to act",
              2: "act and report", 3: "act within limits",
              4: "bounded end-to-end autonomy"}


def integer_range(value, lo, hi, name):
    if type(value) is not int or not lo <= value <= hi:
        raise ValueError(f"invalid {name}")


def allowed_rung(impact, reversibility):
    """Upper bound only; prohibited actions remain prohibited."""
    integer_range(impact, 0, 2, "impact")
    integer_range(reversibility, 0, 2, "reversibility")
    return MAX_RUNG[impact][reversibility]


def permits(rung, impact, reversibility):
    integer_range(rung, 0, 4, "rung")
    return rung <= allowed_rung(impact, reversibility)


def money(value):
    """Exact nonnegative amount, to at most two decimal
    places."""
    if isinstance(value, bool):
        raise ValueError("invalid money")
    try:
        result = Decimal(str(value))
        if (not result.is_finite() or result < 0
                or result != result.quantize(Decimal("0.01"))):
            raise ValueError("invalid money")
    except (InvalidOperation, ValueError):
        raise ValueError("invalid money") from None
    return result


@dataclass
class Envelope:
    """Single-process budget reservation demo; no payments
    executed.

    All amounts use one declared currency. An upstream trusted
    service
    must authenticate confirmation for the exact proposed
    transaction.
    Successful authorisation reserves budget. Release of
    reservations
    and settlement are deliberately outside this teaching
    example.
    """
    spend_cap: object
    recipients: Sequence[str]
    confirm_above: object
    currency: str = "INR"
    allow_identity_sharing: bool = False
    revoked: bool = False
    spent: Decimal = field(init=False, default=Decimal("0"))
    _accepted: dict = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.spend_cap = money(self.spend_cap)
        self.confirm_above = money(self.confirm_above)
        if self.confirm_above > self.spend_cap:
            raise ValueError("confirmation limit exceeds cap")
        if (not isinstance(self.currency, str)
                or len(self.currency) != 3):
            raise ValueError("declare one currency")
        if (isinstance(self.recipients, str)
                or not self.recipients
                or any(not isinstance(r, str) or not r.strip()
                       for r in self.recipients)):
            raise ValueError(
                "recipients must be nonempty identifiers")
        self.recipients = tuple(self.recipients)
        if (type(self.allow_identity_sharing) is not bool
                or type(self.revoked) is not bool):
            raise ValueError("flags must be booleans")

    def authorise(self, action_id, amount, recipient,
                  shares_identity=False, confirmed=False):
        if (not isinstance(action_id, str)
                or not action_id.strip()):
            raise ValueError("action_id required")
        amount = money(amount)
        if (type(shares_identity) is not bool
                or type(confirmed) is not bool):
            raise ValueError("flags must be booleans")
        request = (amount, recipient, shares_identity)
        if action_id in self._accepted:
            if self._accepted[action_id] != request:
                raise ValueError(
                    "action_id reused for different action")
            # Never return a new authorisation to execute a
            # retry.
            return {"allowed": False,
                    "reason": ("already reserved; "
                               "reconcile by action_id")}
        if self.revoked:
            return {"allowed": False, "reason": "revoked"}
        if recipient not in self.recipients:
            return {"allowed": False,
                    "reason": "recipient not allowed"}
        if shares_identity and not self.allow_identity_sharing:
            return {"allowed": False,
                    "reason": "identity not allowed"}
        if self.spent + amount > self.spend_cap:
            return {"allowed": False,
                    "reason": "cumulative cap exceeded"}
        if amount > self.confirm_above and not confirmed:
            return {"allowed": False,
                    "reason": "confirmation required"}
        self.spent += amount
        self._accepted[action_id] = request
        return {"allowed": True, "reason": "budget reserved"}


def validate_binary(values, name):
    if not values or any(type(v) is not int or v not in (0, 1)
                         for v in values):
        raise ValueError(
            f"{name} must be a nonempty binary sequence")


def validate_groups(groups, length):
    if len(groups) != length or any(
            not isinstance(g, str) or not g.strip()
            for g in groups):
        raise ValueError("invalid group identifiers or lengths")


def selection_rates(predictions, groups):
    validate_binary(predictions, "predictions")
    validate_groups(groups, len(predictions))
    return {
        g: mean(p for p, gg in zip(predictions, groups)
                if gg == g)
        for g in sorted(set(groups))
    }


def demographic_parity_difference(predictions, groups):
    """Max minus min group selection rate (not rate minus
    overall)."""
    rates = selection_rates(predictions, groups)
    if len(rates) < 2:
        raise ValueError("need at least two groups")
    return max(rates.values()) - min(rates.values())


def true_positive_rates(labels, predictions, groups):
    validate_binary(labels, "labels")
    validate_binary(predictions, "predictions")
    if len(predictions) != len(labels):
        raise ValueError("length mismatch")
    validate_groups(groups, len(labels))
    out = {}
    for g in sorted(set(groups)):
        rows = [
            p for y, p, gg in zip(labels, predictions, groups)
            if gg == g and y == 1
        ]
        # Undefined is explicit, never silently dropped.
        out[g] = mean(rows) if rows else None
    return out


def equal_opportunity_gap(labels, predictions, groups):
    rates = true_positive_rates(labels, predictions, groups)
    if len(rates) < 2 or any(v is None for v in rates.values()):
        raise ValueError(
            "need positives in each of at least two groups")
    return max(rates.values()) - min(rates.values())


def calibration_by_group(scores, labels, groups, bins=5):
    validate_binary(labels, "labels")
    validate_groups(groups, len(labels))
    if len(scores) != len(labels):
        raise ValueError("length mismatch")
    integer_range(bins, 1, 10000, "bins")
    for s in scores:
        finite_number(s, 0, 1, "probability")
    out = {}
    for g in sorted(set(groups)):
        for b in range(bins):
            rows = [
                (s, y)
                for s, y, gg in zip(scores, labels, groups)
                if gg == g
                and min(int(s * bins), bins - 1) == b
            ]
            if rows:
                out[f"{g}:bin{b}"] = {
                    "mean_score": mean(s for s, _ in rows),
                    "observed_rate": mean(y for _, y in rows),
                    "count": len(rows),
                }
    return out


@dataclass
class ActionRecord:
    action_id: str
    timestamp_utc: str
    actor: str
    operator: str
    tool: str
    authority: str
    effect: str
    model_version: str
    approved_by: str = ""
    metadata: dict = field(default_factory=dict)

    def is_complete(self):
        fields = ("action_id", "timestamp_utc", "actor",
                  "operator",
                  "tool", "authority", "effect", "model_version")
        return all(isinstance(getattr(self, k), str)
                   and getattr(self, k).strip() for k in fields)

    def as_dict(self):
        # Metadata remains nested; it cannot overwrite identity
        # fields.
        return asdict(self)


def _selftest():
    scores = dict(zip(INDEX_WEIGHTS,
                      [55, 71, 62, 83, 58, 74, 66, 80, 70, 52]))
    assert composite(scores) == 66.64
    assert not Assessment(scores).release
    assert allowed_rung(2, 0) == 1
    env = Envelope(40000, ["airline"], 25000)
    assert env.authorise("a1", 12000, "airline")["allowed"]
    assert not env.authorise("a1", 12000, "airline")["allowed"]
    assert not env.authorise("a2", 30000, "airline")["allowed"]
    assert env.spent == Decimal("12000")
    print("ethical_ai_toolkit: self-tests passed")


if __name__ == "__main__":
    _selftest()
