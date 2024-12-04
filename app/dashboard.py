import streamlit as st
import pandas as pd
import sqlite3

# Title
st.title("Fraud Detection Dashboard")

# Input for Claim Number
claim_number = st.text_input("Enter Claim Number:")


# Mock function to fetch claim data
def get_claim_data_mock(claim_no):
    # Mocked Data
    mock_data = {
        "CLM_NO": claim_no,
        "CLM_AMT": 1200,
        "CUST_AGE": 45,
        "CLM_TYP": "Medical",
        "CLM_OCCR_DT": "2023-09-15",
        "PREDICTION": "Not Fraudulent"  # Mock prediction
    }
    return pd.DataFrame([mock_data])


# Predict Fraud (Mock)
if st.button("Predict"):
    if claim_number:
        # Fetch data (mock for now)
        claim_data = get_claim_data_mock(claim_number)

        if claim_data.empty:
            st.error("Claim not found.")
        else:
            # Display claim details
            st.subheader("Claim Details")
            st.dataframe(claim_data.drop(columns=["PREDICTION"]))

            # Display prediction
            st.subheader(f"Prediction: {claim_data['PREDICTION'][0]}")
    else:
        st.error("Please enter a claim number.")
