import pandas as pd
import random
import faker
import os
from datetime import date, timedelta

# Initialize Faker
fake = faker.Faker()

# Parameters
num_customers = 9000  # Total number of customer records
num_claimant = 3000  # Number of claimants
num_insured = 3000  # Number of insured
num_medical_provider = 3000  # Number of medical providers

# Policy generation parameters
payment_statuses = ['Paid', 'Delinquent']
business_types = ['Construction', 'Retail', 'Healthcare', 'Technology', 'Manufacturing']
risk_levels = ['Low', 'Medium', 'High']

# State options for customer location and claim jurisdiction states
states = ['CA', 'VA', 'NY', 'TX', 'FL', 'WA', 'MA', 'NV', 'OH', 'MI', 'WV', 'NJ']

# List of industry names for business names
industries = [
    'Technology Solutions', 'Financial Services', 'Manufacturing Inc',
    'Retail Group', 'Healthcare Partners', 'Construction LLC', 'Consulting LLC',
    'Education Co', 'Entertainment Group', 'Logistics Solutions',
    'Energy Systems', 'Global Trade Inc', 'Transportation Co'
]

# List of medical provider names
medical_providers = [
    'Health First Medical Group', 'Wellness Solutions', 'Prime Health Network',
    'CarePoint Medical', 'Cura Medical Services', 'Alliance Medical',
    'Medix Healthcare', 'BlueShield Care', 'Patient First Medical',
    'UrgentWell Healthcare', 'FamilyCare Partners', 'American Medical Group',
    'PrimeCare Health'
]

# Mapping of BUSINESS_TYPE to potential business name prefixes
business_type_to_name_mapping = {
    'Construction': ['BuildCo', 'Solid Foundations', 'Construction Pros', 'BuildMaster', 'Pro Constructors', 'HardHat', 'Lennar Constructions'],
    'Retail': ['Retail Group', 'SuperShop', 'Market Masters', 'Retail World', 'ShopEase', 'Global Traders', 'Saks', 'Macys', 'Bloomingdales'],
    'Healthcare': ['Healthcare Partners', 'Prime Health Network', 'Wellness Solutions', 'Cura Health', 'Medical Assist', 'CareLine', 'All Health', 'Innova Health care'],
    'Technology': ['Tech Solutions', 'Innova Tech', 'NextGen Systems', 'SmartCode', 'CyberEdge', 'AI Vision Systems', 'Cloud Solutions', 'Our Book', 'Notebook Solutions'],
    'Manufacturing': ['MFG Solutions', 'Prime Manufacturing', 'MetalWorks', 'Precision Fabrication', 'IndusMFG', 'Master Builders', 'COFORGE']
}

# Business name suffixes to be added randomly
business_suffixes = ['LLC', 'Inc.', 'Group', 'Solutions', 'Corporation', 'Partners']

# Enhanced list of body parts
injury_body_parts = [
    'Head', 'Back', 'Arm', 'Leg', 'Shoulder', 'Hand', 'Foot',
    'Neck', 'Chest', 'Abdomen', 'Hip', 'Knee', 'Elbow', 'Ankle',
    'Wrist', 'Neck and Spine', 'Toes', 'Fingers', 'Teeth',
    'Ears', 'Eyes', 'Internal Organs', 'Pelvis', 'Groin'
]

# Enhanced list of injury types
injury_types = [
    'Fracture', 'Burn', 'Sprain', 'Cut', 'Bruise', 'Amputation',
    'Dislocation', 'Puncture', 'Contusion', 'Crush Injury', 'Tear',
    'Laceration', 'Concussion', 'Whiplash', 'Electric Shock',
    'Frostbite', 'Poisoning', 'Radiation Exposure', 'Chemical Exposure',
    'Nerve Damage', 'Soft Tissue Injury', 'Eye Injury', 'Hearing Loss'
]



# Function to clean phone number (keep only 10 digits)
def clean_phone_number(phone_number):
    """Remove non-digit characters and ensure it is exactly 10 digits."""
    cleaned_phone = ''.join(filter(str.isdigit, phone_number))
    return cleaned_phone[:10]  # Return only the first 10 digits


# Function to clean tax ID (keep only 9 digits)
def clean_tax_id(tax_id):
    """Remove non-digit characters and ensure it is exactly 9 digits."""
    cleaned_tax_id = ''.join(filter(str.isdigit, tax_id))
    return cleaned_tax_id[:9]  # Return only the first 9 digits

# Function to generate unique policy numbers
def generate_unique_policy_number(existing_numbers):
    while True:
        policy_number = f"COF{random.randint(1000000, 9999999)}"
        if policy_number not in existing_numbers:
            existing_numbers.add(policy_number)
            return policy_number

