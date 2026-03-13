from opencost.classification.heuristics import classify_event


def test_classify_coding():
    category, confidence, _ = classify_event({"text": "refactor python bug"})
    assert category == "coding"
    assert confidence > 0.5
