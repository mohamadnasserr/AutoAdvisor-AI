# Tasks - Used-Car Price Estimator

- [x] Add public used-car dataset locally under `data/raw/`.
- [x] Train used-car price estimator using the CarDekho dataset.
- [x] Convert selling price from INR to USD using a fixed demo conversion rate.
- [x] Train Random Forest regression model.
- [x] Save model artifact to `models/used_car_price_estimator.joblib`.
- [x] Store model metadata including MAE, R2, source currency, target currency,
  and features.
- [x] Add price estimator service.
- [x] Add used-car price prediction schemas.
- [x] Add `/price/used-car` endpoint.
- [x] Return estimated price, low estimate, high estimate, model MAE, model R2,
  currency, and disclaimer.
- [x] Add tests for successful price prediction.
- [x] Add tests for required-field validation.
- [ ] Define preprocessing and leakage controls.
- [ ] Report deeper failure examples and segment-level model performance.
- [ ] Calibrate the public non-local dataset for Lebanon/MENA market pricing.

## Important Notes

- This estimator predicts used-car prices only.
- New cars are not predicted by this ML model.
- The CarDekho dataset is public and non-local; Lebanon/MENA calibration is a
  future improvement.

## Verification

- Training rows used: 15,411.
- Training result: MAE around $1,206.86, R2 around 0.932.
- `python -m pytest tests\test_price_estimator.py` -> 2 passed.
- `python -m pytest tests` -> 32 passed.
