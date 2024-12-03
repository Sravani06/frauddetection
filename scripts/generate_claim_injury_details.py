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

    # Possible values for INJURY_POB and INJURY_SEVERITY
    injury_parts = ['Head', 'Back', 'Arm', 'Leg', 'Shoulder', 'Knee', 'Foot', 'Brain', 'Hip']
    injury_severity = ['High', 'Medium', 'Low']
    injury_types = ['Fracture', 'Sprain', 'Burn', 'Cut', 'Bruise','Amputation', 'Concussion', 'Dislocation', 'Infection', 'Severance', 'COVID-19']

    for _, claim_row in claim_details.iterrows():
        clm_id = claim_row['CLM_DTL_ID']

        # Determine the number of injuries for the claim (1 to 3)
        num_injuries = np.random.randint(1, 4)

        for _ in range(num_injuries):
            # Generate injury details
            clm_inj_id = injury_id_start
            injury_id_start += 1

            injury_pob = np.random.choice(injury_parts)
            injury_severity_level = np.random.choice(injury_severity)
            injury_type = np.random.choice(injury_types)

            prescriber_notes = fake.text(max_nb_chars=200)

            # Append the record to the list
            injury_details.append([
                clm_inj_id, clm_id, injury_pob, injury_severity_level,
                injury_type, prescriber_notes
            ])

    # Convert to DataFrame
    return pd.DataFrame(injury_details, columns=[
        'CLM_INJ_ID', 'CLM_ID', 'INJURY_POB', 'INJURY_SEVERITY',
        'INJURY_TYP_CD', 'PRESCRIBER_NOTES'
    ])

# Generate the dataset
claim_injury_details_df = generate_claim_injury_details(claim_details_df)

# Save the dataset to a CSV file
claim_injury_details_df.to_csv('data/CLAIM_INJURY_DETAILS.csv', index=False)

print("CLAIM_INJURY_DETAILS dataset generated and saved as 'data/CLAIM_INJURY_DETAILS.csv'.")
