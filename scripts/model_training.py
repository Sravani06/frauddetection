import pandas as pd
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Paths
TRAIN_FILE = os.path.join(os.getcwd(), 'data', 'train.csv')
VALIDATION_FILE = os.path.join(os.getcwd(), 'data', 'validation.csv')
MODEL_DIR = os.path.join(os.getcwd(), 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'fraud_detection_model.pkl')

#  Load train data
print(" Loading train dataset...")
try:
    train_df = pd.read_csv(TRAIN_FILE)
    print(f"Train dataset loaded successfully. Shape: {train_df.shape}")
except FileNotFoundError:
    raise FileNotFoundError(f" Train file not found at {TRAIN_FILE}. Please check the path and try again.")

#  Split features and target
if 'CLM_FRAUD_IND' not in train_df.columns:
    raise KeyError(" Target column 'CLM_FRAUD_IND' not found in training dataset.")

X_train = train_df.drop(columns=['CLM_FRAUD_IND'], errors='ignore')
y_train = train_df['CLM_FRAUD_IND']

# 🧹 Data Cleaning for Training Data
if X_train.isnull().sum().sum() > 0:
    print(" Handling missing values in training data...")
    X_train = X_train.fillna(0)

# Load validation data
print(" Loading validation dataset...")
try:
    val_df = pd.read_csv(VALIDATION_FILE)
    print(f" Validation dataset loaded successfully. Shape: {val_df.shape}")
except FileNotFoundError:
    raise FileNotFoundError(f" Validation file not found at {VALIDATION_FILE}. Please check the path and try again.")

#  Split features and target for validation
if 'CLM_FRAUD_IND' not in val_df.columns:
    raise KeyError(" Target column 'CLM_FRAUD_IND' not found in validation dataset.")

X_val = val_df.drop(columns=['CLM_FRAUD_IND'], errors='ignore')
y_val = val_df['CLM_FRAUD_IND']

# 🧹 Data Cleaning for Validation Data
if X_val.isnull().sum().sum() > 0:
    print(" Handling missing values in validation data...")
    X_val = X_val.fillna(0)

# ✨ Ensure train and validation features are consistent
missing_cols = set(X_train.columns) - set(X_val.columns)
if missing_cols:
    print(f"Warning: Columns in training but not in validation: {missing_cols}")

extra_cols = set(X_val.columns) - set(X_train.columns)
if extra_cols:
    print(f" Warning: Extra columns in validation but not in training: {extra_cols}")

X_val = X_val[X_train.columns]  # Ensure the same columns in training and validation

#  Train a RandomForestClassifier
print(" Training Random Forest Classifier...")
model = RandomForestClassifier(random_state=42, n_estimators=100, max_depth=20, n_jobs=-1)
model.fit(X_train, y_train)
print("Model training complete.")

# Evaluate on validation set
print(" Evaluating model on validation set...")
y_val_pred = model.predict(X_val)

accuracy = accuracy_score(y_val, y_val_pred)
precision = precision_score(y_val, y_val_pred)
recall = recall_score(y_val, y_val_pred)
f1 = f1_score(y_val, y_val_pred)
roc_auc = roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])

#  Print validation metrics
print(f" Validation Metrics:")
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-Score: {f1:.4f}")
print(f"ROC-AUC: {roc_auc:.4f}")

#  Save the trained model
os.makedirs(MODEL_DIR, exist_ok=True)
try:
    joblib.dump(model, MODEL_PATH)
    print(f" Model saved to {MODEL_PATH}")
except Exception as e:
    print(f" Failed to save model. Error: {e}")
