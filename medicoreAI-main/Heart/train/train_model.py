import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# ==============================
# PATH SETUP (IMPORTANT)
# ==============================

# Get root directory (heart_module)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset path
data_path = os.path.join(BASE_DIR, "DataSets", "heart_disease_cleaned.csv")

# Model save path
model_dir = os.path.join(BASE_DIR, "models")
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "heart_attack_model.pkl")

# ==============================
# LOAD DATA
# ==============================

df = pd.read_csv(data_path)

# ==============================
# SPLIT DATA
# ==============================

X = df.drop("target", axis=1)
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ==============================
# TRAIN MODEL
# ==============================

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ==============================
# EVALUATION
# ==============================

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print("Accuracy:", round(acc, 4))

# ==============================
# SAVE MODEL
# ==============================

joblib.dump(model, model_path)

print("✅ Model saved at:", model_path)