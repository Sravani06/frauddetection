import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Load CLAIM_DETAILS and CUSTOMER_DETAILS datasets
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')
customer_details_df = pd.read_csv('data/CUSTOMER_DETAILS.csv')

# Number of total claims
total_claims = claim_details_df.shape[0]

# Function to generate CLAIM_PARTICIPANT dataset
def generate_claim_participants(claim_details, customer_details):
    claim_participants = []
    claim_participant_id = 10001  # Starting ID for participant records

    # Filter customers by type
    injured_workers = customer_details[customer_details['CUST_TYP'] == 'prsn']
    medical_providers = customer_details[customer_details['CUST_TYP'] == 'busn']
    insured_customers = customer_details[customer_details['CUST_TYP'] == 'busn']

    for _, claim_row in claim_details.iterrows():
        clm_dtl_id = claim_row['CLM_DTL_ID']
        clm_jur_typ_cd = claim_row['CLM_JUR_TYP_CD']

        # === 1. CLAIMANT (Injured Worker) ===
        claimant = injured_workers.sample(1).iloc[0]
        # 10% chance to assign a worker from a different state for fraud detection
        if np.random.rand() < 0.1:
            claimant = injured_workers.sample(1).iloc[0]
        claim_participants.append([
            claim_participant_id, clm_dtl_id, claimant['CUST_ID'], 'clmt', 'prsn'
        ])
        claim_participant_id += 1

        # === 2. MEDICAL PROVIDER ===
        provider = medical_providers.sample(1).iloc[0]
        # 10% chance to assign a provider from a different state for fraud detection
        if np.random.rand() < 0.1:
            provider = medical_providers.sample(1).iloc[0]
        claim_participants.append([
            claim_participant_id, clm_dtl_id, provider['CUST_ID'], 'provider', 'busn'
        ])
        claim_participant_id += 1

        # === 3. INSURED (Policyholder) ===
        insured = insured_customers.sample(1).iloc[0]
        # 10% chance to assign an insured from a different state for fraud detection
        if np.random.rand() < 0.1:
            insured = insured_customers.sample(1).iloc[0]
        claim_participants.append([
            claim_participant_id, clm_dtl_id, insured['CUST_ID'], 'insured', 'busn'
        ])
        claim_participant_id += 1

    # Convert to a DataFrame
    return pd.DataFrame(claim_participants, columns=[
        'CLM_PTCP_ID', 'CLM_DTL_ID', 'CUST_ID', 'PTCP_TYP', 'CUST_TYP'
    ])

# Generate the dataset
claim_participants_df = generate_claim_participants(claim_details_df, customer_details_df)

# Save the dataset to a CSV file
claim_participants_df.to_csv('data/CLAIM_PARTICIPANT.csv', index=False)

print("CLAIM_PARTICIPANT dataset generated and saved as 'data/CLAIM_PARTICIPANT.csv'.")
