import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Load CLAIM_DETAILS dataset
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')


# Function to generate CLAIM_INJURY_DETAILS dataset
def generate_claim_injury_details(claim_details):
    injury_details = []
    injury_id_start = 50001  # Starting ID for CLM_INJ_ID

    injury_parts = ['Head', 'Back', 'Arm', 'Leg', 'Shoulder', 'Knee', 'Foot', 'Brain', 'Hip']
    injury_severity = ['High', 'Medium', 'Low']
    injury_types = ['Fracture', 'Sprain', 'Burn', 'Cut', 'Bruise', 'Amputation', 'Concussion', 'Dislocation',
                    'Infection', 'Severance', 'COVID-19']

    # Select 30% of claims to have "fraud-like characteristics"
    fraud_like_claim_ids = np.random.choice(claim_details['CLM_DTL_ID'], size=int(0.3 * len(claim_details)),
                                            replace=False)

    for _, claim_row in claim_details.iterrows():
        clm_id = claim_row['CLM_DTL_ID']
        is_fraud_like_claim = clm_id in fraud_like_claim_ids

        # Determine the number of injuries for the claim (1 to 3)
        num_injuries = np.random.randint(1, 4) if is_fraud_like_claim else 1

        for _ in range(num_injuries):
            clm_inj_id = injury_id_start
            injury_id_start += 1

            injury_pob = np.random.choice(injury_parts)
            injury_severity_level = np.random.choice(injury_severity)

            # Fraud Pattern: Rare injury type for labor-intensive jobs
            injury_type = np.random.choice(injury_types)
            if is_fraud_like_claim and np.random.rand() < 0.2:
                injury_type = np.random.choice(['COVID-19', 'Brain Injury', 'Infection'])

            prescriber_notes = fake.text(
                max_nb_chars=200) if not is_fraud_like_claim else f"Note: {fake.catch_phrase()}"

            # Fraud Pattern: Injury Location does not match Injury Type
            if is_fraud_like_claim and injury_pob == 'Foot' and injury_type in ['Concussion', 'Brain Injury']:
                injury_type = 'Sprain'

            # Additional Details
            treatment_required = 'Yes' if injury_severity_level in ['High', 'Medium'] else 'No'
            days_lost = np.random.randint(1, 120) if treatment_required == 'Yes' else 0
            doctor_name = fake.name()
            medical_provider = fake.company()

            injury_details.append([
                clm_inj_id, clm_id, injury_pob, injury_severity_level,
                injury_type, prescriber_notes, treatment_required, days_lost,
                doctor_name, medical_provider
            ])

    # Convert to DataFrame
    return pd.DataFrame(injury_details, columns=[
        'CLM_INJ_ID', 'CLM_DTL_ID', 'INJURY_POB', 'INJURY_SEVERITY',
        'INJURY_TYP_CD', 'PRESCRIBER_NOTES', 'TREATMENT_REQUIRED',
        'DAYS_LOST', 'DOCTOR_NAME', 'MEDICAL_PROVIDER'
    ])


# Generate the dataset
claim_injury_details_df = generate_claim_injury_details(claim_details_df)

# Save the dataset to a CSV file
claim_injury_details_df.to_csv('data/CLAIM_INJURY_DETAILS.csv', index=False)

print("CLAIM_INJURY_DETAILS dataset generated and saved as 'data/CLAIM_INJURY_DETAILS.csv'.")
