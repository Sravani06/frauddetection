import pandas as pd
import numpy as np

# Load all required datasets
print("Loading CSV files...")
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')
customer_details_df = pd.read_csv('data/CUSTOMER_DETAILS.csv')
policy_details_df = pd.read_csv('data/POLICY_DETAILS.csv')
claim_status_df = pd.read_csv('data/CLAIM_STATUS.csv')
claim_participant_df = pd.read_csv('data/CLAIM_PARTICIPANT.csv')
claim_additional_details_df = pd.read_csv('data/CLAIM_ADDITIONAL_DETAILS.csv')
claim_injury_details_df = pd.read_csv('data/CLAIM_INJURY_DETAILS.csv')
payment_details_df = pd.read_csv('data/PAYMENT_DETAILS.csv')

# Merge datasets into a unified DataFrame
print("Merging datasets into unified DataFrame...")
unified_df = claim_details_df.merge(customer_details_df, on='CUST_ID', how='left', suffixes=('', '_customer'))
unified_df = unified_df.merge(policy_details_df, on='PLCY_NO', how='left', suffixes=('', '_policy'))
unified_df = unified_df.merge(claim_status_df, on='CLM_DTL_ID', how='left', suffixes=('', '_status'))
unified_df = unified_df.merge(claim_participant_df, on='CLM_DTL_ID', how='left', suffixes=('', '_participant'))
unified_df = unified_df.merge(claim_additional_details_df, on='CLM_DTL_ID', how='left', suffixes=('', '_additional'))
unified_df = unified_df.merge(claim_injury_details_df, on='CLM_DTL_ID', how='left', suffixes=('', '_injury'))
unified_df = unified_df.merge(payment_details_df, on='CLM_DTL_ID', how='left', suffixes=('', '_payment'))

# Convert date columns to datetime
print("Converting date columns to datetime...")
date_columns = ['CLM_OCCR_DT', 'CLM_RPT_DT', 'PLCY_STRT_DT', 'PLCY_END_DT', 'CUST_DOB', 'CUST_DOD']
for col in date_columns:
    unified_df[col] = pd.to_datetime(unified_df[col], errors='coerce')

# Use Case 1: Late claim reporting (more than 30 days after the occurrence)
unified_df.loc[(unified_df['CLM_RPT_DT'] - unified_df['CLM_OCCR_DT']).dt.days > 30, 'FRAUD_INDICATOR'] = 1

# Use Case 2: Occurrence on a weekend or public holiday
holidays = ['2023-01-01', '2023-12-25']
unified_df.loc[(unified_df['CLM_OCCR_DT'].dt.weekday >= 5) | (unified_df['CLM_OCCR_DT'].isin(holidays)), 'FRAUD_INDICATOR'] = 1

# Use Case 3: Occurrence date before the policy start date or after policy end date
unified_df.loc[(unified_df['CLM_OCCR_DT'] < unified_df['PLCY_STRT_DT']) | (unified_df['CLM_OCCR_DT'] > unified_df['PLCY_END_DT']), 'FRAUD_INDICATOR'] = 1

# Use Case 4: Occurrence date is after the injury report date
unified_df.loc[unified_df['CLM_OCCR_DT'] > unified_df['CLM_RPT_DT'], 'FRAUD_INDICATOR'] = 1

# Use Case 5: Injury type and job title mismatch
unified_df.loc[(unified_df['INJURY_TYP_CD'] == 'Head Injury') & (unified_df['CLMT_JOB_TTL'] == 'Clerk'), 'FRAUD_INDICATOR'] = 1

# Use Case 6: Customer state does not match occurrence state
unified_df.loc[unified_df['CUST_STATE'] != unified_df['CLM_OCCR_STATE'], 'FRAUD_INDICATOR'] = 1

# Use Case 7: Declined claims with payments
unified_df.loc[(unified_df['CLM_STS_CD'] == 'Declined') & (unified_df['PAYMENT_AMOUNT'] > 0), 'FRAUD_INDICATOR'] = 1

