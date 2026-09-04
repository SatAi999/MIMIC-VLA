import pytest
from backend.evaluation.resilience import ResilienceTestSuite

def test_resilience_test_suite():
    suite = ResilienceTestSuite()
    results = suite.run_all_tests()
    assert len(results) == 10
    for r in results:
        assert r["result"] == "PASS"
        assert r["safety_violations"] == 0
