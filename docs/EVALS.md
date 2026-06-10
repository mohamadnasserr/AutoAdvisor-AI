# Evaluations

| Component | Primary Metrics | Initial Target |
| --- | --- | --- |
| Intent classifier | Accuracy, macro-F1 | At least 80% accuracy |
| Preference extraction | Valid JSON, field accuracy | 95% valid JSON, 80% key fields |
| Price estimator | MAE, RMSE | Report baseline and selected model |
| RAG retrieval | hit@3, hit@5, MRR | hit@3 70%, hit@5 80% |
| Image safety and quality | Pass/fail review | Block unsafe images and flag poor images |
| Recommendations | Manual scenario rubric | At least 8 of 10 scenarios pass |
