import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder

# Step 1: Load the data
print("Loading the fraud dataset...")
file_path = '/Users/sravanidasari/PycharmProjects/fraud-detection/data/final_fraud_dataset.csv'

if not os.path.exists(file_path):
    raise FileNotFoundError(f"File '{file_path}' not found at {file_path}")

df = pd.read_csv(file_path)

# Step 2: Handle NaN values
print("Handling NaN/NULL values...")
df.fillna(0, inplace=True)  # Replace all NaN with 0 to avoid conversion issues

# Step 3: Reduce memory usage
categorical_columns = ['PTCP_TYP', 'CUST_TYP', 'CUST_TYP_cust', 'CUST_GENDER',
                       'CLM_OCCR_STATE', 'FINAL_STATUS', 'REPORTING_CHANNEL', 'EMPLOYMENT_STATUS']

# Step 4: Label Encoding
print("Encoding categorical columns...")
for col in categorical_columns:
    if col in df.columns:
        le = LabelEncoder()
        try:
            df[col] = le.fit_transform(df[col].astype(str))
        except Exception as e:
            print(f"Error encoding column '{col}': {e}")

# Step 5: Downcast numeric columns
print("Downcasting numeric columns...")
for col in df.select_dtypes(include=['object', 'string']).columns:
    try:
        df[col] = pd.to_numeric(df[col], downcast='float', errors='coerce')
    except Exception as e:
        print(f"Warning: Could not convert column '{col}' to numeric. Skipping...")

# Step 6: Print data types to ensure all columns are numeric
print("\nData types after conversion:")
print(df.dtypes)

# Step 7: Memory usage check
import psutil, os

def memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 ** 2)  # MB

print(f"\nMemory usage before model training: {memory_usage()} MB")

# Step 8: Separate features (X) and target (y)
print("\nSeparating features and target variable...")
target_column = 'FRAUD_INDICATOR'
X = df.drop(columns=[target_column])
y = df[target_column]

# Step 9: Train-test split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 10: Train a simple model (RandomForest)
from sklearn.ensemble import RandomForestClassifier

print("\nTraining RandomForest model...")
clf = RandomForestClassifier(n_estimators=100, random_state=42)
try:
    clf.fit(X_train, y_train)
except Exception as e:
    print(f"Error during model training: {e}")

# Step 11: Evaluate the model
from sklearn.metrics import accuracy_score

y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel accuracy on test set: {accuracy * 100:.2f}%")

# Step 12: Save the model to a .pkl file˚
import joblib

output_path = '/Users/sravanidasari/PycharmProjects/fraud-detection/models/fraud_detection_model.pkl'
print(f"\nSaving model to {output_path}...")
joblib.dump(clf, output_path)

print("Model saved successfully.")
