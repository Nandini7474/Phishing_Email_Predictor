import pandas as pd
import joblib
import os
from datetime import datetime

# ---------------- Path resolution ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR = Phishing_Mail/Phishing_mail

MODEL_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "modelV1", "phase1_phishing_text_model.pkl")
)

VECTORIZER_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "modelV1", "phase1_tfidf_vectorizer.pkl")
)



PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

TEST_DATA_PATH = os.path.join(DATA_DIR, "test_dataset1.csv")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback_data.csv")
print("TEST_DATA_PATH:", TEST_DATA_PATH)
print("MODEL_PATH:", MODEL_PATH)

# ---------------- Safety checks ----------------
assert os.path.exists(MODEL_PATH), f"Model not found: {MODEL_PATH}"
assert os.path.exists(VECTORIZER_PATH), f"Vectorizer not found: {VECTORIZER_PATH}"
assert os.path.exists(TEST_DATA_PATH), f"Test data not found: {TEST_DATA_PATH}"

# ---------------- Load model & vectorizer ----------------
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# ---------------- Load test dataset ----------------
test_df = pd.read_csv(TEST_DATA_PATH)

# Normalize column names (VERY IMPORTANT)
test_df.columns = test_df.columns.str.strip().str.lower()

# Rename if needed
test_df = test_df.rename(columns={
    "body": "email_text",
    "email": "email_text",
    "email type": "label"
})

# Ensure numeric labels
test_df["label"] = test_df["label"].map({
    "safe email": 0,
    "phishing email": 1,
    0: 0,
    1: 1
})

test_df = test_df.dropna(subset=["email_text", "label"])

# ---------------- Predict ----------------
X_test = vectorizer.transform(test_df["email_text"])
probs = model.predict_proba(X_test)[:, 1]

THRESHOLD = 0.35
test_df["model_prediction"] = (probs >= THRESHOLD).astype(int)
test_df["phishing_probability"] = probs

# ---------------- Identify incorrect predictions ----------------
# ---------------- Identify incorrect predictions ----------------
feedback_df = test_df[
    test_df["model_prediction"] != test_df["label"]
].copy()




feedback_df = feedback_df[
    [
        "email_text",
        "model_prediction",
        "label",
        "phishing_probability"
    ]
]

# ---------------- Append to feedback CSV ----------------
os.makedirs(DATA_DIR, exist_ok=True)

columns = [
    "email_text",
    "model_prediction",
    "label",
    "phishing_probability"
]

if os.path.exists(FEEDBACK_PATH) and os.path.getsize(FEEDBACK_PATH) > 0:
    existing = pd.read_csv(FEEDBACK_PATH)
    feedback_df = pd.concat([existing, feedback_df], ignore_index=True)
else:
    feedback_df = pd.DataFrame(feedback_df, columns=columns)

feedback_df.to_csv(FEEDBACK_PATH, index=False)

print(f"Feedback samples stored: {len(feedback_df)}")
print(f"Saved to: {FEEDBACK_PATH}")