# Function to generate unique claim number
def generate_unique_claim_number(existing_claim_numbers, year):
    while True:
        claim_number = f"{year}{random.randint(100000, 999999)}"
        if claim_number not in existing_claim_numbers:
            existing_claim_numbers.add(claim_number)
            return claim_number


# Function to generate customer details

def generate_customer_details(num_customers):
    print(" Customer details generation started...")
    customer_data = []
    existing_tax_ids = set()  # To ensure tax IDs are unique
    existing_customer_profiles = set()  # To ensure no duplicate customer profiles

    for i in range(1, num_customers + 1):
        cust_id = i

        if i <= num_claimant:
            cust_type = 'Claimant'
        elif i <= num_claimant + num_insured:
            cust_type = 'Insured'
        else:
            cust_type = 'Medical Provider'

        while True:  # Ensure the uniqueness of customer details
            if cust_type == 'Claimant':
                first_name = fake.first_name()
                last_name = fake.last_name()
            elif cust_type == 'Insured':
                company_name_prefix = random.choice(
                    ['Retail Group', 'Tech Solutions', 'Solid Foundations', 'BuildCo', 'MFG Solutions']
                )
                suffix = random.choice(business_suffixes)
                first_name = f"{company_name_prefix} {suffix}"  # Generate full business name
                last_name = ''  # Businesses do not have last names
            elif cust_type == 'Medical Provider':
                company_name_prefix = random.choice(
                    ['Healthcare Partners', 'Prime Health Network', 'Wellness Solutions', 'Cura Medical Services']
                )
                suffix = random.choice(business_suffixes)
                first_name = f"{company_name_prefix} {suffix}"  # Generate full business name
                last_name = ''  # Businesses do not have last names

            # Gender is only applicable to 'Claimant' type
            if cust_type == 'Claimant':
                gender = random.choices(['Male', 'Female', 'Other'], weights=[49, 49, 2], k=1)[0]
            else:
                gender = None

            # Date of birth for person
            if cust_type == 'Claimant':
                dob = fake.date_of_birth(minimum_age=18, maximum_age=85)
                dod = (
                    fake.date_between(start_date=dob, end_date='today')
                    if dob.year < 1960 or (dob.year > 1988 and random.random() < 0.01)
                    else None
                )
            else:
                dob = None
                dod = None

            # Address details
            address = fake.street_address()
            city = fake.city()
            state = random.choices(states + [fake.state_abbr()], weights=[98] * len(states) + [2], k=1)[0]
            zip_code = fake.zipcode()

            # Contact details
            phone_number = clean_phone_number(fake.phone_number())
            email = f'{first_name.lower().replace(" ", "")}.{last_name.lower()}@{"gmail.com" if cust_type == "Claimant" else "company.com"}'

            # Generate a unique Tax ID (SSN or EIN) and ensure it's unique
            if cust_type == 'Claimant':
                tax_id = clean_tax_id(fake.ssn())
                tax_id_type = 'SSN'
            else:
                tax_id = clean_tax_id(fake.ein())
                tax_id_type = 'EIN'

            # Check for uniqueness of customer profile
            customer_profile_hash = (first_name, last_name, address, phone_number, email, tax_id)

            if tax_id not in existing_tax_ids and customer_profile_hash not in existing_customer_profiles:
                existing_tax_ids.add(tax_id)
                existing_customer_profiles.add(customer_profile_hash)
                break  # Customer details are unique, so exit the loop

        # Append the generated customer
        customer_data.append([
            cust_id, cust_type, first_name, last_name, gender, dob, dod,
            address, city, state, zip_code, phone_number, email, tax_id, tax_id_type
        ])

    # Create DataFrame
    customer_df = pd.DataFrame(customer_data, columns=[
        'CUST_ID', 'CUST_TYP', 'CUST_FRST_NM', 'CUST_LST_NM', 'CUST_GENDER', 'CUST_DOB',
        'CUST_DOD', 'CUST_ADDR', 'CUST_CITY', 'CUST_STATE', 'CUST_ZIP', 'CUST_PH_NO',
        'CUST_EMAIL', 'CUST_TAX_ID', 'CUST_TAX_ID_TYP'
    ])

    # Ensure proper data types for each column
    customer_df['CUST_ID'] = customer_df['CUST_ID'].astype(int)
    customer_df['CUST_TYP'] = customer_df['CUST_TYP'].astype(str)
    customer_df['CUST_FRST_NM'] = customer_df['CUST_FRST_NM'].astype(str)
    customer_df['CUST_LST_NM'] = customer_df['CUST_LST_NM'].astype(str)
    customer_df['CUST_GENDER'] = customer_df['CUST_GENDER'].astype('category')
    customer_df['CUST_DOB'] = pd.to_datetime(customer_df['CUST_DOB'], errors='coerce')
    customer_df['CUST_DOD'] = pd.to_datetime(customer_df['CUST_DOD'], errors='coerce')
    customer_df['CUST_ADDR'] = customer_df['CUST_ADDR'].astype(str)
    customer_df['CUST_CITY'] = customer_df['CUST_CITY'].astype(str)
    customer_df['CUST_STATE'] = customer_df['CUST_STATE'].astype(str)
    customer_df['CUST_ZIP'] = customer_df['CUST_ZIP'].astype(str)
    customer_df['CUST_PH_NO'] = customer_df['CUST_PH_NO'].astype(str)
    customer_df['CUST_EMAIL'] = customer_df['CUST_EMAIL'].astype(str)
    customer_df['CUST_TAX_ID'] = customer_df['CUST_TAX_ID'].astype(str)
    customer_df['CUST_TAX_ID_TYP'] = customer_df['CUST_TAX_ID_TYP'].astype(str)

    print(" Customer details generation completed.")
    return customer_df


