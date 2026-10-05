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

## Make it yours

1. Fork this repo.
2. On [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, **Create app**, pick your fork and `app.py`.
   Any Python version works.
3. Change something in `app.py`, commit, and watch the app redeploy.
4. Optional: train your own model with the session 10 notebook, download its `hotel_model` folder, and replace the
   files in `model/`. The notebook's download cell writes the portable files.

Run locally: `pip install -r requirements.txt && streamlit run app.py`.

Data: Antonio, Almeida & Nunes (2019), *Hotel booking demand datasets*, Data in Brief 22. Memes embedded from GIPHY.
