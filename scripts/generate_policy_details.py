import pandas as pd
import numpy as np
from faker import Faker
from datetime import timedelta, date

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Number of policies to generate
num_policies = 1000  # Changeable as needed


def generate_policy_details(num_policies):
    policy_details = []

    for i in range(1, num_policies + 1):
        # Policy Unique Identifiers
        plcy_dtl_id = i
        plcy_no = f"COF{str(i).zfill(7)}"

        # Policy Start and End Dates
        plcy_strt_dt = fake.date_between(start_date=date(2006, 1, 1), end_date=date(2024, 12, 31))
        plcy_end_dt = plcy_strt_dt + timedelta(days=365)  # 1-year policy duration

        # Policy Status
        plcy_sts = np.random.choice(['Active', 'Lapsed', 'Canceled'], p=[0.7, 0.2, 0.1])

        # Premium, Claim Limit, and Deductible
        premium_amt = round(np.random.uniform(500.00, 5000.00), 2)
        claim_limit = round(np.random.uniform(10000.00, 100000.00), 2)
        claim_deductible = round(np.random.uniform(500.00, 5000.00), 2)

        # New Column: Policy Maximum Coverage
        # Set it as a random percentage (between 80% and 120%) of the claim limit.
        plcy_max_coverage = round(claim_limit * np.random.uniform(0.8, 1.2), 2)

        policy_details.append([
            plcy_dtl_id,
            plcy_no,
            plcy_strt_dt,
            plcy_end_dt,
            plcy_sts,
            premium_amt,
            claim_limit,
            claim_deductible,
            plcy_max_coverage
        ])

    return pd.DataFrame(policy_details, columns=[
        'PLCY_DTL_ID',
        'PLCY_NO',
        'PLCY_STRT_DT',
        'PLCY_END_DT',
        'PLCY_STS',
        'PREMIUM_AMT',
        'CLAIM_LIMIT',
        'CLAIM_DEDUCTIBLE',
        'PLCY_MAX_COVERAGE'
    ])


# Generate and save the policy details dataset
policy_details_df = generate_policy_details(num_policies)
policy_details_df.to_csv('data/POLICY_DETAILS.csv', index=False)

print("POLICY_DETAILS dataset generated and saved as 'data/POLICY_DETAILS.csv'.")
