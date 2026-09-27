# 🛎️ Tonight's front desk

An overbooking game for the MSc Business Data Science programme at Aalborg University (module 1, session 10).
Five real nights at a Lisbon city hotel: how many extra rooms do you sell, knowing some guests will cancel?
You play against the model and against Gut Feeling Gus.

**Play:** https://tonights-front-desk.streamlit.app

## How it is put together

| Piece | Where |
|---|---|
| App code | `app.py` (Streamlit), this repo |
| Environment | `requirements.txt`, versions pinned to match the model |
| Model (registry) | [AAUBS/hotel-cancellation-model](https://huggingface.co/AAUBS/hotel-cancellation-model) on the Hugging Face Hub, downloaded at start-up |
| Hosting | Streamlit Community Cloud, rebuilt on every push to `main` |

## Make it yours

1. Fork this repo.
2. On [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, **Create app**, pick your fork and `app.py`.
   Under *Advanced settings* choose **Python 3.12**.
3. Change something in `app.py`, commit, and watch the app redeploy.
4. Optional: publish your own model from the session 10 notebook and set `MODEL_REPO = "you/your-model"` in the app's
   **Secrets** (Settings → Secrets). Keep `requirements.txt` on the versions in your `config.json`.

Run locally: `pip install -r requirements.txt && streamlit run app.py`.

Data: Antonio, Almeida & Nunes (2019), *Hotel booking demand datasets*, Data in Brief 22. Memes embedded from GIPHY.