# Function to generate policy details
def generate_policy_details(insured_customers, min_policies=5000):
    print("Policy details generation started...")
    policy_data = []
    policy_id = 1001  # Start PLCY_DTL_ID at 1001
    existing_policy_numbers = set()  # Track unique policy numbers

    total_policies = 0
    while total_policies < min_policies:  # Ensure at least 5000 policies
        for _, insured in insured_customers.iterrows():
            num_policies = random.randint(1, 3)  # Each insured can have 1 to 3 policies
            cust_id = insured['CUST_ID']

            # Generate non-overlapping policies
            start_date = fake.date_between(start_date=date(2006, 1, 1), end_date=date(2023, 12, 31))
            for _ in range(num_policies):
                if total_policies >= min_policies:
                    break  # Stop once we reach the minimum required policies

                # Generate unique policy number
                policy_number = generate_unique_policy_number(existing_policy_numbers)
                policy_start_date = start_date
                policy_end_date = policy_start_date + timedelta(days=365)  # End date is exactly 1 year later

                # Generate other policy details
                premium_amount = round(random.uniform(500, 5000), 2)  # Premium between $500 and $5000
                payment_status = random.choices(['Paid', 'Delinquent'], weights=[95, 5], k=1)[
                    0]  # 95% Paid, 5% Delinquent
                claim_limit = round(random.uniform(5000, 100000), 2)  # Claim limit between $5000 and $100000
                risk_level = random.choices(risk_levels, weights=[50, 35, 15], k=1)[0]  # Low is most common

                # Append the policy record
                policy_data.append([
                    policy_id, cust_id, policy_number, policy_start_date, policy_end_date,
                    premium_amount, payment_status, claim_limit, risk_level
                ])

                # Increment IDs and update start_date to prevent overlap
                policy_id += 1
                start_date = policy_end_date + timedelta(days=1)  # Next policy starts the day after previous ends
                total_policies += 1

    # Convert to DataFrame
    policy_df = pd.DataFrame(policy_data, columns=[
        'PLCY_DTL_ID', 'CUST_ID', 'PLCY_NO', 'PLCY_STRT_DT', 'PLCY_END_DT',
        'PLCY_PREMIUM_AMT', 'PLCY_PAYMENT_STATUS', 'PLCY_CLAIM_LIMIT', 'RISK_LEVEL'
    ])

    print(f"Policy details generation completed. Total policies generated: {len(policy_df)}")
    return policy_df


