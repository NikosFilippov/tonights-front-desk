import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from portable import Model


# ============================================================
# 1. Settings
# ============================================================

st.set_page_config(
    page_title="Study Office Risk Calculator",
    page_icon="🎓",
    layout="wide",
)

MODEL_DIR = Path(__file__).resolve().parent / "model"

DATA_URL = (
    "https://raw.githubusercontent.com/aaubs/ds-master/main/"
    "assignments/study-office/data/"
)

HISTORY_URL = DATA_URL + "history_week6.csv"
NEW_URL = DATA_URL + "new_week6.csv"
GIF = {k: f"https://media.giphy.com/media/{v}/giphy.gif" for k, v in {
    "welcome": "MCudzuADLuJWw", "thinking": "WRQBXSCnEFJIuxktnw", "fire": "Z1BTGhofioRxK",
    "empty": "3oriff4xQ7Oq2TIgTu", "nailed": "8VrtCswiLDNnO", "cheers": "DfLwM9kttDFEQ",
    "pikachu": "6nWhy3ulBL7GSCvKw6", "win": "3oEduKVQdG4c0JVPSo"}.items()}
LABEL = {"lead_time": "booked {v:.0f} days ahead", "total_nights": "{v:.0f} nights", "adr": "{v:.0f} EUR a night",
         "previous_cancellations": "{v:.0f} earlier cancellations", "previous_bookings_not_canceled": "{v:.0f} earlier stays",
         "is_repeated_guest": "repeat guest: {v:.0f}", "deposit_type": "deposit: {v}", "market_segment": "segment: {v}",
         "customer_type": "customer: {v}", "agent": "agent {v}", "distribution_channel": "channel: {v}",
         "arrival_weekday": "arrival weekday {v:.0f}"}


# ============================================================
# 2. Load model, configuration and data
# ============================================================

@st.cache_resource
def load_model():
    model = Model(MODEL_DIR)

    with open(MODEL_DIR / "config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    return model, config


@st.cache_data
def load_data():
    history = pd.read_csv(HISTORY_URL)
    new = pd.read_csv(NEW_URL)

    # The notebook filled missing quiz_mean values with 0.
    # Apply the same treatment to the app data if necessary.
    if "quiz_mean" in history.columns:
        history["quiz_mean"] = history["quiz_mean"].fillna(0)

    if "quiz_mean" in new.columns:
        new["quiz_mean"] = new["quiz_mean"].fillna(0)

    return history, new


try:
    model, config = load_model()
    history, new = load_data()
except Exception as e:
    st.error("The app could not load the model or the study-office data.")
    st.exception(e)
    st.stop()


# ============================================================
# 3. Predict risk
# ============================================================

# 2025 is the validation cohort used in the notebook.
val = history[history["cohort"] == 2025].copy()

# 2026 is the current cohort: the outcome is not known yet.
new = new.copy()

val["risk"] = model.predict_proba(val)
new["risk"] = model.predict_proba(new)


# ============================================================
# 4. Helper functions
# ============================================================

def confusion_boxes(data, threshold):
    """Return TP, FP, FN and TN for a given risk threshold."""

    called = data["risk"].to_numpy() >= threshold
    truth = data["left"].to_numpy().astype(bool)

    tp = int(np.sum(called & truth))
    fp = int(np.sum(called & ~truth))
    fn = int(np.sum(~called & truth))
    tn = int(np.sum(~called & ~truth))

    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
    }


def safe_ratio(a, b):
    return a / b if b else 0.0


def group_name(value):
    return "International" if int(value) == 1 else "Domestic"


def model_explanation(row):
    """
    Use the XGBoost contribution values to show which original
    features push this student's prediction upward.

    Positive contribution = pushes predicted risk upward.
    Negative contribution = pushes predicted risk downward.
    """

    one_row = row.to_frame().T

    contributions = model.contributions(one_row).iloc[0]

    positive = (
        contributions[contributions > 0]
        .sort_values(ascending=False)
    )

    negative = (
        contributions[contributions < 0]
        .sort_values()
    )

    return positive, negative


