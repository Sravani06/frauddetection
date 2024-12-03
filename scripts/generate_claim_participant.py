import pandas as pd

# Load CLAIM_DETAILS and CUSTOMER_DETAILS datasets
claim_details_df = pd.read_csv('data/CLAIM_DETAILS.csv')
customer_details_df = pd.read_csv('data/CUSTOMER_DETAILS.csv')

# Function to generate CLAIM_PARTICIPANT dataset
def generate_claim_participants(claim_details, customer_details):
    claim_participants = []
    participant_id_start = 30001

    # Iterate over each claim in CLAIM_DETAILS
    for _, claim_row in claim_details.iterrows():
        clm_id = claim_row['CLM_DTL_ID']

        # Select random customers
        claimant = customer_details[customer_details['CUST_TYP'] == 'prsn'].sample(1).iloc[0]
        insured = customer_details[customer_details['CUST_TYP'] == 'busn'].sample(1).iloc[0]
        provider = customer_details[customer_details['CUST_TYP'] == 'busn'].sample(1).iloc[0]

        # Add Claimant Participant
        claim_participants.append([
            participant_id_start,
            clm_id,
            claimant['CUST_ID'],
            claimant['CUST_TYP'],
            'clmt'
        ])
        participant_id_start += 1

        # Add Insured Participant
        claim_participants.append([
            participant_id_start,
            clm_id,
            insured['CUST_ID'],
            insured['CUST_TYP'],
            'Insured'
        ])
        participant_id_start += 1

        # Add Provider Participant
        claim_participants.append([
            participant_id_start,
            clm_id,
            provider['CUST_ID'],
            provider['CUST_TYP'],
            'Provider'
        ])
        participant_id_start += 1

    # Convert to DataFrame
    return pd.DataFrame(claim_participants, columns=[
        'CLM_PTCP_ID', 'CLM_ID', 'CUST_ID', 'CUST_TYP', 'PTCP_TYP'
    ])

# Generate the CLAIM_PARTICIPANT dataset
claim_participant_df = generate_claim_participants(claim_details_df, customer_details_df)

# Save the dataset to a CSV file
claim_participant_df.to_csv('data/CLAIM_PARTICIPANT.csv', index=False)

print("CLAIM_PARTICIPANT dataset generated and saved as 'data/CLAIM_PARTICIPANT.csv'.")