def generate_claim_details(policy_df, customer_df, min_claims=15000, fraud_percentage=0.05):

    print("Claim details generation started...")
    claim_data = []
    claim_id = 11001  # Start CLM_DTL_ID at 11001
    existing_claim_numbers = set()  # Track unique claim numbers

    insured_customers = customer_df[customer_df['CUST_TYP'] == 'Insured']
    claimant_customers = customer_df[customer_df['CUST_TYP'] == 'Claimant']
    medical_providers = customer_df[customer_df['CUST_TYP'] == 'Medical Provider']

    # Fraud claim control
    total_fraud_claims = int(min_claims * fraud_percentage)  # 15% of claims are fraudulent
    fraud_claims_count = 0

    for _ in range(min_claims):
        policy = policy_df.sample(1).iloc[0]
        insured_customer = insured_customers.sample(1).iloc[0]
        claimant_customer = claimant_customers.sample(1).iloc[0]
        medical_provider = medical_providers.sample(1).iloc[0]

        policy_start_date = pd.to_datetime(policy['PLCY_STRT_DT']).date()
        policy_end_date = pd.to_datetime(policy['PLCY_END_DT']).date()

        # Determine claim occurrence date
        claim_type = random.choices(['regular', 'near_end'], weights=[0.98, 0.02], k=1)[0]

        if claim_type == 'regular':
            # Claims occur randomly in the policy period, excluding the first 30 days and last 30 days
            min_claim_date = policy_start_date + timedelta(days=30)
            max_claim_date = policy_end_date - timedelta(days=30)
            clm_occur_date = fake.date_between(start_date=min_claim_date, end_date=max_claim_date)
        else:
            # Claims occur in the last 30 days of the policy (2% chance)
            clm_occur_date = fake.date_between(start_date=policy_end_date - timedelta(days=30),
                                               end_date=policy_end_date)

        # Generate report date ranging from 4 to 40 days after the occurrence date
        days_offset = random.choices(range(4, 41), weights=[1 if i > 30 else 19 for i in range(4, 41)], k=1)[0]
        clm_report_date = clm_occur_date + timedelta(days=days_offset)

        # Generate claim amount with realistic patterns
        if fraud_claims_count < total_fraud_claims:
            # Fraudulent claims tend to have higher amounts close to the claim limit
            clm_amount = round(random.uniform(0.9 * policy['PLCY_CLAIM_LIMIT'], policy['PLCY_CLAIM_LIMIT']), 2)
        else:
            # Non-fraudulent claims use a triangular distribution (more claims between $500 and $5000)
            clm_amount = round(random.triangular(10, 5000, 10000), 2)

        # Ensure claim amount does not exceed policy claim limit
        clm_amount = min(clm_amount, policy['PLCY_CLAIM_LIMIT'])

        # Generate occurrence address details
        clm_occr_address = fake.street_address()
        clm_occr_city = fake.city()
        clm_occr_zip = fake.zipcode()

        # Fraud Indicator and Logic
        clm_fraud_ind = 0
        fraud_reasons = []

        if fraud_claims_count < total_fraud_claims:
            # Fraud Detection Rules
            if clm_occur_date > policy_end_date:
                clm_fraud_ind = 1
                fraud_reasons.append('Claim After Policy Expiry')

            if (policy_end_date - clm_occur_date).days < 7:
                clm_fraud_ind = 1
                fraud_reasons.append('Claim Near Policy Expiry')

            if clm_amount > 0.9 * policy['PLCY_CLAIM_LIMIT']:
                clm_fraud_ind = 1
                fraud_reasons.append('High Claim Amount Near Policy Limit')

            if random.random() < 0.15:  # Add mismatched state logic to some frauds
                clm_occr_state = random.choice(
                    [state for state in customer_df['CUST_STATE'].unique() if state != insured_customer['CUST_STATE']])
                clm_fraud_ind = 1
                fraud_reasons.append('Mismatched Insured, Claimant, or Provider State')
            else:
                clm_occr_state = insured_customer['CUST_STATE']

            if clm_fraud_ind == 1:
                fraud_claims_count += 1
        else:
            # Non-fraudulent claims logic
            clm_occr_state = insured_customer['CUST_STATE']

        if not fraud_reasons:
            fraud_reasons.append('None')

        fraud_reason_str = ', '.join(fraud_reasons)

        # Generate unique claim number
        while True:
            claim_number = f"{clm_occur_date.year}{random.randint(100000, 999999)}"
            if claim_number not in existing_claim_numbers:
                existing_claim_numbers.add(claim_number)
                break

        # Append claim record
        claim_data.append([
            claim_id,
            claim_number,
            clm_report_date,
            clm_occur_date,
            clm_amount,
            policy['PLCY_NO'],
            insured_customer['CUST_ID'],
            claimant_customer['CUST_ID'],
            medical_provider['CUST_ID'],
            clm_occr_address,
            clm_occr_city,
            clm_occr_zip,
            clm_occr_state,
            clm_fraud_ind,
            fraud_reason_str
        ])
        claim_id += 1

    claim_df = pd.DataFrame(claim_data, columns=[
        'CLM_DTL_ID', 'CLM_NO', 'CLM_RPT_DT', 'CLM_OCCR_DT', 'CLM_AMT',
        'PLCY_NO', 'CUST_ID_INSURED', 'CUST_ID_CLAIMANT', 'CUST_ID_MED_PROV',
        'CLM_OCCR_ADDR', 'CLM_OCCR_CITY', 'CLM_OCCR_ZIP', 'CLM_OCCR_STATE',
        'CLM_FRAUD_IND', 'FRAUD_REASON'
    ])

    print(
        f"Total Claims: {len(claim_df)} | Fraudulent Claims: {claim_df['CLM_FRAUD_IND'].sum()} (Target: {total_fraud_claims})")
    return claim_df


