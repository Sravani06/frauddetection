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

    for index, row in claim_details_df.iterrows():
        claim_dtl_id = row['CLM_DTL_ID']
        report_date = row['CLM_RPT_DT']  # CLM_RPT_DT from CLAIM_DETAILS

        # Convert report_date to datetime
        report_date_dt = datetime.strptime(report_date, '%Y-%m-%d')

        # Create Pending Status
        pending_start_date = report_date_dt  # Start date for Pending is equal to CLM_RPT_DT
        pending_end_date = pending_start_date + timedelta(days=np.random.randint(1, 5))

        claim_status.append([
            claim_dtl_id,  # CLAIM_DTL_ID
            clm_sts_id_start,  # CLM_STS_ID
            'Pending',  # CLM_STS_CD
            pending_start_date.strftime('%Y-%m-%d %H:%M:%S'),  # CLM_STS_START_DT
            pending_end_date.strftime('%Y-%m-%d %H:%M:%S')  # CLM_STS_END_DT
        ])
        clm_sts_id_start += 1

        # Create Final Status (Accepted or Declined)
        final_status = np.random.choice(['Accepted', 'Declined'])
        final_start_date = pending_end_date + timedelta(days=1)

        claim_status.append([
            claim_dtl_id,  # CLAIM_DTL_ID
            clm_sts_id_start,  # CLM_STS_ID
            final_status,  # CLM_STS_CD
            final_start_date.strftime('%Y-%m-%d %H:%M:%S'),  # CLM_STS_START_DT
            None  # CLM_STS_END_DT is NULL for final status
        ])
        clm_sts_id_start += 1

    # Convert to DataFrame
    return pd.DataFrame(claim_status, columns=[
        'CLM_DTL_ID', 'CLM_STS_ID', 'CLM_STS_CD', 'CLM_STS_START_DT', 'CLM_STS_END_DT'
    ])

# Load CLAIM_DETAILS dataset
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')

# Generate CLAIM_STATUS dataset
claim_status_df = generate_claim_status(claim_details_df)

# Save the dataset to a CSV file
claim_status_df.to_csv('data/CLAIM_STATUS.csv', index=False)

print("CLAIM_STATUS dataset generated and saved as 'CLAIM_STATUS.csv'.")
