import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, timedelta
import random

from scripts.generate_fraud_detection_dataset import states

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Load POLICY_DETAILS dataset
policy_details_df = pd.read_csv('data/POLICY_DETAILS.csv')

# Number of claims to generate
num_claims = 5000  # Generating 10,000 claims as an example

# Function to generate CLAIM_DETAILS dataset
def generate_claim_details(policy_df, customer_df, min_claims=15000, fraud_percentage=0.15):
    print("🚀 Claim details generation started...")
    claim_data = []
    claim_id = 11001  # Start CLM_DTL_ID at 11001
    existing_claim_numbers = set()  # Track unique claim numbers
    blacklisted_providers = ['Prime Health Network', 'Cura Medical Services', 'Alliance Medical']

    total_fraud_claims = int(min_claims * fraud_percentage)  # 15% of claims are fraudulent
    fraud_claims_count = 0

    claimants = customer_df[customer_df['CUST_TYP'] == 'Claimant']

    while len(claim_data) < min_claims:
        for _, claimant in claimants.iterrows():
            if len(claim_data) >= min_claims:
                break

            # Each claimant can have 1 to 10 claims
            num_claims_for_claimant = random.randint(1, 10)

            for _ in range(num_claims_for_claimant):
                if len(claim_data) >= min_claims:
                    break

                policy = policy_df.sample(1).iloc[0]
                policy_number = policy['PLCY_NO']
                policy_start_date = pd.to_datetime(policy['PLCY_STRT_DT']).date()
                policy_end_date = pd.to_datetime(policy['PLCY_END_DT']).date()

                clm_occur_date = fake.date_between(start_date=policy_start_date, end_date=policy_end_date)
                clm_report_date = clm_occur_date + timedelta(days=random.choice([1, 2]))

                clm_amount = round(random.uniform(10, 10000), 2)

                clm_occr_address = fake.street_address()
                clm_occr_city = fake.city()
                clm_occr_zip = fake.zipcode()
                clm_occr_state = random.choice(states)

                clm_fraud_ind = 0
                fraud_reasons = []

                # 💡 Fraud Rules
                if fraud_claims_count < total_fraud_claims:
                    # 1️⃣ Mismatched Occurrence State
                    if random.random() < 0.20:  # 20% of fraud claims have mismatched state
                        clm_occr_state = random.choice([state for state in states if state != policy['PLCY_NO']])
                        clm_fraud_ind = 1
                        fraud_reasons.append('Mismatched Occurrence State')

                    # 2️⃣ Suspicious Claim Amount
                    if clm_amount > 0.9 * policy['CLAIM_LIMIT']:  # Claim amount close to claim limit
                        clm_fraud_ind = 1
                        fraud_reasons.append('Claim Amount Close to Limit')

                    # 3️⃣ Claim Near Policy Expiry
                    if (policy_end_date - clm_occur_date).days < 7:  # Claim close to policy expiration
                        clm_fraud_ind = 1
                        fraud_reasons.append('Claim Near Policy Expiry')

                    # 4️⃣ Short Policy Tenure
                    if policy['PLCY_STRT_DT'] > (pd.to_datetime(clm_occur_date) - timedelta(days=30)).strftime(
                            '%Y-%m-%d'):
                        clm_fraud_ind = 1
                        fraud_reasons.append('Short Policy Tenure')

                    # 5️⃣ Blacklisted Medical Providers
                    if random.random() < 0.05:  # 5% of frauds are linked to blacklisted providers
                        clm_fraud_ind = 1
                        fraud_reasons.append('Blacklisted Provider')

                    fraud_claims_count += 1

                if not fraud_reasons:
                    fraud_reasons.append('None')

                fraud_reason_str = ', '.join(fraud_reasons)

                claim_data.append([
                    claim_id,
                    f"CLM{random.randint(100000, 999999)}",
                    random.choice(states),
                    clm_report_date,
                    clm_occur_date,
                    'Medical',
                    clm_amount,
                    policy_number,
                    clm_occr_address,
                    clm_occr_city,
                    clm_occr_zip,
                    clm_occr_state,
                    clm_fraud_ind,
                    fraud_reason_str
                ])
                claim_id += 1

    claim_df = pd.DataFrame(claim_data, columns=[
        'CLM_DTL_ID', 'CLM_NO', 'CLM_JUR_TYP_CD', 'CLM_RPT_DT', 'CLM_OCCR_DT', 'CLM_TYP',
        'CLM_AMT', 'PLCY_NO', 'CLM_OCCR_ADDR', 'CLM_OCCR_CITY', 'CLM_OCCR_ZIP',
        'CLM_OCCR_STATE', 'CLM_FRAUD_IND', 'FRAUD_REASON'
    ])

    print(f"✅ Claim details generation completed. Total claims: {len(claim_df)}")
    print(
        f"🕵️‍♂️ Total fraudulent claims generated: {fraud_claims_count} out of {min_claims} ({(fraud_claims_count / min_claims) * 100:.2f}%)")
    return claim_df


# Generate the dataset
claim_details_df = generate_claim_details(num_claims, policy_details_df)

# Save the dataset to a CSV file
claim_details_df.to_csv('data/CLAIM_DETAILS.csv', index=False)

print("✅ CLAIM_DETAILS dataset generated and saved with PLCY_NO as 'data/CLAIM_DETAILS.csv'.")
