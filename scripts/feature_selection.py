import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split

# Paths
DATA_PATH = "data/Enhanced_Unified_Dataset.csv"
OUTPUT_PATH_FEATURE_IMPORTANCE = "data/Feature_Importance.csv"
OUTPUT_PATH_SELECTED_FEATURES = "data/Selected_Features.csv"
OUTPUT_TRAIN = "data/train.csv"
OUTPUT_VALIDATION = "data/validation.csv"
OUTPUT_TEST = "data/test.csv"
SELECTED_FEATURES_PATH = "data/selected_features.txt"

# Load the enhanced dataset
print("Loading enhanced dataset...")
df = pd.read_csv(DATA_PATH)

#  Drop columns that are not useful for prediction
columns_to_drop = ['PLCY_NO', 'CLM_NO', 'CLM_OCCR_ADDR', 'CLM_OCCR_CITY', 'INSURED_CUST_FRST_NM',
                   'CLAIMANT_CUST_FRST_NM', 'CLAIMANT_CUST_LST_NM', 'MEDPROV_CUST_FRST_NM']
df = df.drop(columns=columns_to_drop, errors='ignore')

#  Convert date columns to numeric (UNIX timestamp)
date_columns = ['CLM_RPT_DT', 'CLM_OCCR_DT', 'PLCY_END_DT', 'PLCY_STRT_DT']
for col in date_columns:
    if col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce').astype('int64') // 10**9  # Convert to UNIX timestamp
        except Exception as e:
            print(f" Error converting {col} to UNIX timestamp: {e}")

# Encode categorical variables
categorical_columns = ['RISK_LEVEL', 'PLCY_PAYMENT_STATUS', 'EMPLOYMENT_STATUS', 'CLM_STS_CD']
for col in categorical_columns:
    if col in df.columns:
        if not np.issubdtype(df[col].dtype, np.number):  # Ensure column is not already numeric
            df[col] = df[col].astype('category').cat.codes  # Encode as numeric

#  Drop non-numeric columns to ensure model compatibility
non_numeric_columns = df.select_dtypes(include=['object']).columns
if len(non_numeric_columns) > 0:
    print(f" Dropping non-numeric columns: {list(non_numeric_columns)}")
    df = df.drop(columns=non_numeric_columns)

# Define the target column and feature set
target_column = "CLM_FRAUD_IND"
if target_column not in df.columns:
    raise KeyError(f" Target column '{target_column}' not found in the dataset.")

X = df.drop(columns=[target_column])  # Features
y = df[target_column]  # Target

#  Handle missing or invalid values
if X.isnull().sum().sum() > 0 or not np.isfinite(X).all().all():
    print("Handling missing or invalid values...")
    X = X.fillna(0)  # Replace NaN with 0
    X = np.nan_to_num(X)  # Replace inf/-inf with finite values

# Ensure y is numeric
y = y.astype(int)

#  Split the data into training, validation, and testing sets
print("Splitting data into training, validation, and test sets...")
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)

# Train a Random Forest model for feature selection
print(" Training Random Forest for feature selection...")
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

#  Compute feature importance
feature_importances = model.feature_importances_
important_features = pd.DataFrame({
    "Feature": X.columns,
    "Importance": feature_importances
}).sort_values(by="Importance", ascending=False)

# Save important features
print(" Feature Importance Ranking:")
print(important_features)
important_features.to_csv(OUTPUT_PATH_FEATURE_IMPORTANCE, index=False)
print(f"Feature importance saved to {OUTPUT_PATH_FEATURE_IMPORTANCE}")

# Select important features using a threshold
print(" Selecting important features...")
threshold = 0.01  # Adjust threshold
selector = SelectFromModel(model, threshold=threshold, prefit=True)
X_train_selected = selector.transform(X_train)
X_val_selected = selector.transform(X_val)
X_test_selected = selector.transform(X_test)

# Save the names of selected features to a file for dashboard compatibility
selected_columns = X.columns[selector.get_support()]
with open(SELECTED_FEATURES_PATH, 'w') as file:
    for feature in selected_columns:
        file.write(f"{feature}\n")
print(f" Selected features saved to {SELECTED_FEATURES_PATH}")

print(f"Selected {X_train_selected.shape[1]} features out of {X.shape[1]}")

# Save the selected features to a new dataset
selected_features_df = pd.DataFrame(X_train_selected, columns=selected_columns)
selected_features_df[target_column] = y_train.reset_index(drop=True)
selected_features_df.to_csv(OUTPUT_PATH_SELECTED_FEATURES, index=False)
print(f" Selected features with target column saved to '{OUTPUT_PATH_SELECTED_FEATURES}'")

# Save the train, validation, and test datasets
print("Saving train, validation, and test datasets...")
pd.concat([pd.DataFrame(X_train_selected, columns=selected_columns), y_train.reset_index(drop=True)], axis=1).to_csv(OUTPUT_TRAIN, index=False)
pd.concat([pd.DataFrame(X_val_selected, columns=selected_columns), y_val.reset_index(drop=True)], axis=1).to_csv(OUTPUT_VALIDATION, index=False)
pd.concat([pd.DataFrame(X_test_selected, columns=selected_columns), y_test.reset_index(drop=True)], axis=1).to_csv(OUTPUT_TEST, index=False)

print(f" Train, validation, and test datasets saved at:\n{OUTPUT_TRAIN}\n{OUTPUT_VALIDATION}\n{OUTPUT_TEST}")