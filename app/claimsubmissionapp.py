import streamlit as st
import datetime
import sqlite3
import random


# Database connection
def create_connection():
    return sqlite3.connect('db/claims.db')


# Dropdown options
states = ['CA', 'VA', 'NY', 'TX', 'FL', 'WA', 'MA', 'NV', 'OH', 'MI', 'WV', 'NJ']
injury_body_parts = [
    'Head', 'Back', 'Arm', 'Leg', 'Shoulder', 'Hand', 'Foot', 'Neck', 'Chest', 'Abdomen',
    'Hip', 'Knee', 'Elbow', 'Ankle', 'Wrist', 'Neck and Spine', 'Toes', 'Fingers', 'Teeth',
    'Ears', 'Eyes', 'Internal Organs', 'Pelvis', 'Groin'
]
injury_types = [
    'Fracture', 'Burn', 'Sprain', 'Cut', 'Bruise', 'Amputation', 'Dislocation', 'Puncture',
    'Contusion', 'Crush Injury', 'Tear', 'Laceration', 'Concussion', 'Whiplash',
    'Electric Shock', 'Frostbite', 'Poisoning', 'Radiation Exposure', 'Chemical Exposure',
    'Nerve Damage', 'Soft Tissue Injury', 'Eye Injury', 'Hearing Loss'
]
risk_levels = ['Low', 'Medium', 'High']
industries = [
    'Construction', 'Healthcare', 'Manufacturing', 'Transportation',
    'Retail', 'Education', 'Information Technology', 'Financial Services',
    'Hospitality', 'Warehousing', 'Agriculture', 'Mining', 'Energy',
    'Public Administration', 'Arts & Entertainment', 'Real Estate',
    'Professional Services', 'Telecommunications', 'Utilities', 'Wholesale Trade'
]
injury_severities = ['Low', 'Medium', 'High']
treatment_required = ['Yes', 'No']


# Function to generate a unique claim number
def generate_claim_number():
    today = datetime.date.today().strftime('%Y%m%d')
    random_number = random.randint(1000, 9999)
    return f"CLM{today}{random_number}"


# Claim Submission Form
st.title("Claim Submission Portal")

with st.form("claim_submission_form"):
    st.header("Claim Details")
    clm_occr_dt = st.date_input("Claim Occurrence Date", value=datetime.date.today())
    clm_occr_state = st.selectbox("Claim Occurrence State", options=states)
    clm_amt = st.number_input("Claim Amount ($)", min_value=0.0, step=0.01)

    st.header("Policy Details")
    plcy_start_dt = st.date_input("Policy Start Date")
    plcy_end_dt = st.date_input("Policy End Date")
    plcy_risk_level = st.selectbox("Policy Risk Level", options=risk_levels)
    plcy_claim_limit = st.number_input("Policy Claim Limit ($)", min_value=0.0, step=0.01)

    st.header("Reported Details")
    st.subheader("Claimant Details")
    clmnt_first_name = st.text_input("Claimant First Name")
    clmnt_last_name = st.text_input("Claimant Last Name")
    clmnt_state = st.selectbox("Claimant Residing State", options=states)
    clmnt_industry = st.selectbox("Claimant Industry", options=industries)

    st.subheader("Insured Details")
    insured_first_name = st.text_input("Insured First Name")
    insured_last_name = st.text_input("Insured Last Name")
    insured_state = st.selectbox("Insured Residing State", options=states)
    insured_industry = st.selectbox("Insured Industry", options=industries)

    st.subheader("Medical Provider Details")
    medprov_first_name = st.text_input("Medical Provider First Name")
    medprov_last_name = st.text_input("Medical Provider Last Name")
    medprov_state = st.selectbox("Medical Provider State", options=states)

    st.header("Injury Details")
    injury_body_part = st.selectbox("Injury Body Part", options=injury_body_parts)
    injury_type = st.selectbox("Injury Type", options=injury_types)
    injury_severity = st.selectbox("Injury Severity", options=injury_severities)
    treatment_req = st.selectbox("Treatment Required?", options=treatment_required)
    days_lost = st.number_input("Days Lost Due to Injury", min_value=0, step=1)
    prescriber_notes = st.text_area("Prescriber Notes")

    submitted = st.form_submit_button("Submit")

    if submitted:
        # Generate a unique claim number
        claim_number = generate_claim_number()

        # Connect to the database
        conn = create_connection()
        cursor = conn.cursor()

        # Insert claim details into the Claims Table
        cursor.execute('''
            INSERT INTO main.Claim_Details_submission (
                CLAIM_NUMBER, CLAIM_OCCUR_DATE, CLAIM_STATE, CLAIM_AMOUNT,
                POLICY_START_DATE, POLICY_END_DATE, POLICY_RISK_LEVEL, POLICY_CLAIM_LIMIT,
                CLAIMANT_FIRST_NAME, CLAIMANT_LAST_NAME, CLAIMANT_STATE, CLAIMANT_INDUSTRY,
                INSURED_FIRST_NAME, INSURED_LAST_NAME, INSURED_STATE, INSURED_INDUSTRY,
                MEDICAL_PROVIDER_FIRST_NAME, MEDICAL_PROVIDER_LAST_NAME, MEDICAL_PROVIDER_STATE,
                INJURY_BODY_PART, INJURY_TYPE, INJURY_SEVERITY, TREATMENT_REQUIRED, DAYS_LOST, PRESCRIBER_NOTES
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            claim_number, clm_occr_dt, clm_occr_state, clm_amt,
            plcy_start_dt, plcy_end_dt, plcy_risk_level, plcy_claim_limit,
            clmnt_first_name, clmnt_last_name, clmnt_state, clmnt_industry,
            insured_first_name, insured_last_name, insured_state, insured_industry,
            medprov_first_name, medprov_last_name, medprov_state,
            injury_body_part, injury_type, injury_severity, treatment_req, days_lost, prescriber_notes
        ))

        conn.commit()
        conn.close()

        st.success(f"Your Claim has been submitted successfully. Your Claim Number is: **{claim_number}**")
