# 🛎️ Tonight's front desk

An overbooking game for the MSc Business Data Science programme at Aalborg University (module 1, session 10).

**Play:** https://tonights-front-desk.streamlit.app

## How it is put together

| Piece | Where |
|---|---|
| App code | `app.py` (Streamlit), this repo |
| Environment | `requirements.txt`: four packages, no version pins |
| Model | `model/`: `booster.json` (XGBoost's own format) + `preprocess.json` (scaling and one-hot as plain numbers), `config.json` with metrics, and the model card (`README.md`). Loaded by `portable.py`, no pickle, so any Python version works |
| Hosting | Streamlit Community Cloud, rebuilt on every push to `main` |

 Memes embedded from GIPHY.
