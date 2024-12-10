import streamlit as st
import joblib
import pandas as pd

# Paths
MODEL_PATH = 'models/fraud_detection_model.pkl'

# Load the trained model
try:
    model = joblib.load(MODEL_PATH)
    st.success("Model loaded successfully!")
except FileNotFoundError:
    st.error(f" Model file not found at {MODEL_PATH}. Please train the model and try again.")
    st.stop()
except Exception as e:
    st.error(f" Error loading model: {e}")
    st.stop()

# Streamlit App Title
st.title(" Fraud Detection Dashboard")

# Sidebar for input
st.sidebar.header("Enter Claim Details")

# Input fields for claim details (Only features required by the model)
clm_dtl_id = st.sidebar.number_input("Claim Detail ID", min_value=10000, step=1,
                                     help="Enter the unique claim detail ID")
clm_amt = st.sidebar.number_input("Claim Amount", min_value=0.0, step=100.0, help="Enter the claim amount")
clmt_avg_wkly_wage = st.sidebar.number_input("Claimant's Average Weekly Wage", min_value=0.0, step=50.0,
                                             help="Enter the claimant's weekly wage")
employment_status = st.sidebar.selectbox("Employment Status", ['Active', 'Inactive'],
                                         help="Select employment status of the claimant")
days_lost = st.sidebar.number_input("Days Lost", min_value=0, step=1,
                                    help="Enter the number of days lost due to the claim injury")
plcy_claim_limit = st.sidebar.number_input("Policy Claim Limit", min_value=0.0, step=1000.0,
                                           help="Enter the claim limit for the policy")

# Button to trigger prediction
if st.sidebar.button("Predict Fraud"):
    try:
        # Preprocess user inputs to match model requirements

        #  Compute engineered features
        employment_active_flag = 1 if employment_status == 'Active' else 0
        clm_amt_percent_limit = clm_amt / plcy_claim_limit if plcy_claim_limit > 0 else 0
        suspicious_claim_amount = 1 if clm_amt_percent_limit > 0.9 else 0

        # Prepare input data for prediction (Only the 8 selected features)
        input_data = pd.DataFrame([{
            'CLM_DTL_ID': clm_dtl_id,
            'CLM_AMT': clm_amt,
            'CLMT_AVG_WKLY_WAGE': clmt_avg_wkly_wage,
            'EMPLOYMENT_STATUS': 1 if employment_status == 'Active' else 0,
            'DAYS_LOST': days_lost,
            'CLM_AMT_PERCENT_LIMIT': clm_amt_percent_limit,
            'SUSPICIOUS_CLAIM_AMOUNT': suspicious_claim_amount,
            'EMPLOYMENT_ACTIVE_FLAG': employment_active_flag
        }])

        #  Predict fraud
        prediction = model.predict(input_data)[0]
        prediction_proba = model.predict_proba(input_data)[0]

        # Display prediction results
        st.subheader("Prediction Result")
        if prediction == 1:
            st.error(" This claim is predicted as **FRAUDULENT**!")
        else:
            st.success("This claim is predicted as **NOT FRAUDULENT**!")

        #  Display prediction probabilities
        st.subheader("Prediction Probabilities")
        st.write(f"Fraud Probability: {prediction_proba[1]:.2f}")
        st.write(f"Not Fraud Probability: {prediction_proba[0]:.2f}")

        # Display the input data for reference
        st.subheader("Input Data")
        st.dataframe(input_data)

    except Exception as e:
        st.error(f" Error in preparing data for prediction: {e}")
