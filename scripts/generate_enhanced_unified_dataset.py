import pandas as pd
import os

# Paths
DATA_PATH = os.path.join(os.getcwd(), 'data', 'Unified_Customer_Policy_Claim_Details.csv')
OUTPUT_PATH = os.path.join(os.getcwd(), 'data', 'Enhanced_Unified_Dataset.csv')


def enhance_dataset(df):
    """Enhance the dataset with derived and interaction features."""
    print(" Enhancing dataset with derived and interaction features...")

    # Validate required columns
    required_columns = ['CLM_RPT_DT', 'CLM_OCCR_DT', 'PLCY_END_DT', 'PLCY_CLAIM_LIMIT', 'CLM_AMT']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}. Please ensure the unified dataset is complete.")

    #  Convert date columns to datetime
    date_columns = ['CLM_RPT_DT', 'CLM_OCCR_DT', 'PLCY_END_DT', 'PLCY_STRT_DT']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    #  Derived Features
    # 1. Days between occurrence and report
    df['DAYS_BETWEEN_OCCUR_AND_REPORT'] = (df['CLM_RPT_DT'] - df['CLM_OCCR_DT']).dt.days

    # 2. Flag for late report (more than 30 days)
    df['LATE_REPORT_FLAG'] = (df['DAYS_BETWEEN_OCCUR_AND_REPORT'] > 30).astype(int)

    # 3. Proximity of claim occurrence to policy end date
    df['DAYS_TO_POLICY_END'] = (df['PLCY_END_DT'] - df['CLM_OCCR_DT']).dt.days

    # 4. Percent of claim amount relative to the policy claim limit
    df['CLM_AMT_PERCENT_LIMIT'] = df['CLM_AMT'] / df['PLCY_CLAIM_LIMIT']

    # 5. Flag if claim amount exceeds 90% of the policy claim limit
    df['SUSPICIOUS_CLAIM_AMOUNT'] = (df['CLM_AMT_PERCENT_LIMIT'] > 0.9).astype(int)

    # 6. Employment Status Indicator (set to 1 if employment status is "Active")
    if 'EMPLOYMENT_STATUS' in df.columns:
        df['EMPLOYMENT_ACTIVE_FLAG'] = (df['EMPLOYMENT_STATUS'] == 'Active').astype(int)

    #  Interaction Features
    # Example: Claim amount and risk level interaction
    if 'RISK_LEVEL' in df.columns:
        risk_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
        df['RISK_LEVEL_NUMERIC'] = df['RISK_LEVEL'].map(risk_mapping)
        df['HIGH_RISK_HIGH_AMOUNT'] = ((df['RISK_LEVEL_NUMERIC'] == 3) & (df['CLM_AMT_PERCENT_LIMIT'] > 0.8)).astype(
            int)

    #  Fraud Reason Update
    fraud_reasons = []
    for index, row in df.iterrows():
        reasons = []
        if row.get('LATE_REPORT_FLAG', 0) == 1:
            reasons.append('Late Report')
        if row.get('SUSPICIOUS_CLAIM_AMOUNT', 0) == 1:
            reasons.append('Suspicious Claim Amount')
        if row.get('HIGH_RISK_HIGH_AMOUNT', 0) == 1:
            reasons.append('High Risk and High Claim Amount')
        if row.get('DAYS_TO_POLICY_END', 0) < 7:
            reasons.append('Claim Near Policy End')
        if reasons:
            fraud_reasons.append(', '.join(reasons))
        else:
            fraud_reasons.append('None')

    df['UPDATED_FRAUD_REASON'] = fraud_reasons

    print("Dataset enhancement complete!")
    return df


def save_enhanced_data(df, output_path):
    """Save the enhanced dataset to a CSV file."""
    try:
        df.to_csv(output_path, index=False)
        print(f"Enhanced dataset saved to {output_path}")
    except Exception as e:
        print(f" Failed to save enhanced dataset: {e}")


if __name__ == "__main__":
    try:
        print("🔍 Loading unified dataset...")
        # Load the unified dataset
        unified_df = pd.read_csv(DATA_PATH)

        print(f" Unified dataset loaded. Shape: {unified_df.shape}")

        # Enhance the dataset
        enhanced_df = enhance_dataset(unified_df)

        # Save the enhanced dataset
        save_enhanced_data(enhanced_df, OUTPUT_PATH)

    except Exception as e:
        print(f" An error occurred: {e}")