# Use Case 8: Injury type is not related to work
unified_df.loc[unified_df['INJURY_TYP_CD'].isin(['Personal', 'Non-Work Related']), 'FRAUD_INDICATOR'] = 1

# Use Case 9: Claimant age is less than 18 or greater than 70
unified_df.loc[(unified_df['CUST_AGE'] < 18) | (unified_df['CUST_AGE'] > 70), 'FRAUD_INDICATOR'] = 1

# Use Case 10: Date of death exists for the claimant
unified_df.loc[unified_df['CUST_DOD'].notnull(), 'FRAUD_INDICATOR'] = 1

# Use Case 11: Claim frequency is too high (multiple claims in a short period)
unified_df = unified_df.sort_values(by=['CUST_ID', 'CLM_OCCR_DT'])
unified_df['CLAIM_FREQUENCY'] = unified_df.groupby('CUST_ID')['CLM_OCCR_DT'].transform(lambda x: x.diff().dt.days)
unified_df.loc[unified_df['CLAIM_FREQUENCY'] < 30, 'FRAUD_INDICATOR'] = 1

# Use Case 12: High claim amounts (above $10,000)
unified_df.loc[unified_df['CLM_AMT'] > 10000, 'FRAUD_INDICATOR'] = 1

# Use Case 13: Payments exceeding claim amount
unified_df['TOTAL_PAYMENT_AMOUNT'] = unified_df.groupby('CLM_DTL_ID')['PAYMENT_AMOUNT'].transform('sum')
unified_df.loc[unified_df['TOTAL_PAYMENT_AMOUNT'] > unified_df['CLM_AMT'], 'FRAUD_INDICATOR'] = 1

# Use Case 14: Claims with multiple payment failures
unified_df['FAILED_PAYMENTS'] = unified_df.groupby('CLM_DTL_ID')['PAYMENT_STATUS'].transform(lambda x: (x == 'Failed').sum())
unified_df.loc[unified_df['FAILED_PAYMENTS'] > 3, 'FRAUD_INDICATOR'] = 1

# Use Case 15: Claims for injuries with unusual severity (e.g., "Severe" for simple bruises)
unified_df.loc[(unified_df['INJURY_TYP_CD'] == 'Bruise') & (unified_df['INJURY_SEVERITY'] == 'Severe'), 'FRAUD_INDICATOR'] = 1

# Use Case 16: Use of unusual payment methods (like cryptocurrencies)
unified_df.loc[unified_df['PAYMENT_METHOD'].isin(['Crypto']), 'FRAUD_INDICATOR'] = 1

# Use Case 17: Claimant is linked to another fraudulent claim
fraud_claims = unified_df[unified_df['FRAUD_INDICATOR'] == 1]['CUST_ID'].unique()
unified_df.loc[unified_df['CUST_ID'].isin(fraud_claims), 'FRAUD_INDICATOR'] = 1

# Use Case 18: High claim frequency (more than 3 claims within 60 days)
unified_df['CLAIM_FREQUENCY'] = unified_df.groupby('CUST_ID')['CLM_OCCR_DT'].transform(lambda x: x.diff().dt.days)
unified_df['HIGH_CLAIM_FREQUENCY'] = unified_df.groupby('CUST_ID')['CLAIM_FREQUENCY'].transform(lambda x: (x < 60).sum())
unified_df.loc[unified_df['HIGH_CLAIM_FREQUENCY'] > 3, 'FRAUD_INDICATOR'] = 1

# Use Case 19: Claims submitted during unusual business hours
unified_df['HOUR_REPORTED'] = pd.to_datetime(unified_df['CLM_RPT_DT']).dt.hour
unified_df.loc[(unified_df['HOUR_REPORTED'] < 6) | (unified_df['HOUR_REPORTED'] > 22), 'FRAUD_INDICATOR'] = 1