def readable_signal(feature, value):
    """Turn a few important variables into plain-language descriptions."""

    if feature == "fees_owed" and value == 1:
        return "Fees are owed."

    if feature == "submitted_share" and value < 0.5:
        return f"Only {value:.0%} of assignments have been submitted."

    if feature == "logins_last3" and value < 5:
        return f"Only {value:.0f} logins were recorded in the last three weeks."

    if feature == "logins_trend" and value < 0:
        return "Login activity is decreasing."

    if feature == "missed_last3" and value >= 2:
        return f"{value:.0f} activities were missed in the last three weeks."

    if feature == "weeks_since_login" and value >= 1:
        return f"The student has not logged in for {value:.0f} week(s)."

    if feature == "quiz_mean" and value < 50:
        return f"The average quiz score is {value:.1f}."

    return None


# ============================================================
# 5. Header
# ============================================================

st.title("🎓 Student Support Risk Calculator")

st.markdown(
    """
    This dashboard helps the study office identify students who may
    benefit from an early conversation.

    **Important:** the model gives a risk estimate. It does not decide
    that a student will leave, and a staff member should make the final
    decision about contacting a student.
    """
)
col1, col2, col3 = st.columns(3)
with col3:
    st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTc0OThqdmV6bW11M3Jtc2VtNGN0dmYzOGRrdWpqOTI4dnI1OHBwbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kGuY7LXCNbUyCFbiNm/giphy.gif", width=300)


# ============================================================
# 6. Recommended rule
# ============================================================

recommended_threshold = float(config.get("call_threshold", 0.24))

st.subheader("1. Decision rule")

st.write(
    f"The cost-based rule selected in the notebook is a "
    f"**{recommended_threshold:.0%} risk threshold**."
)

threshold = st.slider(
    "Risk threshold",
    min_value=0.05,
    max_value=0.95,
    value=round(recommended_threshold, 2),
    step=0.01,
    help=(
        "Students at or above this predicted risk are considered "
        "for contact."
    ),
)

boxes = confusion_boxes(val, threshold)