def generate_claim_additional_details(claim_df):
    print(" Generating Claim Additional Details...")
    additional_details = []
    job_titles = ['Software Engineer', 'Construction Worker', 'Retail Associate', 'Nurse', 'Driver', 'Teacher']
    work_environments = ['On-site', 'Remote', 'Hybrid']
    employment_statuses = ['Active', 'Terminated', 'On Leave']

    for _, claim in claim_df.iterrows():
        clm_dtl_id = claim['CLM_DTL_ID']
        clm_occur_date = pd.to_datetime(claim['CLM_OCCR_DT']).date()
        fraud_flag = claim['CLM_FRAUD_IND']

        # Default data
        clmt_hire_date = fake.date_between(start_date=date(2000, 1, 1), end_date=clm_occur_date - timedelta(days=30))
        clmt_disab_bgn_date = clm_occur_date + timedelta(days=random.randint(1, 30))
        clmt_avg_weekly_wage = round(random.uniform(500, 8000), 2)
        job_title = random.choice(job_titles)
        work_environment = random.choice(work_environments)
        job_desc = f"{job_title} responsible for various operational and administrative tasks."

        # Fraud-specific logic
        fraud_reasons = []
        if fraud_flag == 1:
            if random.random() < 0.3:
                # Fraud: Hire date is AFTER occurrence date
                clmt_hire_date = clm_occur_date + timedelta(days=random.randint(1, 30))
                fraud_reasons.append('Hire Date After Claim Occurrence')

            if random.random() < 0.3:
                # Fraud: Disability Begin Date far before occurrence date
                clmt_disab_bgn_date = clm_occur_date - timedelta(days=random.randint(90, 180))
                fraud_reasons.append('Disability Date Before Occurrence')

            if random.random() < 0.2:
                # Fraud: Unusual weekly wage (extremely high)
                clmt_avg_weekly_wage = round(random.uniform(10000, 20000), 2)
                fraud_reasons.append('Unusual Weekly Wage')

            if random.random() < 0.2:
                # Fraud: Terminated but claiming wages
                employment_status = 'Terminated'
                fraud_reasons.append('Terminated Employee Claiming Wages')
            else:
                employment_status = random.choice(employment_statuses)
        else:
            # For Non-Fraud Claims: Keep most employment statuses "Active"
            if random.random() < 0.9:
                employment_status = 'Active'
            else:
                employment_status = 'On Leave'

        additional_details.append([
            clm_dtl_id, clmt_hire_date, job_title, 'Full-time' if random.random() < 0.8 else 'Part-time',
            clmt_disab_bgn_date, clmt_avg_weekly_wage, job_desc, work_environment, employment_status, ', '.join(fraud_reasons)
        ])

    additional_details_df = pd.DataFrame(additional_details, columns=[
        'CLM_DTL_ID', 'CLMT_HIRE_DT', 'CLMT_JOB_TITLE', 'CLMT_JOB_TYP',
        'CLMT_DISAB_BGN_DT', 'CLMT_AVG_WKLY_WAGE', 'JOB_DESC',
        'WORK_ENVIRONMENT', 'EMPLOYMENT_STATUS', 'FRAUD_REASON_ADDITIONAL'
    ])
    print(" Claim Additional Details generated.")
    return additional_details_df

