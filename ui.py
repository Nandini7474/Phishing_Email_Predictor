import os
import streamlit as st
import joblib
import pandas as pd
from datetime import datetime

# ---------------- Path resolution ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR = Phishing_Mail/Phishing_mail/Phishing_email

MODEL_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "modelV2", "phishing_model_v2.pkl")
)

VECTORIZER_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "modelV2", "vectorizer_v2.pkl")
)

# ---------------- Load artifacts ----------------
@st.cache_resource
def load_artifacts():
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    return model, vectorizer

#  REQUIRED: make them global
model, vectorizer = load_artifacts()


#  UI Header 
st.title("Email Classification System")
st.write("Paste an email below to analyze it.")

email_text = st.text_area("Email Content", height=200)

#  Prediction Function 
def predict_email(text, threshold=0.35):
    X = vectorizer.transform([text])
    prob = model.predict_proba(X)[0][1]
    label = "Phishing" if prob >= threshold else "Safe"
    return label, prob

#  Analyze Button
if st.button("Analyze Email", key="analyze_btn") and email_text.strip():
    prediction, probability = predict_email(email_text)

    st.session_state["prediction"] = prediction
    st.session_state["probability"] = probability
    st.session_state["email_text"] = email_text

#  Show Prediction
if "prediction" in st.session_state:
    st.subheader("Model Prediction")
    st.write(f"Prediction: **{st.session_state['prediction']}**")
    st.write(f"Phishing Probability: **{st.session_state['probability']:.2f}**")

#  Human Feedback 
if "prediction" in st.session_state:
    st.subheader("Human Feedback")

    feedback = st.radio(
        "Is this prediction correct?",
        ["Correct", "Incorrect"],
        key="feedback_radio"
    )

    if feedback == "Incorrect":
        correct_label = st.radio(
            "What is the correct label?",
            ["Safe", "Phishing"],
            key="correct_label_radio"
        )
    else:
        correct_label = st.session_state["prediction"]

    #  Save Feedback 
    if st.button("Submit Feedback", key="submit_feedback"):
        feedback_row = {
            "email_text": st.session_state["email_text"],
            "model_prediction": st.session_state["prediction"],
            "human_label": correct_label,
            "phishing_probability": st.session_state["probability"],
            "timestamp": datetime.now().isoformat()
        }

        feedback_file = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "feedback_data.csv"))
        os.makedirs("data", exist_ok=True)
        columns = [
             "email_text",
             "model_prediction",
             "human_label",
             "phishing_probability",
             "timestamp"
            ]

        if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
            df = pd.read_csv(feedback_file)
            df = pd.concat([df, pd.DataFrame([feedback_row])], ignore_index=True)
        else:
            df = pd.DataFrame([feedback_row], columns=columns)
 
        
        df.to_csv(feedback_file, index=False)
        st.success("Feedback saved successfully!")