contacts = boxes["TP"] + boxes["FP"]
precision = safe_ratio(boxes["TP"], contacts)
recall = safe_ratio(boxes["TP"], boxes["TP"] + boxes["FN"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Students contacted", f"{contacts:,}")
col2.metric("Reached in time", f"{boxes['TP']:,}")
col3.metric("Worried for nothing", f"{boxes['FP']:,}")
col4.metric("Missed", f"{boxes['FN']:,}")

st.markdown("### What do these numbers mean?")

st.info(
    f"""
    **Reached in time:** {boxes['TP']} students who later left were
    identified by the rule.

    **Worried for nothing:** {boxes['FP']} students who stayed would
    have been contacted unnecessarily.

    **Missed:** {boxes['FN']} students who later left were not flagged.

    **Precision:** {precision:.1%} of the students contacted actually left.

    **Recall:** the rule identifies {recall:.1%} of all students who later left.
    """
)

st.caption(
    "These numbers are evaluated on the 2025 cohort, where the actual "
    "outcome is known."
)


# ============================================================
# 7. This week's students — top 40
# ============================================================

st.subheader("2. This week's students")

st.write(
    "The model ranks the 2026 students by predicted risk. "
    "The assignment asks the office to focus on the 40 highest-risk students."
)

top40 = new.nlargest(min(40, len(new)), "risk").copy()
top40.insert(0, "Rank", range(1, len(top40) + 1))

top40_display = top40[
    [
        "Rank",
        "student_id",
        "risk",
        "international",
        "programme",
        "logins_last3",
        "submitted_share",
        "missed_last3",
        "fees_owed",
    ]
].copy()

top40_display["Risk"] = top40_display.pop("risk")
top40_display["International"] = top40_display.pop("international").map(
    {0: "Domestic", 1: "International"}
)
top40_display["Fees owed"] = top40_display.pop("fees_owed").map(
    {0: "No", 1: "Yes"}
)

top40_display = top40_display.rename(
    columns={
        "student_id": "Student",
        "programme": "Programme",
        "logins_last3": "Logins last 3 weeks",
        "submitted_share": "Submitted share",
        "missed_last3": "Missed last 3",
    }
)

st.dataframe(
    top40_display.style.format(
        {
            "Risk": "{:.1%}",
            "Submitted share": "{:.0%}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "A high risk is a reason to consider a conversation, not a final "
    "judgement about the student."
)


# ============================================================
# 8. Fairness: international vs domestic students
# ============================================================

st.subheader("3. Fair to whom?")

st.write(
    """
    The same rule is checked separately for domestic and international
    students. This helps the study office see whether the model's
    mistakes are very different between the two groups.
    """
)

# Top-40 indicator, exactly following the notebook's fairness analysis.
val["top40"] = (
    val["risk"].rank(ascending=False, method="first") <= min(40, len(val))
)

group_rows = []

for group_value in [0, 1]:
    group = val[val["international"] == group_value]

    group_boxes = confusion_boxes(group, threshold)

    group_top40 = group[group["left"] == 1]["top40"].mean()

    group_rows.append(
        {
            "Group": group_name(group_value),
            "Students": len(group),
            "Actually left": group["left"].mean(),
            "Average predicted risk": group["risk"].mean(),
            "Reached in time": group_boxes["TP"],
            "Worried for nothing": group_boxes["FP"],
            "Missed": group_boxes["FN"],
            "Top-40 recall": group_top40,
            "Average total logins": group["logins_total"].mean(),
        }
    )

fairness = pd.DataFrame(group_rows)

st.dataframe(
    fairness.style.format(
        {
            "Actually left": "{:.1%}",
            "Average predicted risk": "{:.1%}",
            "Top-40 recall": "{:.1%}",
            "Average total logins": "{:.1f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "The notebook also found different average login activity between "
    "the two groups, so a login should not automatically be interpreted "
    "as the same signal for every student."
)


# ============================================================
# 9. Extra feature: inspect one student
# ============================================================

st.subheader("4. Inspect a student")

st.write(
    "Select a student to see the model risk and the features that "
    "contribute most strongly to the prediction."
)

student_ids = top40["student_id"].astype(str).tolist()

selected_id = st.selectbox(
    "Student",
    student_ids,
)

selected = new[new["student_id"].astype(str) == selected_id].iloc[0]

left, right = st.columns([1, 2])

with left:
    st.metric(
        "Predicted risk",
        f"{selected['risk']:.1%}",
    )

    st.write(
        f"**Programme:** {selected['programme']}"
    )

    st.write(
        f"**Student group:** {group_name(selected['international'])}"
    )

    st.write(
        f"**Age:** {selected['age']}"
    )

with right:
    st.markdown("### Model signals")

    try:
        positive, negative = model_explanation(selected)

        if len(positive) > 0:
            st.write("**Features pushing risk upward:**")

            shown = 0

            for feature, contribution in positive.items():
                value = selected[feature]
                signal = readable_signal(feature, value)

                if signal is not None:
                    st.write(
                        f"- {signal} "
                        f"(`{feature}`, contribution {contribution:.2f})"
                    )
                else:
                    st.write(
                        f"- `{feature}` contributes positively "
                        f"({contribution:.2f})"
                    )

                shown += 1

                if shown >= 4:
                    break

        if len(negative) > 0:
            st.write("**Features pushing risk downward:**")

            shown = 0

            for feature, contribution in negative.items():
                st.write(
                    f"- `{feature}` contributes negatively "
                    f"({contribution:.2f})"
                )

                shown += 1

                if shown >= 3:
                    break

        st.caption(
            "These are model contributions, not causal explanations. "
            "They show which features pushed this prediction up or down."
        )

    except Exception as e:
        st.warning(
            "The student's risk was calculated, but the contribution "
            "explanation could not be displayed."
        )


# ============================================================
# 10. Method information
# ============================================================

with st.expander("About the model"):
    st.write(
        "The model was trained on the 2023 and 2024 cohorts and "
        "validated on the 2025 cohort."
    )

    st.write(
        f"**Model:** {config.get('model', 'study-office-dropout-xgb')}"
    )

    st.write(
        f"**Validation AUC:** "
        f"{config.get('metrics_test', {}).get('auc', float('nan')):.3f}"
    )

    st.write(
        f"**Cost-based threshold from notebook:** "
        f"{recommended_threshold:.0%}"
    )

    st.write(
        "The current 2026 students are scored using information "
        "available at week 6. The later outcome is not used by the app."
    )

    st.warning(
        "This should be used as decision support. A human at the study "
        "office should decide whether and how to contact a student."
    )