def generate_injury_details(claim_df, customer_df):
    print(" Generating Injury Details...")
    injury_data = []
    injury_id = 111001  # Start injury ID from INJ111001
    injury_severities = ['Low', 'Medium', 'High']
    fraud_notes = ['suspected exaggeration', 'requires further investigation', 'inconsistent patient history']

    # Create a map of CUST_ID to CUST_FRST_NM for Medical Providers
    med_provider_map = customer_df.set_index('CUST_ID')['CUST_FRST_NM']

    # Define desk-job roles that are unlikely to have high-risk injuries
    desk_job_roles = ['Software Engineer', 'Data Analyst', 'Office Manager', 'Accountant']
    high_risk_injuries = ['Burn', 'Fracture', 'Sprain']

    # Iterate over claims to generate injuries
    for index, claim in claim_df.iterrows():
        clm_dtl_id = claim['CLM_DTL_ID']
        clm_fraud_ind = claim['CLM_FRAUD_IND']
        claimant_job_title = claim.get('CLMT_JOB_TTL', 'Unknown')
        claimant_work_env = claim.get('WORK_ENVIRONMENT', 'Unknown')

        # Retrieve medical provider name using CUST_ID_MED_PROV
        medical_provider_id = claim['CUST_ID_MED_PROV']
        medical_provider = med_provider_map.get(medical_provider_id, 'Unknown Medical Provider')

        num_injuries = random.randint(1, 3)  # Each claim can have 1 to 3 injuries
        injury_fraud_reasons = []  # Track fraud reasons for injuries

        for _ in range(num_injuries):
            injury_pob = random.choice(injury_body_parts)
            injury_severity = random.choice(injury_severities)
            injury_type = random.choice(injury_types)
            treatment_required = 'Yes' if injury_severity in ['Medium', 'High'] else 'No'
            days_lost = random.randint(0, 30) if treatment_required == 'No' else random.randint(5, 180)
            prescriber_notes = f"{injury_severity} severity injury. Recovery expected within {days_lost} days."

            # Fraud-specific logic
            if clm_fraud_ind == 1:
                if random.random() < 0.3:
                    # Fraud: High severity but no treatment required
                    if injury_severity == 'High' and treatment_required == 'No':
                        injury_fraud_reasons.append('High severity injury without treatment')

                if random.random() < 0.2:
                    # Fraud: Exaggerated workdays lost
                    days_lost = random.randint(181, 365)
                    injury_fraud_reasons.append('Exaggerated workdays lost')

                if random.random() < 0.2:
                    # Fraud: Inconsistent injuries
                    injury_type = random.choice(injury_types)
                    injury_fraud_reasons.append(f'Inconsistent injury type for {injury_pob}')

                if random.random() < 0.3:
                    # Fraud: Suspicious prescriber notes
                    prescriber_notes = random.choice(fraud_notes)
                    injury_fraud_reasons.append('Suspicious prescriber notes')

                # New Fraud: Occupation-injury mismatch
                if (claimant_job_title in desk_job_roles) and (injury_type in high_risk_injuries):
                    injury_fraud_reasons.append('Illogical Occupation-Injury Pair')

            # Append the generated injury record
            injury_data.append([
                f"INJ{injury_id}", clm_dtl_id, injury_pob, injury_severity,
                injury_type, treatment_required, days_lost
            ])
            injury_id += 1

        # Append injury fraud reasons to claim's FRAUD_REASON
        if injury_fraud_reasons:
            updated_fraud_reason = claim['FRAUD_REASON'] if pd.notnull(claim['FRAUD_REASON']) else ''
            updated_fraud_reason += ', ' + ', '.join(injury_fraud_reasons)
            claim_df.at[index, 'FRAUD_REASON'] = updated_fraud_reason.strip(', ')

    # Create Injury Details DataFrame
    injury_df = pd.DataFrame(injury_data, columns=[
        'CLM_INJ_ID', 'CLM_DTL_ID', 'INJURY_BODY_PART', 'INJURY_SEVERITY',
        'INJURY_TYPE', 'TREATMENT_REQUIRED',
        'DAYS_LOST'
    ])
    print(f" Injury Details generated: {len(injury_df)} injuries.")
    return injury_df, claim_df


def generate_claim_status(claim_df):
    print("Generating Claim Status Details...")
    status_data = []
    claim_status_id_start = 11100000  # Start claim status ID

    for _, claim in claim_df.iterrows():
        clm_dtl_id = claim['CLM_DTL_ID']
        clm_rpt_dt = pd.to_datetime(claim['CLM_RPT_DT']).date()
        clm_fraud_ind = claim['CLM_FRAUD_IND']
        fraud_reason = claim['FRAUD_REASON']

        # Initialize defaults
        clm_sts_cd = 'Approved'
        status_reason = 'Claim approved within policy terms'
        clm_sts_dt = clm_rpt_dt + timedelta(days=random.randint(1, 7))  # Approved within a week

        if clm_fraud_ind == 1:
            # Fraudulent claim statuses
            if random.random() < 0.10:  # 10% of fraud claims declined
                clm_sts_cd = 'Declined'
                status_reason = f'Claim declined due to fraud: {fraud_reason}'
                clm_sts_dt = clm_rpt_dt + timedelta(days=random.randint(1, 7))  # Declined within a week
            elif random.random() < 0.05:  # 5% of fraud claims pending
                clm_sts_cd = 'Pending'
                status_reason = 'Claim under review for suspected fraud'
                clm_sts_dt = clm_rpt_dt + timedelta(weeks=random.randint(1, 15))  # Pending up to 15 weeks
        else:
            # Non-fraud claims
            if random.random() < 0.25:  # 25% of non-fraud claims pending
                clm_sts_cd = 'Pending'
                status_reason = 'Claim under review for additional information'
                clm_sts_dt = clm_rpt_dt + timedelta(weeks=random.randint(1, 15))  # Pending up to 15 weeks

        # Generate unique Claim Status ID
        clm_sts_id = claim_status_id_start + random.randint(10000, 99999)

        # Append status record
        status_data.append([
            clm_dtl_id, clm_sts_id, clm_sts_cd, clm_sts_dt, status_reason
        ])

    status_df = pd.DataFrame(status_data, columns=[
        'CLM_DTL_ID', 'CLM_STS_ID', 'CLM_STS_CD', 'CLM_STS_DT', 'STATUS_REASON'
    ])
    print(f"Claim Status Details generated: {len(status_df)} statuses.")
    return status_df


