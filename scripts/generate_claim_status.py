import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
np.random.seed(42)


# Function to generate CLAIM_STATUS dataset
def generate_claim_status(claim_details_df):
    claim_status = []
    clm_sts_id_start = 10001  # Starting ID for CLM_STS_ID

    total_claims = len(claim_details_df)

    # Select 10% of claims to remain in "Pending" status
    pending_only_claim_ids = np.random.choice(claim_details_df['CLM_DTL_ID'], size=int(0.1 * total_claims),
                                              replace=False)

    # Randomly select 30% of the total claims for fraud-like patterns
    fraud_like_claim_ids = np.random.choice(claim_details_df['CLM_DTL_ID'], size=int(0.3 * total_claims), replace=False)

    for index, row in claim_details_df.iterrows():
        claim_dtl_id = row['CLM_DTL_ID']
        report_date = row['CLM_RPT_DT']  # CLM_RPT_DT from CLAIM_DETAILS
        report_date_dt = datetime.strptime(report_date, '%Y-%m-%d')

        is_fraud_like_claim = claim_dtl_id in fraud_like_claim_ids
        is_pending_only_claim = claim_dtl_id in pending_only_claim_ids

        # === 1. Create Pending Status ===
        pending_start_date = report_date_dt  # Start date for Pending is equal to CLM_RPT_DT

        # If it's a fraud-like claim, delay the end of the pending status
        pending_end_delay = (
            np.random.randint(30, 100) if is_fraud_like_claim
            else np.random.randint(1, 5)
        )

        # If the claim is in the "pending-only" list, extend the pending period to over 180 days
        if is_pending_only_claim:
            pending_end_delay = np.random.randint(181, 365)

        pending_end_date = pending_start_date + timedelta(days=pending_end_delay)

        status_reason = 'Initial Review' if not is_fraud_like_claim else np.random.choice(
            ['Delayed Docs', 'System Error', 'Claim Resubmission'])
        status_updated_by = np.random.choice(['System', 'User'])
        status_source = np.random.choice(['Manual', 'Automated'])

        claim_status.append([
            claim_dtl_id,  # CLAIM_DTL_ID
            clm_sts_id_start,  # CLM_STS_ID
            'Pending',  # CLM_STS_CD
            pending_start_date.strftime('%Y-%m-%d %H:%M:%S'),  # CLM_STS_START_DT
            pending_end_date.strftime('%Y-%m-%d %H:%M:%S') if not is_pending_only_claim else None,  # CLM_STS_END_DT
            status_reason,  # STATUS_REASON
            status_updated_by,  # STATUS_UPDATED_BY
            status_source  # STATUS_SOURCE
        ])
        clm_sts_id_start += 1

        # If the claim is one of the 10% that stays in "Pending", skip final status generation
        if is_pending_only_claim:
            continue

        # === 2. Create Final Status (Accepted or Declined) ===
        final_status = np.random.choice(['Accepted', 'Declined'], p=[0.7, 0.3])

        # If it's a fraud-like claim, introduce inconsistencies in the final status
        if is_fraud_like_claim and np.random.rand() < 0.3:
            final_status = 'Declined'

        final_start_date = pending_end_date + timedelta(days=1)

        if is_fraud_like_claim and np.random.rand() < 0.2:
            final_start_date = pending_start_date + timedelta(days=np.random.randint(10, 50))  # Inconsistent start

        status_reason = 'Claim Finalized' if not is_fraud_like_claim else np.random.choice(
            ['Resubmission', 'Duplicate Claim', 'Insufficient Info'])
        status_updated_by = np.random.choice(['System', 'User'])
        status_source = np.random.choice(['Manual', 'Automated'])

        claim_status.append([
            claim_dtl_id,  # CLAIM_DTL_ID
            clm_sts_id_start,  # CLM_STS_ID
            final_status,  # CLM_STS_CD
            final_start_date.strftime('%Y-%m-%d %H:%M:%S'),  # CLM_STS_START_DT
            None,  # CLM_STS_END_DT is NULL for final status
            status_reason,  # STATUS_REASON
            status_updated_by,  # STATUS_UPDATED_BY
            status_source  # STATUS_SOURCE
        ])
        clm_sts_id_start += 1

    # Convert to DataFrame
    return pd.DataFrame(claim_status, columns=[
        'CLM_DTL_ID', 'CLM_STS_ID', 'CLM_STS_CD', 'CLM_STS_START_DT',
        'CLM_STS_END_DT', 'STATUS_REASON', 'STATUS_UPDATED_BY', 'STATUS_SOURCE'
    ])


# Load CLAIM_DETAILS dataset
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')

# Generate CLAIM_STATUS dataset
claim_status_df = generate_claim_status(claim_details_df)

# Save the dataset to a CSV file
claim_status_df.to_csv('data/CLAIM_STATUS.csv', index=False)

print("CLAIM_STATUS dataset generated and saved as 'data/CLAIM_STATUS.csv'.")
