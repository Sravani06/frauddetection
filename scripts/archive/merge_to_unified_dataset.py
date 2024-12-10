import pandas as pd

# Load CSV files
print("Loading CSV files...")
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')
customer_details_df = pd.read_csv('data/CUSTOMER_DETAILS.csv')
policy_details_df = pd.read_csv('data/POLICY_DETAILS.csv')
claim_status_df = pd.read_csv('data/CLAIM_STATUS.csv')
claim_participant_df = pd.read_csv('data/CLAIM_PARTICIPANT.csv')
claim_additional_details_df = pd.read_csv('data/CLAIM_ADDITIONAL_DETAILS.csv')
claim_injury_details_df = pd.read_csv('data/CLAIM_INJURY_DETAILS.csv')
payment_details_df = pd.read_csv('data/PAYMENT_DETAILS.csv')

# Step 1: Merge CUSTOMER_DETAILS with CLAIM_PARTICIPANT
print("Merging CUSTOMER_DETAILS with CLAIM_PARTICIPANT...")
claim_with_participants = claim_participant_df.merge(
    customer_details_df,
    on='CUST_ID',
    how='left',
    suffixes=('', '_cust')
)

# Step 2: Merge CLAIM_PARTICIPANT with CLAIM_DETAILS
print("Merging CLAIM_PARTICIPANT with CLAIM_DETAILS...")
claim_full = claim_with_participants.merge(
    claim_details_df,
    on='CLM_DTL_ID',
    how='left',
    suffixes=('', '_claim')
)

# Step 3: Merge POLICY_DETAILS with CLAIM_DETAILS on PLCY_NO
print("Merging POLICY_DETAILS with CLAIM_DETAILS...")
claim_full = claim_full.merge(
    policy_details_df,
    on='PLCY_NO',
    how='left',
    suffixes=('', '_policy')
)

# Step 4: Merge CLAIM_STATUS with CLAIM_DETAILS
print("Merging CLAIM_STATUS with CLAIM_DETAILS...")
final_status = claim_status_df.sort_values(by=['CLM_DTL_ID', 'CLM_STS_START_DT']).groupby('CLM_DTL_ID').last().reset_index()
final_status = final_status[['CLM_DTL_ID', 'CLM_STS_CD']].rename(columns={'CLM_STS_CD': 'FINAL_STATUS'})
claim_full = claim_full.merge(final_status, on='CLM_DTL_ID', how='left')
claim_full = claim_full.merge(
    claim_status_df,
    on='CLM_DTL_ID',
    how='left',
    suffixes=('', '_status')
)

# Step 5: Merge CLAIM_ADDITIONAL_DETAILS with CLAIM_DETAILS
print("Merging CLAIM_ADDITIONAL_DETAILS with CLAIM_DETAILS...")
claim_full = claim_full.merge(
    claim_additional_details_df,
    on='CLM_DTL_ID',
    how='left',
    suffixes=('', '_addl')
)

# Step 6: Aggregate injury details for CLAIM_INJURY_DETAILS
print("Aggregating CLAIM_INJURY_DETAILS for each claim...")

# Step 6.1: Aggregate NUM_INJURIES (preserve existing logic)
print("Calculating number of injuries per claim...")
injury_count_agg = claim_injury_details_df.groupby('CLM_DTL_ID').agg({
    'INJURY_TYP_CD': 'count'
}).rename(columns={'INJURY_TYP_CD': 'NUM_INJURIES'}).reset_index()

# Step 6.2: Aggregate INJURY_POB (new logic)
print("Aggregating parts of body injured for each claim...")
injury_pob_agg = claim_injury_details_df.groupby('CLM_DTL_ID').agg({
    'INJURY_POB': lambda x: ', '.join(x.unique())  # Combine unique injury parts of the body
}).rename(columns={'INJURY_POB': 'INJURY_POB'}).reset_index()

# Step 6.3: Aggregate INJURY_TYP_CD (new logic)
print("Aggregating types of injury for each claim...")
injury_typ_cd_agg = claim_injury_details_df.groupby('CLM_DTL_ID').agg({
    'INJURY_TYP_CD': lambda x: ', '.join(x.unique())  # Combine unique injury types
}).rename(columns={'INJURY_TYP_CD': 'INJURY_TYP_CD'}).reset_index()

# Step 6.4: Merge NUM_INJURIES, INJURY_POB, and INJURY_TYP_CD into the claim_full dataset
print("Merging injury details (NUM_INJURIES, INJURY_POB, INJURY_TYP_CD) into claim_full...")

# Merge NUM_INJURIES
claim_full = claim_full.merge(
    injury_count_agg,
    on='CLM_DTL_ID',
    how='left',
    suffixes=('', '_injury_count')
)

# Merge INJURY_POB
claim_full = claim_full.merge(
    injury_pob_agg,
    on='CLM_DTL_ID',
    how='left',
    suffixes=('', '_injury_pob')
)

# Merge INJURY_TYP_CD
claim_full = claim_full.merge(
    injury_typ_cd_agg,
    on='CLM_DTL_ID',
    how='left',
    suffixes=('', '_injury_typ_cd')
)


# Step 7: Aggregate payment details for PAYMENT_DETAILS
print("Aggregating PAYMENT_DETAILS for each claim...")

# Include PAYMENT_DATE in aggregation
payment_agg = payment_details_df.groupby('CLM_DTL_ID').agg({
    'PAYMENT_AMOUNT': 'sum',
    'PAYMENT_ID': 'count',
    'PAYMENT_DATE': lambda x: ', '.join(pd.to_datetime(x).dt.strftime('%Y-%m-%d').unique())  # Join unique payment dates
}).rename(columns={
    'PAYMENT_AMOUNT': 'TOTAL_PAYMENT_AMOUNT',
    'PAYMENT_ID': 'TOTAL_PAYMENTS',
    'PAYMENT_DATE': 'PAYMENT_DATE'
}).reset_index()

claim_full = claim_full.merge(
    payment_agg,
    on='CLM_DTL_ID',
    how='left',
    suffixes=('', '_payment')
)

# Drop unnecessary columns
print("Dropping unnecessary columns...")
claim_full.drop(columns=['CUST_ID_cust', 'CUST_FRST_NM', 'CUST_LST_NM'], inplace=True, errors='ignore')

# Convert date columns to datetime
date_columns = ['CLM_OCCR_DT', 'CLM_RPT_DT', 'PLCY_STRT_DT', 'PLCY_END_DT', 'CUST_DOB', 'CUST_DOD', 'CLM_STS_START_DT']
for col in date_columns:
    if col in claim_full.columns:
        claim_full[col] = pd.to_datetime(claim_full[col], errors='coerce')

# Fill missing values for numerical columns with 0
numerical_columns = ['TOTAL_PAYMENT_AMOUNT', 'TOTAL_PAYMENTS', 'NUM_INJURIES']
claim_full[numerical_columns] = claim_full[numerical_columns].fillna(0)

# Calculate MULTIPLE_INJURIES
claim_full['MULTIPLE_INJURIES'] = (claim_full['NUM_INJURIES'] > 2).astype(int)

# Export the final unified dataset
print(f"Exporting unified dataset to 'data/unified_dataset.csv'...")
claim_full.to_csv('data/unified_dataset.csv', index=False)

print(f"Unified dataset successfully saved with {claim_full.shape[0]} rows and {claim_full.shape[1]} columns.")

