import pandas as pd
import numpy as np
from faker import Faker
from datetime import timedelta

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Load CLAIM_DETAILS and CLAIM_STATUS datasets
try:
    claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')
    claim_status_df = pd.read_csv('data/CLAIM_STATUS.csv')
except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    exit(1)

# Function to check if a claim is denied
def is_claim_denied(claim_id, claim_status):
    try:
        final_status = claim_status[claim_status['CLM_DTL_ID'] == claim_id].iloc[-1]
        return final_status['CLM_STS_CD'] == 'Declined'
    except IndexError:
        print(f"Warning: No status found for claim ID {claim_id}. Skipping.")
        return True

# Function to generate PAYMENT_DETAILS dataset
def generate_payment_details(claim_details, claim_status):
    payment_details = []
    payment_id_start = 50001  # Starting ID for PAYMENT_ID

    # Iterate over each claim in CLAIM_DETAILS
    for _, claim_row in claim_details.iterrows():
        clm_id = claim_row['CLM_DTL_ID']
        clm_occr_dt = pd.to_datetime(claim_row['CLM_OCCR_DT'], errors='coerce')
        clm_amt = claim_row['CLM_AMT']

        # Check for invalid data
        if pd.isna(clm_occr_dt) or pd.isna(clm_amt):
            print(f"Skipping claim ID {clm_id} due to missing data.")
            continue

        # Skip denied claims
        if is_claim_denied(clm_id, claim_status):
            continue

        # Generate multiple payments for the claim
        remaining_amount = clm_amt
        iteration_count = 0
        while remaining_amount > 0:
            iteration_count += 1
            if iteration_count > 50:  # Safety check to prevent infinite loops
                print(f"Exceeded iteration limit for claim ID {clm_id}. Skipping.")
                break

            # PAYMENT_AMOUNT: Random portion (20% to 50%) of remaining amount
            payment_amount = round(min(remaining_amount, clm_amt * np.random.uniform(0.2, 0.5)), 2)
            remaining_amount -= payment_amount

            # PAYMENT_DATE: Random date on or after CLM_OCCR_DT
            payment_date = clm_occr_dt + timedelta(days=np.random.randint(0, 30))

            # PAYMENT_STATUS: Randomly choose status
            payment_status = np.random.choice(['Processed', 'Pending', 'Failed'])

            # PAYMENT_METHOD: Randomly choose payment method
            payment_method = np.random.choice(['Check', 'Wire Transfer', 'ACH'])

            # PAYMENT_TYP: Either 'med' or 'ind'
            payment_typ = np.random.choice(['med', 'ind'])

            # BNFT_TYP_CD: Only if PAYMENT_TYP is 'ind'
            bnft_typ_cd = None
            if payment_typ == 'ind':
                bnft_typ_cd = np.random.choice(['DIS', 'LOST_WAGES', 'PERM_IMPAIRMENT', 'VOC_REHAB'])

            # Append the record
            payment_details.append([
                clm_id, payment_id_start, payment_date, payment_amount,
                payment_status, payment_method, payment_typ, bnft_typ_cd
            ])
            payment_id_start += 1

    # Convert to DataFrame
    return pd.DataFrame(payment_details, columns=[
        'CLM_ID', 'PAYMENT_ID', 'PAYMENT_DATE', 'PAYMENT_AMOUNT',
        'PAYMENT_STATUS', 'PAYMENT_METHOD', 'PAYMENT_TYP', 'BNFT_TYP_CD'
    ])

# Debugging: Process a subset of claims for testing
print("Processing payment details generation...")
claim_details_df = claim_details_df.head(10)  # Remove this line to process the full dataset

# Generate the PAYMENT_DETAILS dataset
payment_details_df = generate_payment_details(claim_details_df, claim_status_df)

# Save the dataset to a CSV file
try:
    payment_details_df.to_csv('data/PAYMENT_DETAILS.csv', index=False)
    print("PAYMENT_DETAILS dataset generated and saved as 'data/PAYMENT_DETAILS.csv'.")
except Exception as e:
    print(f"Error saving PAYMENT_DETAILS.csv: {e}")