# Use Case 20: Policyholder has an expired or inactive policy
unified_df.loc[unified_df['PLCY_END_DT'] < unified_df['CLM_OCCR_DT'], 'FRAUD_INDICATOR'] = 1

# Use Case 21: Multiple injuries for a single claim (unusual scenario)
injury_count = unified_df.groupby('CLM_DTL_ID')['INJURY_TYP_CD'].nunique()
unified_df.loc[unified_df['CLM_DTL_ID'].isin(injury_count[injury_count > 3].index), 'FRAUD_INDICATOR'] = 1

# Use Case 22: Large claim amount compared to policyholder's historical claim average
average_claim = unified_df.groupby('CUST_ID')['CLM_AMT'].transform('mean')
unified_df.loc[unified_df['CLM_AMT'] > 1.5 * average_claim, 'FRAUD_INDICATOR'] = 1

# Use Case 23: Repetitive claim injuries (same injury type in multiple claims)
injury_repeats = unified_df.groupby(['CUST_ID', 'INJURY_TYP_CD']).size().reset_index(name='COUNT')
repeated_injuries = injury_repeats[injury_repeats['COUNT'] > 3]['CUST_ID'].unique()
unified_df.loc[unified_df['CUST_ID'].isin(repeated_injuries), 'FRAUD_INDICATOR'] = 1

# Use Case 24: Claims with inconsistencies in injury descriptions
unified_df.loc[(unified_df['INJURY_TYP_CD'] == 'Head Injury') & (unified_df['INJURY_SEVERITY'] == 'Low'), 'FRAUD_INDICATOR'] = 1

# Use Case 25: Injuries involving complex medical codes
unified_df.loc[unified_df['INJURY_TYP_CD'].str.contains('Concussion', na=False), 'FRAUD_INDICATOR'] = 1

# Use Case 26: Claims from high-risk geographic locations
high_risk_states = ['FL', 'CA', 'NV']
unified_df.loc[unified_df['CLM_OCCR_STATE'].isin(high_risk_states), 'FRAUD_INDICATOR'] = 1

# Use Case 27: Inconsistent injury details for same policyholder
unified_df['INJURY_COMBO'] = unified_df['INJURY_TYP_CD'] + unified_df['INJURY_SEVERITY']
inconsistent_injuries = unified_df.groupby('CUST_ID')['INJURY_COMBO'].nunique()
unified_df.loc[unified_df['CUST_ID'].isin(inconsistent_injuries[inconsistent_injuries > 2].index), 'FRAUD_INDICATOR'] = 1

# Use Case 28: Claimant's age is inconsistent with the job title
unified_df.loc[(unified_df['CUST_AGE'] < 25) & (unified_df['CLMT_JOB_TTL'] == 'Executive'), 'FRAUD_INDICATOR'] = 1

# Use Case 29: Payments made to accounts flagged as suspicious
unified_df.loc[unified_df['PAYMENT_METHOD'].isin(['Wire Transfer']), 'FRAUD_INDICATOR'] = 1

# Use Case 30: Claims with inconsistent claim reasons
unified_df.loc[unified_df['INJURY_TYP_CD'] == 'Non-Specific', 'FRAUD_INDICATOR'] = 1

# Use Case 31: Suspicious claims on public holidays
unified_df.loc[unified_df['CLM_OCCR_DT'].dt.strftime('%Y-%m-%d').isin(holidays), 'FRAUD_INDICATOR'] = 1

# Use Case 32: Policyholders with multiple failed payments
unified_df['FAILED_PAYMENTS'] = unified_df.groupby('CUST_ID')['PAYMENT_STATUS'].transform(lambda x: (x == 'Failed').sum())
unified_df.loc[unified_df['FAILED_PAYMENTS'] > 3, 'FRAUD_INDICATOR'] = 1

