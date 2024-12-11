import pandas as pd
import numpy as np
import holidays
import random

#  Load the Unified Data
print("Loading unified customer policy claim details dataset...")
df = pd.read_csv('data/Unified_Customer_Policy_Claim_Details.csv')

# Convert date columns to datetime
date_columns = ['CLM_RPT_DT', 'CLM_OCCR_DT', 'PLCY_STRT_DT', 'PLCY_END_DT']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# Initialize fraud indicator
df['CLM_FRAUD_IND'] = 0

# Time-Based Anomaly Rules
df['Fraud_Rule_1'] = ((df['CLM_RPT_DT'] < df['CLM_OCCR_DT']) & df['CLM_RPT_DT'].notnull() & df['CLM_OCCR_DT'].notnull()).astype(int)
df['Days_To_Policy_End'] = (df['PLCY_END_DT'] - df['CLM_OCCR_DT']).dt.days
df['Fraud_Rule_2'] = ((df['Days_To_Policy_End'] <= 14) & (df['Days_To_Policy_End'] > 0)).astype(int)
df['Days_From_Policy_Start'] = (df['CLM_OCCR_DT'] - df['PLCY_STRT_DT']).dt.days
df['Fraud_Rule_3'] = ((df['Days_From_Policy_Start'] <= 14) & (df['Days_From_Policy_Start'] > 0)).astype(int)
df['Fraud_Rule_4'] = df['CLM_RPT_DT'].dt.weekday.isin([5, 6]).astype(int)
df['Days_Delay_Reporting'] = (df['CLM_RPT_DT'] - df['CLM_OCCR_DT']).dt.days
df['Fraud_Rule_5'] = (df['Days_Delay_Reporting'] > 30).astype(int)
df['Fraud_Rule_6'] = (df['Days_Delay_Reporting'] < 1).astype(int)
df['Previous_Claim_Date'] = df.groupby('CUST_ID_CLAIMANT')['CLM_OCCR_DT'].shift(1)
df['Days_Between_Claims'] = (df['CLM_OCCR_DT'] - df['Previous_Claim_Date']).dt.days
df['Fraud_Rule_7'] = ((df['Days_Between_Claims'] <= 30) & (df['Days_Between_Claims'] > 0)).astype(int)
df['CLM_RPT_DT'] = pd.to_datetime(df['CLM_RPT_DT'], errors='coerce')

# Add random hour and minute if CLM_RPT_DT does not have time
df['CLM_RPT_DT'] = df['CLM_RPT_DT'].apply(lambda x: x + pd.Timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)) if pd.notnull(x) else x)

# Rule 8: Claims reported during unusual hours (10 PM to 6 AM)
# Only mark 1% of these claims as fraudulent
def mark_fraud_based_on_time(x):
    if pd.notnull(x) and (x.hour >= 22 or x.hour <= 6):
        return 1 if random.random() <= 0.01 else 0  # 1% chance of being fraud
    return 0

df['Fraud_Rule_8'] = df['CLM_RPT_DT'].apply(mark_fraud_based_on_time)

# Financial Anomaly Rules**
df['Fraud_Rule_9'] = ((df['CLM_AMT'] > 0.9 * df['PLCY_CLAIM_LIMIT']) & df['CLM_AMT'].notnull()).astype(int)
df['Previous_Claim_Amount'] = df.groupby('CUST_ID_INSURED')['CLM_AMT'].shift(1)
df['Fraud_Rule_10'] = ((df['CLM_AMT'] > 3 * df['Previous_Claim_Amount']) & (df['INJURY_SEVERITY'] != 'High')).astype(int)
df['Fraud_Rule_11'] = df.groupby(['CUST_ID_INSURED', 'CLM_AMT'])['CLM_NO'].transform('count') > 1
df['Fraud_Rule_12'] = df.groupby('CUST_ID_CLAIMANT')['CLM_NO'].transform('count') > 5

