from datetime import datetime

from opencost.optimizer.engine import generate_recommendations


class DummyDB:
    def __init__(self):
        self.items = []

    def scalar(self, _):
        return 10.0

    def add(self, item):
        self.items.append(item)

    def commit(self):
        return None


def test_generate_recommendations_creates_three():
    db = DummyDB()
    recs = generate_recommendations(db, period_days=30)
    assert len(recs) == 3
    assert {r.strategy_name for r in recs} == {"ultra_cheap", "balanced", "premium_safe"}
