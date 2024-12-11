import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import OneClassSVM
from xgboost import XGBClassifier
import joblib
import shap
import streamlit as st


# Paths
INPUT_FILE = 'data/Cleaned_Unified_Customer_Policy_Claim_Details.csv'
FEATURE_SELECTED_FILE = 'data/Feature_Selected_Unified_Customer_Policy_Claim_Details.csv'
MODEL_DIR = 'models/'

# Load data
print("Loading cleaned dataset...")
df = pd.read_csv(INPUT_FILE, parse_dates=['CLM_RPT_DT', 'CLM_OCCR_DT', 'PLCY_STRT_DT', 'PLCY_END_DT'], low_memory=False)
print(f"Data loaded. Shape: {df.shape}")

# Extract useful features from datetime columns
df['CLM_RPT_YEAR'] = df['CLM_RPT_DT'].dt.year
df['CLM_RPT_MONTH'] = df['CLM_RPT_DT'].dt.month
df['CLM_RPT_DAY_OF_WEEK'] = df['CLM_RPT_DT'].dt.weekday
df['CLM_OCCR_YEAR'] = df['CLM_OCCR_DT'].dt.year
df['CLM_OCCR_MONTH'] = df['CLM_OCCR_DT'].dt.month
df['CLM_OCCR_DAY_OF_WEEK'] = df['CLM_OCCR_DT'].dt.weekday

# Drop original datetime columns
df.drop(columns=['CLM_RPT_DT', 'CLM_OCCR_DT', 'PLCY_STRT_DT', 'PLCY_END_DT'], inplace=True, errors='ignore')

# Separate features and target
X = df.drop(columns=['CLM_FRAUD_IND'], errors='ignore')
y = df['CLM_FRAUD_IND']

# Impute and encode
numeric_columns = X.select_dtypes(include=['int64', 'float64']).columns
categorical_columns = X.select_dtypes(include=['object', 'category']).columns

# Impute missing values
numeric_imputer = SimpleImputer(strategy='median')
categorical_imputer = SimpleImputer(strategy='most_frequent')
X[numeric_columns] = numeric_imputer.fit_transform(X[numeric_columns])
X[categorical_columns] = categorical_imputer.fit_transform(X[categorical_columns])

# One-hot encode categorical features
X = pd.get_dummies(X, columns=categorical_columns, drop_first=True)

# Normalize numeric features
scaler = StandardScaler()
X[numeric_columns] = scaler.fit_transform(X[numeric_columns])

# Remove low-variance features
var_thresh = VarianceThreshold(threshold=0.01)
X_low_variance = pd.DataFrame(var_thresh.fit_transform(X), columns=X.columns[var_thresh.get_support()])

# Feature selection using SelectKBest
k_best_selector = SelectKBest(score_func=f_classif, k=50)
X_k_best = pd.DataFrame(k_best_selector.fit_transform(X_low_variance, y), columns=X_low_variance.columns[k_best_selector.get_support()])

# Feature importance using RandomForestClassifier
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_low_variance, y)

# Select features from RandomForest
X_important = X_low_variance.loc[:, rf_model.feature_importances_ > 0.01]

# Handle duplicated columns before joining
X_important = X_important.loc[:, ~X_important.columns.duplicated()]
X_k_best = X_k_best.loc[:, ~X_k_best.columns.duplicated()]

# Get unique columns from X_k_best that are NOT in X_important
unique_kbest_cols = [col for col in X_k_best.columns if col not in X_important.columns]

# Join without overlapping columns
X_final = pd.concat([X_important, X_k_best[unique_kbest_cols]], axis=1)

# Add the target back
X_final['CLM_FRAUD_IND'] = y

# Save feature-selected dataset
X_final.to_csv(FEATURE_SELECTED_FILE, index=False)

# Save the final feature set
training_features = X_final.drop(columns=['CLM_FRAUD_IND']).columns.tolist()
joblib.dump(training_features, MODEL_DIR + 'training_features.pkl')

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X_final.drop(columns=['CLM_FRAUD_IND']), X_final['CLM_FRAUD_IND'], test_size=0.2, random_state=42, stratify=X_final['CLM_FRAUD_IND'])

# Train One-Class SVM
oc_svm = OneClassSVM(kernel='rbf', gamma='scale', nu=0.05)
oc_svm.fit(X_train)

# Train XGBoost Classifier
xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb_model.fit(X_train, y_train)

# Train Random Forest Classifier
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Save models
joblib.dump(oc_svm, MODEL_DIR + 'one_class_svm.pkl')
joblib.dump(xgb_model, MODEL_DIR + 'xgboost.pkl')
joblib.dump(rf_model, MODEL_DIR + 'random_forest.pkl')

# SHAP Analysis for XGBoost
print("Performing SHAP Analysis...")
explainer = shap.Explainer(xgb_model, X_test)
shap_values = explainer(X_test)

# Display SHAP Force Plot for a single prediction
try:
    st.subheader("SHAP Explanation")
    st.write("SHAP Force Plot for Random Forest")

    # Generate the force plot for the first prediction
    shap_force_plot = shap.plots.force(
        base_value=explainer.expected_value,
        shap_values=shap_values[0],
        features=X_test.iloc[0]
    )
    shap_html = shap.save_html("shap_force_plot.html", shap_force_plot)
    with open("shap_force_plot.html", "r") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=500)
except Exception as e:
    st.warning(f"SHAP visualization failed: {str(e)}")

print("\nModel training complete. Feature set and SHAP plots saved.")
