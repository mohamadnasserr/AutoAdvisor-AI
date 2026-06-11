# Tasks - Intent Classifier

- [x] Implement rule-based intent baseline.
- [x] Create labeled intent training dataset.
- [x] Train TF-IDF + Logistic Regression intent classifier.
- [x] Save model artifact to `models/intent_classifier.joblib`.
- [x] Integrate ML classifier into `intent_service`.
- [x] Keep rule-based fallback if model is missing or low confidence.
- [x] Add classifier confidence helper.
- [x] Add tests for all supported intents.
- [x] Add test for fallback rule-based classifier.

## Verification

- Intent training result: accuracy around 0.867, macro F1 around 0.87.
- `python -m pytest tests\test_intent_classifier.py` -> 8 passed.
- `python -m pytest tests` -> all tests passed.
