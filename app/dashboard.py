import streamlit as st
import pandas as pd
import joblib
import shap
import sqlite3
import numpy as np

# Function to fetch claim data
def fetch_claim_data(claim_number, db_path='db/claims.db'):
    query = f"SELECT * FROM Claim_Details_submission WHERE CLAIM_NUMBER = '{claim_number}'"
    with sqlite3.connect(db_path) as conn:  # Thread-safe SQLite connection
        return pd.read_sql_query(query, conn)

# Load pre-trained models
@st.cache_resource
def load_models():
    models = {
        'OneClassSVM': joblib.load('models/one_class_svm.pkl'),
        'XGBoost': joblib.load('models/xgboost.pkl'),
        'RandomForest': joblib.load('models/random_forest.pkl'),
    }
    return models

@st.cache_resource
def load_training_features():
    return joblib.load('models/training_features.pkl')

# App Title
st.title('Fraud Prediction Dashboard')

models = load_models()
training_features = load_training_features()

st.sidebar.header('Claim Lookup')
claim_number_input = st.sidebar.text_input("Enter Claim Number").strip().upper()

def align_features(input_features, training_features):
    input_features = input_features.reindex(columns=training_features, fill_value=0)
    return input_features

if claim_number_input:
    try:
        # Fetch claim data
        claim_details = fetch_claim_data(claim_number_input)

        if not claim_details.empty:
            st.success(f"Claim Number {claim_number_input} found!")

            # Display Claim Details
            st.subheader('Claim Details')
            st.dataframe(claim_details)

            # Prepare Features for Prediction
            input_features = claim_details.drop(columns=['CLAIM_ID', 'CLAIM_NUMBER'], errors='ignore')

            # Ensure numeric and categorical handling
            numeric_cols = input_features.select_dtypes(include=['int64', 'float64']).columns
            categorical_cols = input_features.select_dtypes(include=['object']).columns
            input_features[numeric_cols] = input_features[numeric_cols].fillna(0)
            input_features[categorical_cols] = input_features[categorical_cols].fillna('Unknown')
            input_features = pd.get_dummies(input_features, drop_first=True)

            # Align input features with training features
            input_features = align_features(input_features, training_features)

            # Majority Voting Prediction
            st.subheader(' Model Predictions')
            predictions = []

            try:
                # One-Class SVM
                svm_prediction = models['OneClassSVM'].predict(input_features)
                predictions.append(-1 if svm_prediction[0] == -1 else 0)
            except Exception as e:
                st.warning(f"Error with One-Class SVM Prediction: {str(e)}")

            try:
                # XGBoost
                xgb_prediction = models['XGBoost'].predict(input_features)
                predictions.append(xgb_prediction[0])
            except Exception as e:
                st.warning(f"Error with XGBoost Prediction: {str(e)}")

            try:
                # Random Forest
                rf_prediction = models['RandomForest'].predict(input_features)
                predictions.append(rf_prediction[0])
            except Exception as e:
                st.warning(f"Error with Random Forest Prediction: {str(e)}")

            # Majority Voting
            final_prediction = 1 if predictions.count(1) > predictions.count(0) else 0
            prediction_label = "Fraud" if final_prediction == 1 else "Not Fraud"
            st.write(f"**Overall Prediction:** {prediction_label}")

            # # SHAP Explanation
            # st.subheader(' SHAP Explanation')
            # try:
            #     explainer = shap.Explainer(models['RandomForest'], input_features)
            #     shap_values = explainer(input_features)
            #
            #     # Summarize top features
            #     shap_summary = pd.DataFrame({
            #         'Feature': input_features.columns,
            #         'SHAP Value': shap_values.values[0],
            #         'Feature Value': input_features.iloc[0].values
            #     }).sort_values(by='SHAP Value', key=abs, ascending=False)
            #
            #     # Display textual explanation
            #     top_features = shap_summary.head(3)
            #     explanation = "\n".join(
            #         [f"- {row['Feature']} (Value: {row['Feature Value']}, SHAP: {row['SHAP Value']:.4f})"
            #          for _, row in top_features.iterrows()]
            #     )
            #     st.markdown(f"**Top Contributing Features:**\n{explanation}")
            #
            # except Exception as e:
            #     st.warning(f"SHAP explanation failed: {str(e)}")
            def generate_rule_based_insights(claim_details):
                """
                Generate rule-based insights for a given claim.
                Args:
                    claim_details (DataFrame): A DataFrame containing details of the claim.
                Returns:
                    List of strings explaining the triggered rules.
                """
                insights = []

                # Rule 1: High claim amount
                if claim_details['CLAIM_AMOUNT'].values[0] > 10000:  # Example threshold, can be adjusted
                    insights.append(f"High Claim Amount: ${claim_details['CLAIM_AMOUNT'].values[0]} exceeds $10,000.")

                # Rule 2: Mismatch between claimant and insured states
                if claim_details['CLAIMANT_STATE'].values[0] != claim_details['INSURED_STATE'].values[0]:
                    insights.append(
                        f"Mismatch between Claimant State ({claim_details['CLAIMANT_STATE'].values[0]}) and Insured State ({claim_details['INSURED_STATE'].values[0]}).")

                # Rule 3: Claim occurred after the policy ended
                if pd.to_datetime(claim_details['POLICY_END_DATE'].values[0]) < pd.to_datetime(
                        claim_details['CLAIM_OCCUR_DATE'].values[0]):
                    insights.append("Claim occurred after the policy expired.")

                # Rule 4: Claim filed near policy expiration (last 7 days of policy)
                if (pd.to_datetime(claim_details['POLICY_END_DATE'].values[0]) - pd.to_datetime(
                        claim_details['CLAIM_OCCUR_DATE'].values[0])).days <= 7:
                    insights.append("Claim occurred near the policy expiry date.")

                # Rule 5: Unusual injury body part
                if claim_details['INJURY_BODY_PART'].values[0] in ['Toes', 'Fingers', 'Teeth', 'Internal Organs']:
                    insights.append(f"Unusual injury body part: {claim_details['INJURY_BODY_PART'].values[0]}.")

                # Rule 6: Unusual injury type
                if claim_details['INJURY_TYPE'].values[0] in ['Radiation Exposure', 'Frostbite', 'Chemical Exposure']:
                    insights.append(f"Uncommon injury type: {claim_details['INJURY_TYPE'].values[0]}.")

                # Rule 7: High injury severity but low treatment required
                if claim_details['INJURY_SEVERITY'].values[0] == 'High' and claim_details['TREATMENT_REQUIRED'].values[
                    0] == 'No':
                    insights.append("Inconsistent injury severity (High) with no treatment required.")

                # Rule 8: Multiple claims for the same claimant in a short period (Less than 30 days)
                if 'PREVIOUS_CLAIM_DATE' in claim_details.columns:
                    if (pd.to_datetime(claim_details['CLAIM_OCCUR_DATE'].values[0]) - pd.to_datetime(
                            claim_details['PREVIOUS_CLAIM_DATE'].values[0])).days < 30:
                        insights.append("Multiple claims for the same claimant within 30 days.")

                # Rule 9: Claim reported on a weekend
                claim_report_day = pd.to_datetime(claim_details['CLAIM_REPORT_DATE'].values[0]).weekday()
                if claim_report_day in [5, 6]:  # Saturday and Sunday
                    insights.append(
                        f"Claim reported on a weekend ({['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][claim_report_day]}).")

                # Rule 10: Large gap between injury date and report date
                if 'CLM_RPT_DT' in claim_details.columns:
                    days_gap = (pd.to_datetime(claim_details['CLM_RPT_DT'].values[0]) - pd.to_datetime(
                        claim_details['CLAIM_OCCUR_DATE'].values[0])).days
                    if days_gap > 30:
                        insights.append(
                            f"Significant delay in claim reporting: {days_gap} days from injury date to report date.")

                # Rule 11: High claim amount relative to policy limit
                if 'POLICY_LIMIT' in claim_details.columns:
                    if claim_details['CLAIM_AMOUNT'].values[0] > 0.9 * claim_details['POLICY_LIMIT'].values[0]:
                        insights.append("Claim amount is close to the policy limit (above 90%).")

                # Rule 12: Repeated use of the same medical provider
                if claim_details['MEDICAL_PROVIDER_NAME'].values[0] in ['Provider_A',
                                                                        'Provider_B']:  # Adjust for real provider names
                    insights.append(
                        f"Repeated use of the same medical provider ({claim_details['MEDICAL_PROVIDER_NAME'].values[0]}).")

                # Rule 13: Suspicious job title for injury type (e.g., Software Engineer with back injury)
                if claim_details['JOB_TITLE'].values[0] in ['Software Engineer', 'Data Analyst'] and \
                        claim_details['INJURY_BODY_PART'].values[0] in ['Back', 'Shoulder']:
                    insights.append(
                        f"Suspicious injury for job title: {claim_details['JOB_TITLE'].values[0]} with {claim_details['INJURY_BODY_PART'].values[0]} injury.")

                # Rule 14: Multiple providers for a single claimant
                if 'TOTAL_PROVIDERS' in claim_details.columns and claim_details['TOTAL_PROVIDERS'].values[0] > 3:
                    insights.append(
                        f"Claimant has used multiple providers ({claim_details['TOTAL_PROVIDERS'].values[0]} providers) for a single claim.")

                # Rule 15: Claim from a high-risk state
                high_risk_states = ['NY', 'NJ', 'CA', 'TX']
                if claim_details['CLAIMANT_STATE'].values[0] in high_risk_states:
                    insights.append(f"Claim from a high-risk state ({claim_details['CLAIMANT_STATE'].values[0]}).")

                # Rule 16: Claimant recently terminated
                if claim_details['EMPLOYMENT_STATUS'].values[0] == 'Terminated':
                    insights.append("Claimant was recently terminated.")

                # Rule 17: Medical treatment for low-severity injury
                if claim_details['INJURY_SEVERITY'].values[0] == 'Low' and claim_details['TREATMENT_REQUIRED'].values[
                    0] == 'Yes':
                    insights.append("Treatment required for a low-severity injury, which is unusual.")

                # Rule 18: Duplicate claim within a short timeframe (same injury type, claimant, and injury date)
                if 'DUPLICATE_CLAIM' in claim_details.columns and claim_details['DUPLICATE_CLAIM'].values[0] == 1:
                    insights.append("Duplicate claim detected for the same claimant, injury type, and injury date.")

                # Rule 19: Inconsistent dates (e.g., claim date before injury date)
                if pd.to_datetime(claim_details['CLAIM_REPORT_DATE'].values[0]) < pd.to_datetime(
                        claim_details['CLAIM_OCCUR_DATE'].values[0]):
                    insights.append("Inconsistent dates: Claim reported before the injury occurred.")

                # Rule 20: Unusual timing for claim reporting (e.g., late night reporting)
                if 'CLAIM_REPORT_TIME' in claim_details.columns:
                    report_time = pd.to_datetime(claim_details['CLAIM_REPORT_TIME'].values[0]).hour
                    if report_time < 6 or report_time > 22:
                        insights.append(f"Claim reported at an unusual time: {report_time}:00 hrs.")

                # Rule 21: Claimant or insured state flagged for fraud risk
                flagged_states = ['CA', 'NY', 'NJ']
                if claim_details['CLAIMANT_STATE'].values[0] in flagged_states or claim_details['INSURED_STATE'].values[
                    0] in flagged_states:
                    insights.append(
                        f"Claimant or Insured is from a flagged high-fraud-risk state ({claim_details['CLAIMANT_STATE'].values[0]} or {claim_details['INSURED_STATE'].values[0]}).")

                # Rule 22: Employment mismatch (e.g., job type not matching the injury)
                if claim_details['JOB_TYPE'].values[0] in ['Desk Job', 'Office'] and \
                        claim_details['INJURY_BODY_PART'].values[0] in ['Leg', 'Foot']:
                    insights.append(
                        f"Job type ({claim_details['JOB_TYPE'].values[0]}) is inconsistent with injury to {claim_details['INJURY_BODY_PART'].values[0]}.")

                if not insights:
                    insights.append("No specific fraud indicators were triggered for this claim.")

                return insights

            st.subheader(" Why this Prediction?")

            # If the final prediction is "Not Fraud", display a message and skip rule evaluation
            if final_prediction == 0:  # 0 = Not Fraud
                st.markdown("No specific rules were triggered for this claim.")
            else:  # 1 = Fraud
                rule_insights = generate_rule_based_insights(claim_details, prediction_label)
                if rule_insights and len(rule_insights) > 0:
                    for insight in rule_insights:
                        st.markdown(f"- {insight}")
                else:
                    st.markdown("No specific rules were triggered for this claim.")
        else:
            st.error(f"Claim Number {claim_number_input} not found.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.info('Enter a claim number to begin.')

# Footer
st.sidebar.markdown("##  Useful Tips")
st.sidebar.markdown("""
- Ensure claim numbers are valid and available in the system.
- Only valid claim numbers will display claim details, predictions, and SHAP explanations.
""")