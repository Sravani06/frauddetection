import pandas as pd
from sklearn.impute import SimpleImputer

# File Paths
LABELED_FILE = 'data/Labeled_Unified_Customer_Policy_Claim_Details.csv'
CLEANED_FILE = 'data/Cleaned_Unified_Customer_Policy_Claim_Details.csv'

# Data Type Declaration**
dtypes = {
    'CLM_DTL_ID': 'int64',
    'CLM_NO': 'str',
    'CLM_AMT': 'float64',
    'CUST_ID_INSURED': 'int64',
    'CUST_ID_CLAIMANT': 'int64',
    'CUST_ID_MED_PROV': 'int64',
    'CLM_OCCR_ADDR': 'str',
    'CLM_OCCR_CITY': 'str',
    'CLM_OCCR_STATE': 'category',
    'PLCY_NO': 'str',
    'PLCY_CLAIM_LIMIT': 'float64',
    'PLCY_PREMIUM_AMT': 'float64',
    'PLCY_PAYMENT_STATUS': 'category',
    'RISK_LEVEL': 'category',
    'INJURY_BODY_PART': 'category',
    'INJURY_TYPE': 'category',
    'INJURY_SEVERITY': 'category',
    'DAYS_LOST': 'float64',
    'CLM_FRAUD_IND': 'int8',
    'INSURED_CUST_ADDR': 'str',
    'INSURED_CUST_STATE': 'category',
    'CLAIMANT_CUST_FRST_NM': 'str',
    'CLAIMANT_CUST_LST_NM': 'str',
    'CLAIMANT_CUST_GENDER': 'category',
    'CLAIMANT_CUST_DOB': 'str',
    'CLAIMANT_CUST_DOD': 'str',
    'CLAIMANT_CUST_STATE': 'category',
    'MEDPROV_CUST_STATE': 'category',
    'JOB_DESC': 'str',
    'CLMT_JOB_TITLE': 'str',
    'CLMT_JOB_TYP': 'category',
    'CLM_OCCR_ADDR_STATE': 'category',
    'INSURED_CUST_ADDR_STATE': 'category'
}

# Load Data**
try:
    print("Loading labeled dataset...")
    df = pd.read_csv(
        LABELED_FILE,
        dtype=dtypes,
        parse_dates=['CLM_RPT_DT', 'CLM_OCCR_DT', 'PLCY_STRT_DT', 'PLCY_END_DT'],
        low_memory=False
    )
    print(f"Data loaded successfully. Shape: {df.shape}")
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Check for Missing Columns**
missing_columns = [col for col in dtypes if col not in df.columns]
if missing_columns:
    print(f"Warning: The following columns are missing from the dataset: {missing_columns}")

# Impute Missing Values**
print("\n Imputing missing values...")

# Separate numeric and categorical columns
numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
categorical_columns = df.select_dtypes(include=['category']).columns

# Impute numeric columns with the median**
if not numeric_columns.empty:
    print(f"Imputing missing values for numeric columns: {list(numeric_columns)}")
    numeric_imputer = SimpleImputer(strategy='median')
    try:
        df[numeric_columns] = numeric_imputer.fit_transform(df[numeric_columns])
    except Exception as e:
        print(f"Error during numeric imputation: {e}")
else:
    print("No numeric columns available for imputation.")

# Impute categorical columns with the most frequent value**
if not categorical_columns.empty:
    print(f"Imputing missing values for categorical columns: {list(categorical_columns)}")
    categorical_imputer = SimpleImputer(strategy='most_frequent')
    try:
        df[categorical_columns] = categorical_imputer.fit_transform(df[categorical_columns])
    except Exception as e:
        print(f"Error during categorical imputation: {e}")
else:
    print("No categorical columns available for imputation.")

# Check for Any Remaining Null Values**
remaining_nulls = df.isnull().sum().sum()
if remaining_nulls > 0:
    print(f" Warning: There are still {remaining_nulls} missing values in the dataset.")

#  **Data Validation**
print("\n Validating data types...")
for column, dtype in dtypes.items():
    if column in df.columns:
        if df[column].dtype.name != dtype:
            print(f" Mismatch in data type for column '{column}'. Expected: {dtype}, Got: {df[column].dtype.name}")
    else:
        print(f" Column '{column}' is missing from the DataFrame.")

# *Save Cleaned Data**
try:
    print(f"\n Saving cleaned dataset to {CLEANED_FILE}...")
    df.to_csv(CLEANED_FILE, index=False)
    print(f"Cleaned dataset saved as {CLEANED_FILE}.")
except Exception as e:
    print(f"Error saving file: {e}")
