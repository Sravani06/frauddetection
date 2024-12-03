import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, timedelta

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Load POLICY_DETAILS dataset
policy_details_df = pd.read_csv('data/POLICY_DETAILS.csv')

# Number of claims to generate
num_claims = 1000

# Function to generate CLAIM_DETAILS dataset
def generate_claim_details(num_records, policy_details):
    claim_details = []
    start_date = date(2006, 1, 1)
    end_date = date(2024, 12, 31)
    policy_list = policy_details.to_dict('records')  # Convert policies to a list of dicts

    for i in range(1, num_records + 1):
        # CLM_DTL_ID: Incremental ID
        clm_dtl_id = i

        # CLM_NO: 7-digit unique claim number starting with the claim year
        clm_rpt_dt = fake.date_between(start_date=start_date, end_date=end_date)
        clm_year = clm_rpt_dt.year
        clm_no = f"{clm_year}{str(i).zfill(4)}"  # Year + 4-digit incremental number

        # Select a random policy
        selected_policy = np.random.choice(policy_list)

        # Get the policy details
        plcy_no = selected_policy['PLCY_NO']
        plcy_start_dt = pd.to_datetime(selected_policy['PLCY_STRT_DT'])
        plcy_end_dt = pd.to_datetime(selected_policy['PLCY_END_DT'])

        # Ensure CLM_OCCR_DT is between PLCY_STRT_DT and PLCY_END_DT
        clm_occr_dt = fake.date_between(start_date=plcy_start_dt.date(), end_date=plcy_end_dt.date())

        # CLM_JUR_TYP_CD: Random state code
        state_codes = ['CA', 'VA', 'NY', 'TX', 'FL', 'WA', 'MA', 'NV']
        clm_jur_typ_cd = np.random.choice(state_codes)

        # CLM_OCCR_ADDR, CLM_OCCR_CITY, CLM_OCCR_ZIP, CLM_OCCR_STATE
        clm_occr_addr = fake.street_address()
        clm_occr_city = fake.city()
        clm_occr_zip = fake.zipcode()
        clm_occr_state = clm_jur_typ_cd

        # CLM_TYP: Randomly assign "Medical" or "Indemnity"
        clm_typ = np.random.choice(['Medical', 'Indemnity'])

        # CLM_AMT: Random decimal value between 200 and 10,000
        clm_amt = round(np.random.uniform(200.00, 10000.00), 2)

        # Append the record to the list
        claim_details.append([
            clm_dtl_id, clm_no, plcy_no, clm_jur_typ_cd, clm_rpt_dt, clm_occr_dt,
            clm_occr_addr, clm_occr_city, clm_occr_zip, clm_occr_state, clm_typ, clm_amt
        ])

    # Convert to a DataFrame
    return pd.DataFrame(claim_details, columns=[
        'CLM_DTL_ID', 'CLM_NO', 'PLCY_NO', 'CLM_JUR_TYP_CD', 'CLM_RPT_DT', 'CLM_OCCR_DT',
        'CLM_OCCR_ADDR', 'CLM_OCCR_CITY', 'CLM_OCCR_ZIP', 'CLM_OCCR_STATE', 'CLM_TYP', 'CLM_AMT'
    ])

# Generate the dataset
claim_details_df = generate_claim_details(num_claims, policy_details_df)

# Save the dataset to a CSV file
claim_details_df.to_csv('data/CLAIM_DETAILS.csv', index=False)

print("CLAIM_DETAILS dataset generated and saved as 'data/CLAIM_DETAILS.csv'.")