# Injury-Related Anomaly Rules**
df['Fraud_Rule_13'] = ((df['INJURY_TYPE'] == 'Burn') & (df['INJURY_BODY_PART'] == 'Back')).astype(int)
df['Fraud_Rule_14'] = ((df['INJURY_SEVERITY'] == 'High') & (df['TREATMENT_REQUIRED'] == 'No')).astype(int)
df['Fraud_Rule_15'] = df.groupby(['CUST_ID_CLAIMANT', 'INJURY_BODY_PART'])['CLM_DTL_ID'].transform('count') > 2
df['Fraud_Rule_16'] = ((df['INJURY_BODY_PART'] == 'Head') & (df['INJURY_TYPE'] == 'Burn')).astype(int)
df['Fraud_Rule_17'] = ((df['INJURY_TYPE'] == 'Fracture') & (df['INJURY_BODY_PART'] == 'Neck')).astype(int)
df['Fraud_Rule_18'] = ((df['INJURY_TYPE'] == 'Amputation') & (df['INJURY_BODY_PART'].isin(['Head', 'Chest', 'Back']))).astype(int)
df['Fraud_Rule_19'] = ((df['INJURY_BODY_PART'] == 'Internal Organs') & (df['TREATMENT_REQUIRED'] == 'No')).astype(int)
df['Fraud_Rule_20'] = df.groupby('CLM_DTL_ID')['INJURY_BODY_PART'].transform('nunique') > 3

# Behavioral Anomaly Rules**
df['Fraud_Rule_21'] = df.groupby(['CUST_ID_CLAIMANT', 'CLM_OCCR_DT'])['CLM_DTL_ID'].transform('count') > 1
us_holidays = holidays.US(years=[2023, 2024,2022, 2021, 2022])
df['Fraud_Rule_22'] = df['CLM_RPT_DT'].dt.date.apply(lambda x: 1 if x in us_holidays else 0)
df['Fraud_Rule_23'] = df.groupby('CUST_ID_CLAIMANT')['CUST_ID_MED_PROV'].nunique() > 5
df['Fraud_Rule_24'] = df.groupby(['CUST_ID_MED_PROV', 'CLM_OCCR_DT'])['CLM_DTL_ID'].transform('count') > 3
df['Fraud_Rule_25'] = df.groupby(['CUST_ID_CLAIMANT', 'CLM_RPT_DT'])['CLM_DTL_ID'].transform('count') > 1
df['Fraud_Rule_26'] = ((df['INJURY_SEVERITY'] == 'High') & (df['DAYS_LOST'] < 3)).astype(int)
df['Fraud_Rule_27'] = ((df['INJURY_SEVERITY'] == 'Low') & (df['DAYS_LOST'] > 30)).astype(int)
df['Fraud_Rule_28'] = ((df['INJURY_SEVERITY'] == 'Medium') & (df['DAYS_LOST'] > 60)).astype(int)
df['Fraud_Rule_29'] = ((df['INJURY_SEVERITY'] == 'High') & (df['TREATMENT_REQUIRED'] == 'No')).astype(int)
df['Fraud_Rule_30'] = ((df['INJURY_SEVERITY'] == 'Low') & (df['TREATMENT_REQUIRED'] == 'Yes')).astype(int)

# Fraud Indicator Calculation**
fraud_rules = [col for col in df.columns if 'Fraud_Rule' in col]
df['CLM_FRAUD_IND'] = (df[fraud_rules].sum(axis=1) > 2).astype(int)

# Save the Labeled Data**
columns_to_drop = ['Days_Delay_Reporting', 'Days_Between_Claims', 'Previous_Claim_Date', 'Previous_Claim_Amount']
df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
df.to_csv('data/Labeled_Unified_Customer_Policy_Claim_Details.csv', index=False)

# Print Fraud Distribution**
fraud_distribution = df['CLM_FRAUD_IND'].value_counts(normalize=True)
print(f"Fraud label distribution: \n{fraud_distribution}")
