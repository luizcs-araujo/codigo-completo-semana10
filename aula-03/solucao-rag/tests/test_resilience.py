import pytest
from supportops.resilience import CircuitBreaker, CircuitOpenError


def test_circuit_breaker_opens_after_threshold():
    breaker = CircuitBreaker(failure_threshold=2, recovery_seconds=999)
    breaker.failure(); breaker.before_call()
    breaker.failure()
    with pytest.raises(CircuitOpenError):
        breaker.before_call()
