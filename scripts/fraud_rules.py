import pandas as pd
import random

def identify_fraud(df, fraud_percentage=0.15):
    """Identify fraudulent claims using 21 enhanced fraud rules (after removing 6 rules)."""
    print("Identifying potential fraud using 21 enhanced rules...")

    #  Required Conversions
    df['CLM_RPT_DT'] = pd.to_datetime(df['CLM_RPT_DT'], errors='coerce')
    df['CLM_OCCR_DT'] = pd.to_datetime(df['CLM_OCCR_DT'], errors='coerce')
    df['PLCY_END_DT'] = pd.to_datetime(df['PLCY_END_DT'], errors='coerce')
    df['PLCY_STRT_DT'] = pd.to_datetime(df['PLCY_STRT_DT'], errors='coerce')
    df['CLMT_DISAB_BGN_DT'] = pd.to_datetime(df['CLMT_DISAB_BGN_DT'], errors='coerce')

    #  Fraud Rule Implementation (21 Rules)
    df['LATE_REPORT_FLAG'] = (df['CLM_RPT_DT'] - df['CLM_OCCR_DT']).dt.days > 30
    df['CLAIM_AFTER_POLICY_END'] = df['CLM_OCCR_DT'] > df['PLCY_END_DT']
    df['NEAR_POLICY_EXPIRY'] = (df['PLCY_END_DT'] - df['CLM_OCCR_DT']).dt.days < 7
    df['SUSPICIOUS_CLAIM_AMOUNT'] = df['CLM_AMT'] > 0.9 * df['PLCY_CLAIM_LIMIT']
    df['STATE_MISMATCH'] = df['CLM_OCCR_STATE'] != df['INSURED_CUST_STATE']
    df['CLAIMANT_STATE_MISMATCH'] = df['CLM_OCCR_STATE'] != df['CLAIMANT_CUST_STATE']
    df['PROVIDER_STATE_MISMATCH'] = df['CLM_OCCR_STATE'] != df['MEDPROV_CUST_STATE']
    df['DISABILITY_DATE_FRAUD'] = df['CLMT_DISAB_BGN_DT'] < df['CLM_OCCR_DT']
    df['BACKDATED_CLAIM'] = df['CLM_OCCR_DT'] < df['PLCY_STRT_DT']
    df['EXCESSIVE_CLAIM_AMOUNT'] = df['CLM_AMT'] > 5 * df['PLCY_PREMIUM_AMT']
    df['JOB_INJURY_MISMATCH'] = df.apply(lambda x: 1 if x['CLMT_JOB_TTL'] == 'Software Engineer' and x['INJURY_TYP_CD'] in ['Burn', 'Fracture'] else 0, axis=1)
    df['EMPLOYMENT_STATUS_FRAUD'] = ((df['EMPLOYMENT_STATUS'] == 'Terminated') & (df['CLM_OCCR_DT'] > df['CLMT_HIRE_DT'])).astype(int)
    df['DECLINED_SUSPICIOUS'] = ((df['CLM_STS_CD'] == 'Declined') & (df['STATUS_REASON'].str.contains('Insufficient Evidence', na=False))).astype(int)
    df['LATE_STATUS_CHANGE'] = ((pd.to_datetime(df['CLM_STS_DT']) - pd.to_datetime(df['CLM_RPT_DT'])).dt.days > 60).astype(int)
    df['INJURY_SEVERITY_MISMATCH'] = ((df['INJURY_SEVERITY'] == 'High') & (df['DAYS_LOST'] < 7)).astype(int)
    df['RAPID_CLAIMS'] = df.groupby('CUST_ID_INSURED')['CLM_OCCR_DT'].diff().dt.days < 30
    df['DUPLICATE_CLAIM_NO'] = df.duplicated(subset=['CLM_NO'], keep=False).astype(int)
    df['EXCESSIVE_TREATMENT'] = (df['TREATMENT_REQUIRED'] == 'Surgery') & (df['INJURY_SEVERITY'] != 'Severe')
    df['MULTIPLE_PROVIDERS'] = df.groupby('CLM_DTL_ID')['MEDPROV_CUST_STATE'].transform('nunique') > 1
    df['INJURY_JOB_MISMATCH'] = df.apply(lambda x: 1 if x['CLMT_JOB_TTL'] in ['Software Engineer', 'Office Clerk'] and x['INJURY_TYP_CD'] in ['Burn', 'Fracture'] else 0, axis=1)

    #  Apply all 21 rules
    fraud_columns = [col for col in df.columns if col.endswith('FLAG') or 'FRAUD' in col or 'MISMATCH' in col]
    df[fraud_columns] = df[fraud_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    df['CLM_FRAUD_IND'] = df[fraud_columns].max(axis=1)

    #  Control Total Fraud Percentage
    total_claims = len(df)
    target_fraud_claims = int(total_claims * fraud_percentage)
    current_fraud_claims = df['CLM_FRAUD_IND'].sum()

    if current_fraud_claims > target_fraud_claims:
        excess_indices = df[df['CLM_FRAUD_IND'] == 1].sample(current_fraud_claims - target_fraud_claims).index
        df.loc[excess_indices, 'CLM_FRAUD_IND'] = 0
    elif current_fraud_claims < target_fraud_claims:
        additional_fraud_indices = df[df['CLM_FRAUD_IND'] == 0].sample(target_fraud_claims - current_fraud_claims).index
        df.loc[additional_fraud_indices, 'CLM_FRAUD_IND'] = 1

    # Update the fraud reason
    df['FRAUD_REASON'] = df.apply(lambda row: ', '.join([col for col in fraud_columns if row[col] == 1]), axis=1)
    print(f" Fraud rules applied. Target Fraud Claims: {target_fraud_claims} | Actual Fraud Claims: {df['CLM_FRAUD_IND'].sum()}")
    return df


# Usage
if __name__ == "__main__":
    df = pd.read_csv('data/Enhanced_Unified_Dataset.csv')
    df = identify_fraud(df, fraud_percentage=0.15)
    df.to_csv('data/Enhanced_Fraud_Detection.csv', index=False)
