# model_inference.py
import joblib

model = joblib.load("modelV2/phishing_model_v2.pkl")
vectorizer = joblib.load("modelV2/vectorizer_v2.pkl")

def predict_email(text):
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0][1]
    return pred, prob