def merge_claimant_details(claim_df, customer_df):
    """
    Merges claimant details from customer_df into claim_df.
    """
    print(" Merging Claimant Customer Details...")

    # Step 1: Ensure the keys are integers
    claim_df['CUST_ID_CLAIMANT'] = claim_df['CUST_ID_CLAIMANT'].astype(int)
    customer_df['CUST_ID'] = customer_df['CUST_ID'].astype(int)

    # Step 2: Merge claim_df with customer_df using CUST_ID_CLAIMANT and CUST_ID
    unified_claims_df = pd.merge(
        claim_df,
        customer_df,
        left_on='CUST_ID_CLAIMANT',
        right_on='CUST_ID',
        how='left',
        suffixes=('', '_CLAIMANT')
    )

    # Step 3: Rename claimant columns
    claimant_columns_rename = {
        'CUST_FRST_NM': 'CLAIMANT_FRST_NM',
        'CUST_LST_NM': 'CLAIMANT_LST_NM',
        'CUST_DOB': 'CLAIMANT_DOB',
        'CUST_DOD': 'CLAIMANT_DOD'
    }
    unified_claims_df.rename(columns=claimant_columns_rename, inplace=True)

    # Step 4: Convert data types for claimant fields
    unified_claims_df['CLAIMANT_LST_NM'] = unified_claims_df['CLAIMANT_LST_NM'].astype(str)
    unified_claims_df['CLAIMANT_LST_NM'].replace('nan', pd.NA, inplace=True)

    unified_claims_df['CLAIMANT_DOB'] = pd.to_datetime(unified_claims_df['CLAIMANT_DOB'], errors='coerce')
    unified_claims_df['CLAIMANT_DOD'] = pd.to_datetime(unified_claims_df['CLAIMANT_DOD'], errors='coerce')

    print(" Merge completed successfully.")
    return unified_claims_df

# Function to save CSV files
def save_csv(dataframe, filename):
    """Save a DataFrame as a CSV file in the 'data/' directory."""
    filepath = os.path.join(os.getcwd(), 'data', filename)
    dataframe.to_csv(filepath, index=False)
    print(f"CSV saved: {filepath}")