# Use Case 33: Claims reported multiple times (duplicate claims)
duplicate_claims = unified_df[unified_df.duplicated(subset=['CLM_NO'], keep=False)]
unified_df.loc[duplicate_claims.index, 'FRAUD_INDICATOR'] = 1

# Use Case 34: Policyholder has overlapping active policies
unified_df['POLICY_OVERLAP'] = unified_df.groupby('CUST_ID')['PLCY_NO'].transform('nunique')
unified_df.loc[unified_df['POLICY_OVERLAP'] > 1, 'FRAUD_INDICATOR'] = 1

# Use Case 35: Claims submitted outside of policy coverage dates
unified_df.loc[(unified_df['CLM_OCCR_DT'] < unified_df['PLCY_STRT_DT']) | (unified_df['CLM_OCCR_DT'] > unified_df['PLCY_END_DT']), 'FRAUD_INDICATOR'] = 1

# Use Case 36: Claims with excessive payments made in short time
unified_df['PAYMENT_SPAN'] = unified_df.groupby('CLM_DTL_ID')['PAYMENT_DATE'].transform(lambda x: (pd.to_datetime(x).max() - pd.to_datetime(x).min()).days)
unified_df.loc[unified_df['PAYMENT_SPAN'] < 7, 'FRAUD_INDICATOR'] = 1

# Use Case 37: Claims involving claimants with multiple payment accounts
unified_df['PAYMENT_ACCOUNTS'] = unified_df.groupby('CUST_ID')['PAYMENT_METHOD'].transform('nunique')
unified_df.loc[unified_df['PAYMENT_ACCOUNTS'] > 2, 'FRAUD_INDICATOR'] = 1

# Use Case 38: Claims involving multiple payments to a single provider
provider_payments = unified_df.groupby(['CLM_DTL_ID', 'CUST_ID'])['PAYMENT_AMOUNT'].count()
high_payment_claims = provider_payments[provider_payments > 5].index.get_level_values(0)
unified_df.loc[unified_df['CLM_DTL_ID'].isin(high_payment_claims), 'FRAUD_INDICATOR'] = 1

# Use Case 39: Customer age is not consistent with expected working age
unified_df.loc[(unified_df['CUST_AGE'] < 16) | (unified_df['CUST_AGE'] > 80), 'FRAUD_INDICATOR'] = 1

# Use Case 40: Claims with payments after claim has been declined
unified_df.loc[(unified_df['CLM_STS_CD'] == 'Declined') & (unified_df['PAYMENT_AMOUNT'] > 0), 'FRAUD_INDICATOR'] = 1

# Use Case 41: Claims for injuries that do not match with job type
unified_df.loc[(unified_df['INJURY_TYP_CD'] == 'Back Injury') & (unified_df['CLMT_JOB_TTL'] == 'Desk Job'), 'FRAUD_INDICATOR'] = 1

# Use Case 42: Claims involving policyholders with prior fraud history
fraud_claims = unified_df[unified_df['FRAUD_INDICATOR'] == 1]['CUST_ID'].unique()
unified_df.loc[unified_df['CUST_ID'].isin(fraud_claims), 'FRAUD_INDICATOR'] = 1

# Use Case 43: Suspicious payment method usage (e.g., cryptocurrency)
unified_df.loc[unified_df['PAYMENT_METHOD'].isin(['Crypto']), 'FRAUD_INDICATOR'] = 1

# Randomly assign fraud to 20% of claims for training purposes
np.random.seed(42)
random_fraud_indices = np.random.choice(unified_df.index, size=int(0.2 * len(unified_df)), replace=False)
unified_df.loc[random_fraud_indices, 'FRAUD_INDICATOR'] = 1

# Fill NaN fraud indicators with 0 (non-fraudulent)
unified_df['FRAUD_INDICATOR'] = unified_df['FRAUD_INDICATOR'].fillna(0).astype(int)

# Save the updated dataset
unified_df.to_csv('data/unified_dataset.csv', index=False)

print("Unified dataset created with all fraud use cases applied.")
