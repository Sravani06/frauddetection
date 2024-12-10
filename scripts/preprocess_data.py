import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

# File paths
INPUT_FILE = 'data/Enhanced_Unified_Dataset.csv'
OUTPUT_FILE = 'data/Processed_Enhanced_Dataset.csv'


def preprocess_data(df):
    """Preprocess the Enhanced Unified Dataset."""
    print(" Preprocessing Data...")

    #  ** Drop Unnecessary Columns**
    drop_columns = [
        'CLM_DTL_ID', 'PLCY_NO', 'CLM_NO', 'INSURED_CUST_FRST_NM',
        'CLAIMANT_CUST_FRST_NM', 'CLAIMANT_CUST_LST_NM', 'MEDPROV_CUST_FRST_NM',
        'FRAUD_REASON', 'FRAUD_REASON_ADDITIONAL', 'STATUS_REASON',
        'CLM_OCCR_ADDR', 'CLM_OCCR_CITY', 'CUST_ID_INSURED', 'CUST_ID_CLAIMANT',
        'CUST_ID_MED_PROV', 'INSURED_CUST_ID', 'CLM_OCCR_ZIP'
    ]
    df.drop(columns=drop_columns, inplace=True, errors='ignore')
    print(f" Dropped unnecessary columns. Columns remaining: {df.shape[1]}")

    #  ** Encode Categorical Columns**
    categorical_columns = [
        'RISK_LEVEL', 'PLCY_PAYMENT_STATUS', 'INJURY_TYP_CD',
        'INJURY_SEVERITY', 'PLCY_STRT_DT', 'PLCY_END_DT',
        'CLM_RPT_DT', 'CLM_OCCR_DT', 'CLM_STS_CD', 'EMPLOYMENT_STATUS', 'WORK_ENVIRONMENT'
    ]

    print(f" Encoding categorical columns: {categorical_columns}")
    for col in categorical_columns:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))

    #  ** Normalize Numerical Columns**
    numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns
    print(f" Normalizing numerical columns: {numerical_columns.tolist()}")

    # Standardize the numerical columns (Z-score normalization)
    scaler = StandardScaler()
    df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

    print(f" Data Preprocessing Complete. Total Columns: {len(df.columns)}")
    return df


if __name__ == "__main__":
    print(f" Loading file: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)

    print(f" Initial Data Shape: {df.shape}")
    df = preprocess_data(df)

    print(f" Saving preprocessed data to: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f" Processed dataset saved successfully at {OUTPUT_FILE}")