def generate_all_csvs():
    print("Generating Customer Details...")
    customer_df = generate_customer_details(num_customers)
    save_csv(customer_df, 'Customer_Details.csv')

    print("Generating Policy Details...")
    insured_customers = customer_df[customer_df['CUST_TYP'] == 'Insured']
    policy_df = generate_policy_details(insured_customers)
    save_csv(policy_df, 'Policy_Details.csv')

    print("Generating Claim Details...")
    claim_df = generate_claim_details(policy_df, customer_df, min_claims=15000)
    save_csv(claim_df, 'Claim_Details.csv')

    print("Generating Claim Additional Details...")
    additional_details_df = generate_claim_additional_details(claim_df)
    save_csv(additional_details_df, 'Claim_Additional_Details.csv')

    print("Generating Injury Details...")
    injury_df, updated_claim_df = generate_injury_details(claim_df, customer_df)
    save_csv(injury_df, 'Injury_Details.csv')
    save_csv(updated_claim_df, 'Updated_Claim_Details.csv')

    print("Generating Claim Status Details...")
    status_df = generate_claim_status(claim_df)
    save_csv(status_df, 'Claim_Status_Details.csv')

    print("Merging All Data...")

    #  Step 1: Merge Claim Details with Policy Details
    print("Merging Claim Details with Policy Details...")
    unified_df = pd.merge(
        claim_df,
        policy_df,
        on='PLCY_NO',
        how='left'
    )

    print("Merging Insured Customer Details...")
    #  Step 2: Merge Insured Customer Details with Prefix
    unified_df = pd.merge(
        unified_df,
        customer_df.add_prefix('INSURED_'),
        left_on='CUST_ID_INSURED',
        right_on='INSURED_CUST_ID',
        how='left'
    )
    print(f"After merging insured customer details, shape: {unified_df.shape}")
    print(unified_df.columns)  # Debug: Print columns

    print("Merging Claimant Customer Details...")
    #  Step 3: Merge Claimant Customer Details with Prefix
    unified_df = pd.merge(
        unified_df,
        customer_df.add_prefix('CLAIMANT_'),
        left_on='CUST_ID_CLAIMANT',
        right_on='CLAIMANT_CUST_ID',
        how='left'
    )
    print(f"After merging claimant customer details, shape: {unified_df.shape}")
    print(unified_df.columns)  # Debug: Print columns

    print("Merging Medical Provider Customer Details...")
    #  Step 4: Merge Medical Provider Customer Details with Prefix
    unified_df = pd.merge(
        unified_df,
        customer_df.add_prefix('MEDPROV_'),
        left_on='CUST_ID_MED_PROV',
        right_on='MEDPROV_CUST_ID',
        how='left'
    )
    print(f"After merging medical provider customer details, shape: {unified_df.shape}")
    print(unified_df.columns)  # Debug: Print columns

    print("Merging Additional Claim Details...")
    #  Step 5: Merge Claim Additional Details
    unified_df = pd.merge(
        unified_df,
        additional_details_df,
        on='CLM_DTL_ID',
        how='left'
    )
    print(f"After merging additional claim details, shape: {unified_df.shape}")

    print("Merging Injury Details...")
    #  Step 6: Merge Injury Details
    unified_df = pd.merge(
        unified_df,
        injury_df,
        on='CLM_DTL_ID',
        how='left'
    )
    print(f"After merging injury details, shape: {unified_df.shape}")

    print("Merging Claim Status Details...")
    #  Step 7: Merge Claim Status Details
    unified_df = pd.merge(
        unified_df,
        status_df,
        on='CLM_DTL_ID',
        how='left'
    )
    print(f"After merging claim status details, shape: {unified_df.shape}")

    # Drop unnecessary columns
    unified_df.drop(columns=[ 'MEDPROV_CUST_DOD', 'MEDPROV_CUST_DOB', 'MEDPROV_CUST_GENDER', 'MEDPROV_CUST_LST_NM', 'INSURED_CUST_DOD'
                              , 'INSURED_CUST_DOB', 'INSURED_CUST_GENDER', 'INSURED_CUST_LST_NM', 'CUST_ID', 'INSURED_CUST_TYP'
                              , 'INSURED_CUST_TAX_ID_TYP', 'CLAIMANT_CUST_TYP', 'CLAIMANT_CUST_TAX_ID_TYP'
                              , 'MEDPROV_CUST_ID', 'MEDPROV_CUST_TAX_ID_TYP', 'INSURED_CUST_CITY', 'INSURED_CUST_ZIP'
                              , 'CLAIMANT_CUST_ZIP', 'MEDPROV_CUST_TYP', 'MEDPROV_CUST_ADDR', 'MEDPROV_CUST_CITY', 'MEDPROV_CUST_ZIP'
                              , 'MEDPROV_CUST_EMAIL', 'MEDPROV_CUST_PH_NO', 'MEDPROV_CUST_TAX_ID', 'INSURED_CUST_PH_NO', 'INSURED_CUST_EMAIL'
                              , 'INSURED_CUST_TAX_ID', 'CLAIMANT_CUST_ADDR', 'CLAIMANT_CUST_CITY', 'CLAIMANT_CUST_PH_NO', 'CLAIMANT_CUST_EMAIL'
                              , 'CLM_FRAUD_IND', 'FRAUD_REASON',  'PLCY_DTL_ID', 'INSURED_CUST_ID', 'CLM_STS_ID', 'STATUS_REASON'
                              , 'CLM_INJ_ID', 'FRAUD_REASON_ADDITIONAL', 'CLAIMANT_CUST_ID'
    ], inplace=True, errors='ignore')

    print("Saving Unified CSV...")
    unified_csv_filename = 'Unified_Customer_Policy_Claim_Details.csv'
    save_csv(unified_df, unified_csv_filename)
    print(f"Unified CSV saved: {unified_csv_filename}")

if __name__ == "__main__":
    try:
        generate_all_csvs()
    except Exception as e:
        print(f" An error occurred: {e}")
