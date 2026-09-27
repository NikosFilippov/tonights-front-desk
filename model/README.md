---
license: cc-by-4.0
tags: [tabular-classification, xgboost, scikit-learn, teaching]
---
# Hotel cancellation model (teaching)

Predicts the probability that a hotel booking will be cancelled, from what is known **when the booking is made**.
Built in the Business Data Science programme, Aalborg University, session 10.

- **Data:** Antonio, Almeida & Nunes (2019), *Hotel booking demand datasets*, Data in Brief 22. Two Portuguese hotels, 2015–2017.
- **Model:** scikit-learn pipeline (imputation, scaling, one-hot) + XGBoost, tuned with Optuna on validation log loss.
- **Split:** by arrival date. Train to Nov 2016, validation Dec 2016–Mar 2017, test Apr–Aug 2017.
- **Test performance:** AUC 0.8102, log loss 0.5004, Brier 0.1694.
- **Removed as leakage:** required_car_parking_spaces, total_of_special_requests, booking_changes, days_in_waiting_list, room_changed, is_portugal (recorded or updated after the booking).
- **Limits:** two hotels, one country, 2015–2017; cancellations rose in 2017 and the model under-forecasts them slightly.
  Probabilities describe patterns in this data, not causes. Not for real pricing or staffing decisions.

Load with `joblib.load("model.joblib")` using the versions in `config.json`.
