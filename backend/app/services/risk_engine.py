from dataclasses import dataclass

# Prototype thresholds only. Final thresholds MUST be selected from validated model calibration.
THRESHOLDS = {"low_max": 0.30, "moderate_max": 0.55, "high_max": 0.75}

@dataclass
class RiskResult:
    probability: float
    risk_level: str


def classify_probability(probability: float) -> str:
    p = max(0.0, min(1.0, float(probability)))
    if p >= THRESHOLDS["high_max"]:
        return "critical"
    if p >= THRESHOLDS["moderate_max"]:
        return "high"
    if p >= THRESHOLDS["low_max"]:
        return "moderate"
    return "low"
