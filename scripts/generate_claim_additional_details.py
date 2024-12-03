import pandas as pd
import numpy as np
from faker import Faker
from datetime import timedelta

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Predefined list of industries
industries = [
    "Information Technology", "Healthcare", "Finance", "Retail", "Manufacturing",
    "Education", "Transportation", "Real Estate", "Hospitality", "Construction"
]

# Load CLAIM_DETAILS dataset
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')

# Function to generate CLAIM_ADDITIONAL_DETAILS dataset
def generate_claim_additional_details(claim_details):
    additional_details = []

    for _, claim_row in claim_details.iterrows():
        clm_id = claim_row['CLM_DTL_ID']
        clm_occr_dt = pd.to_datetime(claim_row['CLM_OCCR_DT'])

        # Generate CLMT_HIRE_DT: A date before CLM_OCCR_DT
        clmt_hire_dt = clm_occr_dt - timedelta(days=np.random.randint(100, 3650))

        # Generate CLMT_JOB_TTL: Random job title
        clmt_job_ttl = fake.job()

        # Generate CLMT_JOB_TYP: Fulltime or Parttime
        clmt_job_typ = np.random.choice(['Fulltime', 'Parttime'])

        # Generate CLMT_DISAB_BGN_DT: On or right after CLM_OCCR_DT
        clmt_disab_bgn_dt = clm_occr_dt + timedelta(days=np.random.randint(0, 10))

        # Generate CLMT_AVG_WKLY_WAGE: Random wage between 500 and 8000
        clmt_avg_wkly_wage = round(np.random.uniform(500.00, 8000.00), 2)

        # Generate WORK_LOC: Type of work based on insured business
        work_loc = fake.catch_phrase()

        # Generate Industry: Randomly choose from predefined industries
        industry = np.random.choice(industries)

        # Append the record
        additional_details.append([
            clm_id, clmt_hire_dt, clmt_job_ttl, clmt_job_typ, clmt_disab_bgn_dt,
            clmt_avg_wkly_wage, work_loc, industry
        ])

    # Convert to DataFrame
    return pd.DataFrame(additional_details, columns=[
        'CLM_ID', 'CLMT_HIRE_DT', 'CLMT_JOB_TTL', 'CLMT_JOB_TYP', 'CLMT_DISAB_BGN_DT',
        'CLMT_AVG_WKLY_WAGE', 'WORK_LOC', 'INDUSTRY'
    ])

# Generate the CLAIM_ADDITIONAL_DETAILS dataset
claim_additional_details_df = generate_claim_additional_details(claim_details_df)

# Save the dataset to a CSV file
claim_additional_details_df.to_csv('data/CLAIM_ADDITIONAL_DETAILS.csv', index=False)

print("CLAIM_ADDITIONAL_DETAILS dataset generated and saved as 'data/CLAIM_ADDITIONAL_DETAILS.csv'.")
