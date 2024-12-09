import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Load CLAIM_DETAILS and CLAIM_STATUS datasets
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')
claim_status_df = pd.read_csv('data/CLAIM_STATUS.csv')

# Function to generate PAYMENT_DETAILS dataset
def generate_payment_details(claim_details, claim_status):
    payment_details = []
    payment_id_start = 50001  # Starting ID for PAYMENT_ID
    payment_methods = ['Check', 'Wire Transfer', 'ACH', 'Direct Deposit']
    payment_statuses = ['Processed', 'Pending', 'Failed']
    benefit_types = ['DIS', 'LOST_WAGES', 'PERM_IMPAIRMENT', 'VOC_REHAB']

    # Select 30% of claims to have "fraud-like characteristics"
    fraud_like_claim_ids = np.random.choice(claim_details['CLM_DTL_ID'], size=int(0.3 * len(claim_details)), replace=False)

    for _, claim_row in claim_details.iterrows():
        clm_id = claim_row['CLM_DTL_ID']
        clm_rpt_dt = datetime.strptime(claim_row['CLM_RPT_DT'], '%Y-%m-%d')
        clm_amt = claim_row['CLM_AMT']
        is_fraud_like_claim = clm_id in fraud_like_claim_ids

        # Determine number of payments (1 to 3 payments per claim)
        num_payments = np.random.randint(1, 4) if is_fraud_like_claim else 1

        remaining_amount = clm_amt

        for _ in range(num_payments):
            payment_id = payment_id_start
            payment_id_start += 1

            # Fraud Pattern: Payment date before claim report date
            if is_fraud_like_claim and np.random.rand() < 0.2:
                payment_date = clm_rpt_dt - timedelta(days=np.random.randint(1, 30))
            else:
                payment_date = clm_rpt_dt + timedelta(days=np.random.randint(0, 60))

            # Payment amount
            if is_fraud_like_claim and np.random.rand() < 0.2:
                payment_amount = round(np.random.uniform(clm_amt, clm_amt * 1.5), 2)  # Overpayment
            else:
                payment_amount = round(min(remaining_amount, np.random.uniform(50, 5000)), 2)

            remaining_amount -= payment_amount
            remaining_amount = max(0, remaining_amount)

            # Fraud Pattern: Random payment method
            payment_method = np.random.choice(payment_methods) if is_fraud_like_claim else np.random.choice(['Check', 'Wire Transfer', 'ACH'])

            # Fraud Pattern: Multiple status changes
            payment_status = np.random.choice(payment_statuses) if is_fraud_like_claim else 'Processed'

            payment_type = np.random.choice(['Medical', 'Indemnity'])
            bnft_typ_cd = np.random.choice(benefit_types) if payment_type == 'Indemnity' else None

            # Additional fields
            payee_name = fake.name()
            payee_account = 'XXXX-XXXX-' + str(np.random.randint(1000, 9999))
            currency = 'USD'
            exchange_rate = 1.0

            payment_details.append([
                clm_id, payment_id, payment_date.strftime('%Y-%m-%d %H:%M:%S'), payment_amount,
                payment_status, payment_method, payment_type, bnft_typ_cd,
                payee_name, payee_account, currency, exchange_rate
            ])

    # Convert to DataFrame
    return pd.DataFrame(payment_details, columns=[
        'CLM_DTL_ID', 'PAYMENT_ID', 'PAYMENT_DATE', 'PAYMENT_AMOUNT',
        'PAYMENT_STATUS', 'PAYMENT_METHOD', 'PAYMENT_TYPE', 'BNFT_TYP_CD',
        'PAYEE_NAME', 'PAYEE_ACCOUNT', 'CURRENCY', 'EXCHANGE_RATE'
    ])

# Generate the dataset
payment_details_df = generate_payment_details(claim_details_df, claim_status_df)

# Save the dataset to a CSV file
payment_details_df.to_csv('data/PAYMENT_DETAILS.csv', index=False)

print("PAYMENT_DETAILS dataset generated and saved as 'data/PAYMENT_DETAILS.csv'.")
