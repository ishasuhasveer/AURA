from decision_intelligence.spec_matching.comparators import (
    exact_match,
    numeric_match
)


def test_exact_match():
    assert exact_match("COPPER", "COPPER") == 1.0
    assert exact_match("COPPER", "ALUMINIUM") == 0.0
    assert exact_match(None, "COPPER") is None
    assert exact_match("COPPER", None) == 0.0


def test_numeric_match():
    assert numeric_match(50, 50) == 1.0
    assert numeric_match(50, 70) == 0.5
    assert numeric_match(50, 35) == 0.0
    assert numeric_match(None, 50) is None
    assert numeric_match(50, None) == 0.0
