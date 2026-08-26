"""HST-213 — drift_detector competency logic, tested against the locked pass-3 spec.

Representative corpus (>=8 cases incl. edge/adversarial). The rule under test is
pure (src/shared/drift_policy.evaluate_drift), so these assertions pin the domain
behaviour without the runtime/pydantic stack.
"""
from src.shared.drift_policy import evaluate_drift, drift_urgency_score


def _status(v, name):
    return next(s["status"] for s in v["signals"] if s["name"] == name)


def test_all_clear_no_proposal():
    v = evaluate_drift({"eval_score": 0.92, "eval_threshold": 0.80, "promotion_score": 0.92,
                        "psi": 0.05, "new_rows": 10, "age_days": 3})
    assert v["proposal"] is None
    assert v["cannot_assess"] == []
    assert drift_urgency_score({"eval_score": 0.92, "eval_threshold": 0.80,
                                "promotion_score": 0.92, "psi": 0.05,
                                "new_rows": 10, "age_days": 3}) == 0.0


def test_eval_regression_near_threshold_fires_high():
    # score 0.83 < threshold(0.80) + 0.05 = 0.85 -> fires
    v = evaluate_drift({"eval_score": 0.83, "eval_threshold": 0.80, "promotion_score": 0.90})
    assert _status(v, "eval_regression") == "fired"
    assert v["proposal"]["tier"] == "T2" and v["proposal"]["auto"] is False
    assert v["proposal"]["urgency"] == "high"


def test_eval_regression_by_drop_from_promotion():
    # 0.87 clears (thr+0.05=0.85) but is 0.04 under promotion 0.91 -> fires on the drop rule
    v = evaluate_drift({"eval_score": 0.87, "eval_threshold": 0.80, "promotion_score": 0.91})
    assert _status(v, "eval_regression") == "fired"
    assert v["proposal"] is not None


def test_input_drift_moderate_fires_medium():
    v = evaluate_drift({"psi": 0.22})
    assert _status(v, "input_drift") == "fired"
    assert v["proposal"]["urgency"] == "medium"


def test_input_drift_severe_fires_high():
    v = evaluate_drift({"psi": 0.27})
    assert v["proposal"]["urgency"] == "high"


def test_new_governed_data_fires_low():
    v = evaluate_drift({"new_rows": 600})
    assert _status(v, "new_governed_data") == "fired"
    assert v["proposal"]["urgency"] == "low"


def test_age_alone_never_triggers():
    # >90d old but every other signal is clean -> age must NOT fire, no proposal.
    v = evaluate_drift({"eval_score": 0.95, "eval_threshold": 0.80, "promotion_score": 0.95,
                        "psi": 0.02, "new_rows": 5, "age_days": 365})
    assert _status(v, "age") == "clear"
    assert v["proposal"] is None


def test_age_cofires_when_another_signal_marginal():
    # eval marginal (0.86 in [0.85, 0.87)) + >90d -> age co-fires; eval itself stays marginal.
    v = evaluate_drift({"eval_score": 0.86, "eval_threshold": 0.80, "promotion_score": 0.88,
                        "psi": 0.05, "new_rows": 5, "age_days": 120})
    assert _status(v, "eval_regression") == "marginal"
    assert _status(v, "age") == "fired"
    assert v["proposal"] is not None and v["proposal"]["urgency"] == "low"


def test_cannot_assess_not_reported_as_clear():
    # No eval inputs and no PSI -> those signals are cannot_assess, never a fabricated clear.
    v = evaluate_drift({"new_rows": 10, "age_days": 5})
    assert _status(v, "eval_regression") == "cannot_assess"
    assert _status(v, "input_drift") == "cannot_assess"
    assert set(v["cannot_assess"]) == {"eval_regression", "input_drift"}
    assert v["proposal"] is None  # nothing fired


def test_adversarial_nan_and_negative_do_not_fabricate_drift():
    nan = float("nan")
    v = evaluate_drift({"psi": nan, "new_rows": -50, "eval_score": nan, "eval_threshold": 0.8})
    assert _status(v, "input_drift") == "cannot_assess"   # NaN PSI is not "no drift"
    assert _status(v, "eval_regression") == "cannot_assess"
    assert _status(v, "new_governed_data") == "clear"      # negative rows -> not a trigger
    assert v["proposal"] is None


def test_determinism_same_input_same_output():
    inp = {"eval_score": 0.83, "eval_threshold": 0.80, "psi": 0.22, "new_rows": 600, "age_days": 200}
    assert evaluate_drift(inp) == evaluate_drift(dict(inp))
