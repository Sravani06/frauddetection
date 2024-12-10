import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Function to generate CLAIM_ADDITIONAL_DETAILS dataset
def generate_claim_additional_details(claim_details_df):
    additional_details = []
    job_titles = ['Cashier', 'Warehouse Worker', 'Office Clerk', 'Security Guard', 'Mechanic', 'Sales Associate', 'Software Engineer', 'Nurse']
    industries = ['Retail', 'Manufacturing', 'Healthcare', 'Technology', 'Finance', 'Construction', 'Transportation', 'Hospitality']
    work_environments = ['On-site', 'Remote', 'Hybrid']
    reporting_channels = ['Web', 'Phone', 'Email']

    # Select 30% of claims to have "fraud-like characteristics"
    fraud_like_claim_ids = np.random.choice(claim_details_df['CLM_DTL_ID'], size=int(0.3 * len(claim_details_df)), replace=False)

    for _, row in claim_details_df.iterrows():
        clm_dtl_id = row['CLM_DTL_ID']
        clm_occr_dt = datetime.strptime(row['CLM_OCCR_DT'], '%Y-%m-%d')
        is_fraud_like_claim = clm_dtl_id in fraud_like_claim_ids

        # 1. CLMT_HIRE_DT (Hire Date)
        if is_fraud_like_claim and np.random.rand() < 0.5:
            clmt_hire_dt = clm_occr_dt + timedelta(days=np.random.randint(1, 30))  # Fraud pattern
        else:
            clmt_hire_dt = clm_occr_dt - timedelta(days=np.random.randint(30, 365))  # Normal case

        # 2. CLMT_JOB_TTL (Job Title)
        clmt_job_ttl = np.random.choice(job_titles)

        # 3. CLMT_JOB_TYP (Job Type)
        clmt_job_typ = np.random.choice(['Part-time', 'Full-time']) if is_fraud_like_claim else 'Full-time'

        # 4. CLMT_DISAB_BGN_DT (Disability Start Date)
        clmt_disab_bgn_dt = clm_occr_dt + timedelta(days=np.random.randint(7, 30)) if is_fraud_like_claim else clm_occr_dt + timedelta(days=1)

        # 5. CLMT_AVG_WKLY_WAGE (Average Weekly Wage)
        clmt_avg_wkly_wage = round(np.random.uniform(500, 8000), 2)

        # 6. WORK_LOC (Work Location)
        work_loc = fake.city() if is_fraud_like_claim else row['CLM_OCCR_CITY']

        # 7. INDUSTRY (Industry)
        industry = np.random.choice(industries) if is_fraud_like_claim else 'Healthcare' if clmt_job_ttl == 'Nurse' else np.random.choice(industries)

        # 8. JOB_DESC (Job Description)
        job_desc = f"{clmt_job_ttl} responsible for various operational tasks."

        # 9. WORK_ENVIRONMENT (Work Environment)
        work_environment = np.random.choice(work_environments) if is_fraud_like_claim else 'On-site'

        # 10. SUPERVISOR_NAME (Supervisor Name)
        supervisor_name = fake.name()

        # 11. REPORTING_CHANNEL (Reporting Channel)
        reporting_channel = np.random.choice(reporting_channels)

        # 12. EMPLOYMENT_STATUS (Employment Status)
        employment_status = 'Terminated' if is_fraud_like_claim and np.random.rand() < 0.2 else 'Active'

        # Append the record
        additional_details.append([
            clm_dtl_id, clmt_hire_dt.strftime('%Y-%m-%d'), clmt_job_ttl, clmt_job_typ,
            clmt_disab_bgn_dt.strftime('%Y-%m-%d'), clmt_avg_wkly_wage, work_loc, industry,
            job_desc, work_environment, supervisor_name, reporting_channel, employment_status
        ])

    return pd.DataFrame(additional_details, columns=[
        'CLM_DTL_ID', 'CLMT_HIRE_DT', 'CLMT_JOB_TTL', 'CLMT_JOB_TYP',
        'CLMT_DISAB_BGN_DT', 'CLMT_AVG_WKLY_WAGE', 'WORK_LOC', 'INDUSTRY',
        'JOB_DESC', 'WORK_ENVIRONMENT', 'SUPERVISOR_NAME', 'REPORTING_CHANNEL', 'EMPLOYMENT_STATUS'
    ])

# Load CLAIM_DETAILS dataset
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')

# Generate CLAIM_ADDITIONAL_DETAILS dataset
additional_details_df = generate_claim_additional_details(claim_details_df)

# Save the dataset to a CSV file
additional_details_df.to_csv('data/CLAIM_ADDITIONAL_DETAILS.csv', index=False)

print("CLAIM_ADDITIONAL_DETAILS dataset generated and saved as 'data/CLAIM_ADDITIONAL_DETAILS.csv'.")
