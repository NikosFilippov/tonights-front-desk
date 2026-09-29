"""One-off: convert model/model.joblib into the portable files and check they predict exactly the same.
Needs the training versions (scikit-learn 1.6.1 etc.).   python export_portable.py"""
import json
import joblib, numpy as np, pandas as pd
import xgboost as xgb
from portable import Model, export

pipe = joblib.load("model/model.joblib")
export(pipe, "model")
cfg = json.load(open("model/config.json"))
test = pd.read_parquet("model/test_bookings.parquet")
X = test[cfg["numeric_features"] + cfg["categorical_features"]]
m = Model("model")
a, b = pipe.predict_proba(X)[:, 1], m.predict_proba(X)
odd = X.head(3).assign(meal="Pizza", agent="99999", adr=np.nan)                 # unseen levels + a missing number
assert np.allclose(pipe.predict_proba(odd)[:, 1], m.predict_proba(odd), atol=1e-6)
assert np.allclose(a, b, atol=1e-6), np.abs(a - b).max()
print(f"portable model matches the pipeline on {len(X):,} test bookings (max diff {np.abs(a - b).max():.1e})")
