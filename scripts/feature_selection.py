import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier

# File Paths
CLEANED_FILE = 'data/Cleaned_Unified_Customer_Policy_Claim_Details.csv'
FEATURE_SELECTED_FILE = 'data/Feature_Selected_Unified_Customer_Policy_Claim_Details.csv'
FEATURE_IMPORTANCE_REPORT = 'data/Feature_Importance_Report.csv'

# Load Cleaned Data**
print("Loading feature-engineered dataset...")
try:
    df = pd.read_csv(CLEANED_FILE, low_memory=False)
    print(f"Data loaded successfully. Shape: {df.shape}")
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Separate Features and Target**
X = df.drop(columns=['CLM_FRAUD_IND'])
y = df['CLM_FRAUD_IND']

# Identify Numeric and Categorical Columns**
numeric_columns = X.select_dtypes(include=['int64', 'float64']).columns
categorical_columns = X.select_dtypes(include=['object', 'category']).columns

print(f"Numeric columns: {list(numeric_columns)}")
print(f"Categorical columns: {list(categorical_columns)}")

# Impute Missing Values**
print("\n Imputing missing values...")
# Impute numeric columns with median
if not numeric_columns.empty:
    print(f"Imputing numeric columns: {list(numeric_columns)}")
    numeric_imputer = SimpleImputer(strategy='median')
    X[numeric_columns] = numeric_imputer.fit_transform(X[numeric_columns])

# Impute categorical columns with most frequent
if not categorical_columns.empty:
    print(f"Imputing categorical columns: {list(categorical_columns)}")
    categorical_imputer = SimpleImputer(strategy='most_frequent')
    X[categorical_columns] = categorical_imputer.fit_transform(X[categorical_columns])

# Encode Categorical Columns**
print("\n Encoding categorical features...")
for col in categorical_columns:
    try:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    except Exception as e:
        print(f"Error encoding column '{col}': {e}")

# Normalize Numeric Features**
print("\n Normalizing numeric features...")
scaler = StandardScaler()
try:
    X[numeric_columns] = scaler.fit_transform(X[numeric_columns])
except Exception as e:
    print(f"Error during normalization: {e}")

# Remove Low-Variance Features**
print("\n Removing low-variance features...")
try:
    var_thresh = VarianceThreshold(threshold=0.01)  # 1% variance threshold
    X_low_variance = pd.DataFrame(var_thresh.fit_transform(X), columns=X.columns[var_thresh.get_support()])
    print(f"Low-variance features removed. Shape: {X_low_variance.shape}")
except Exception as e:
    print(f"Error during variance thresholding: {e}")
    X_low_variance = X  # Fallback

# Feature Selection Using SelectKBest (ANOVA F-Statistic)**
print("\n Selecting best features using SelectKBest (f_classif)...")
try:
    selector = SelectKBest(score_func=f_classif, k=50)  # Select top 50 features
    X_selected = selector.fit_transform(X_low_variance, y)
    selected_features = X_low_variance.columns[selector.get_support()]
    print(f"Top 50 features selected. Shape: {X_selected.shape}")
except Exception as e:
    print(f"Error during feature selection with SelectKBest: {e}")
    X_selected = X_low_variance  # Fallback
    selected_features = X_low_variance.columns

# Feature Importance Using RandomForestClassifier**
print("\n Computing feature importance using RandomForestClassifier...")
try:
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_low_variance, y)
    feature_importances = rf_model.feature_importances_
    importance_df = pd.DataFrame({
        'Feature': X_low_variance.columns,
        'Importance': feature_importances
    })
    importance_df.sort_values(by='Importance', ascending=False, inplace=True)
    print(f"Important features selected based on RandomForest importance.")
except Exception as e:
    print(f"Error during RandomForest feature importance: {e}")
    importance_df = pd.DataFrame()

# Save Feature-Selected Data**
print("\nSaving feature-selected dataset...")
try:
    X_selected_df = pd.DataFrame(X_selected, columns=selected_features)
    X_selected_df['CLM_FRAUD_IND'] = y.values
    X_selected_df.to_csv(FEATURE_SELECTED_FILE, index=False)
    print(f"Feature-selected dataset saved as {FEATURE_SELECTED_FILE}.")
except Exception as e:
    print(f"Error saving feature-selected dataset: {e}")

# Save Feature Importance Report**
print("\n Saving feature importance report...")
try:
    importance_df.to_csv(FEATURE_IMPORTANCE_REPORT, index=False)
    print(f"Feature importance report saved as {FEATURE_IMPORTANCE_REPORT}.")
except Exception as e:
    print(f"Error saving feature importance report: {e}")
