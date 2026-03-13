from opencost.pricing.engine import estimate_cost


class DummyPrice:
    input_per_1k_usd = 1.0
    output_per_1k_usd = 2.0
    cached_input_per_1k_usd = 0.5


class DummyDB:
    def scalar(self, _):
        return DummyPrice()


def test_estimate_cost_basic():
    cost = estimate_cost(DummyDB(), "openai", "gpt", 1000, 1000, 1000)
    assert cost == 3.5
