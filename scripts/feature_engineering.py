import pandas as pd
import holidays

#  File Paths
CLEANED_FILE = 'data/Cleaned_Unified_Customer_Policy_Claim_Details.csv'
FEATURED_FILE = 'data/Featured_Unified_Customer_Policy_Claim_Details.csv'

#  Neighboring State Logic (State Adjacency List)
neighboring_states = {
    'NY': ['NJ', 'CT', 'PA', 'MA', 'VT'],
    'NJ': ['NY', 'PA', 'DE'],
    'CA': ['OR', 'NV', 'AZ'],
    'NV': ['CA', 'AZ', 'UT', 'ID'],
    'PA': ['NY', 'NJ', 'OH', 'MD', 'DE', 'WV'],
    'CT': ['NY', 'MA', 'RI'],
    'MA': ['CT', 'NY', 'VT', 'NH'],
    'OH': ['PA', 'MI', 'IN', 'KY', 'WV'],
    'MI': ['OH', 'IN', 'WI'],
    'FL': ['GA', 'AL'],
    'TX': ['NM', 'OK', 'AR', 'LA'],
    'IL': ['IN', 'WI', 'IA', 'MO', 'KY'],
    'WA': ['OR', 'ID'],
    'OR': ['CA', 'WA', 'NV', 'ID'],
    'GA': ['FL', 'AL', 'TN', 'NC', 'SC'],
    'NC': ['GA', 'SC', 'TN', 'VA'],
    'SC': ['GA', 'NC'],
    'VA': ['NC', 'TN', 'KY', 'WV', 'MD'],
    'MD': ['VA', 'DE', 'PA', 'WV'],
    'DE': ['MD', 'PA', 'NJ'],
    'AZ': ['CA', 'NV', 'UT', 'NM'],
    'UT': ['NV', 'CO', 'WY', 'ID', 'AZ'],
    'CO': ['UT', 'NM', 'WY', 'NE', 'KS', 'OK'],
    'NM': ['AZ', 'CO', 'TX', 'OK'],
    'WV': ['OH', 'PA', 'MD', 'VA', 'KY'],
    'KY': ['IL', 'IN', 'OH', 'WV', 'VA', 'TN', 'MO'],
    'TN': ['KY', 'VA', 'NC', 'GA', 'AL', 'MS', 'AR', 'MO']
}
#  Injury Type Risk Mapping
injury_risk_mapping = {
    'High': [ 'Burn', 'Amputation', 'Concussion',
             'Crush Injury', 'Electric Shock', 'Nerve Damage', 'Poisoning', 'Radiation Exposure', 'Chemical Exposure'],
    'Medium': ['Tear', 'Laceration', 'Sprain', 'Soft Tissue Injury', 'Hearing Loss',
               'Eye Injury', 'Frostbite', 'Dislocation'],
    'Low': ['Bruise', 'Cut', 'Puncture', 'Contusion', 'Fracture']
}

#  Injury Body Part Risk Mapping
body_part_risk_mapping = {
    'High': ['Head', 'Spine', 'Neck', 'Chest', 'Internal Organs', 'Brain'],
    'Medium': ['Back', 'Hip', 'Pelvis', 'Shoulder', 'Abdomen', 'Eyes', 'Ears', 'Groin'],
    'Low': ['Hand', 'Foot', 'Ankle', 'Fingers', 'Toes', 'Elbow', 'Knee', 'Wrist']
}


#  Load Data
print("Loading cleaned dataset...")
df = pd.read_csv(CLEANED_FILE, parse_dates=['CLM_RPT_DT', 'CLM_OCCR_DT', 'PLCY_STRT_DT', 'PLCY_END_DT'], low_memory=False)

#  Feature 1: Time-Based Features
print("Generating time-based features...")
df['DAYS_BETWEEN_REPORT_OCCUR'] = (df['CLM_RPT_DT'] - df['CLM_OCCR_DT']).dt.days
df['DAYS_TO_POLICY_END'] = (df['PLCY_END_DT'] - df['CLM_OCCR_DT']).dt.days
df['DAYS_FROM_POLICY_START'] = (df['CLM_OCCR_DT'] - df['PLCY_STRT_DT']).dt.days
df['REPORT_HOUR'] = df['CLM_RPT_DT'].dt.hour
df['REPORT_DAY_OF_WEEK'] = df['CLM_RPT_DT'].dt.dayofweek  # 0 = Monday, 6 = Sunday
df['WEEKEND_CLAIM'] = df['REPORT_DAY_OF_WEEK'].apply(lambda x: 1 if x in [5, 6] else 0)

# Dynamic holiday logic
us_holidays = holidays.US()
df['HOLIDAY_CLAIM'] = df['CLM_RPT_DT'].dt.date.isin(us_holidays).astype(int)

# Feature 2: Location-Based Features
print("Generating location-based features...")
def check_if_neighboring(state1, state2):
    """Check if two states are neighbors according to the adjacency list."""
    if state1 == state2:
        return True
    if state1 in neighboring_states and state2 in neighboring_states[state1]:
        return True
    if state2 in neighboring_states and state1 in neighboring_states[state2]:
        return True
    return False

# Check if insured, claimant, and medical provider states are "neighbors"
df['NEIGHBOR_STATE_FLAG'] = df.apply(
    lambda row: int(
        check_if_neighboring(row['INSURED_CUST_STATE'], row['CLM_OCCR_STATE']) and
        check_if_neighboring(row['INSURED_CUST_STATE'], row['MEDPROV_CUST_STATE']) and
        check_if_neighboring(row['CLM_OCCR_STATE'], row['MEDPROV_CUST_STATE'])
    ), axis=1
)

# Count how many states do not match (if neighbors, ignore)
df['STATE_DISCREPANCY_COUNT'] = (
    ((df['INSURED_CUST_STATE'] != df['CLM_OCCR_STATE']) & (df['NEIGHBOR_STATE_FLAG'] == 0)).astype(int) +
    ((df['INSURED_CUST_STATE'] != df['MEDPROV_CUST_STATE']) & (df['NEIGHBOR_STATE_FLAG'] == 0)).astype(int)
)

df['STATE_DISCREPANCY_COUNT'] = (df['INSURED_CUST_STATE'] != df['CLM_OCCR_STATE']).astype(int) + \
                                (df['INSURED_CUST_STATE'] != df['MEDPROV_CUST_STATE']).astype(int)

# Feature 3: Claim Frequency Features
print("Generating claim frequency features...")
df['CLAIMANT_CLAIM_COUNT'] = df.groupby('CUST_ID_CLAIMANT')['CLM_DTL_ID'].transform('count')
df['PROVIDER_CLAIM_COUNT'] = df.groupby('CUST_ID_MED_PROV')['CLM_DTL_ID'].transform('count')
df['INSURED_CLAIM_COUNT'] = df.groupby('CUST_ID_INSURED')['CLM_DTL_ID'].transform('count')

#  Feature 4: Injury-Related Features
print("Generating injury-related features...")
def map_injury_risk_level(injury_type):
    """Assign risk level to injury type: High = 3, Medium = 2, Low = 1"""
    if injury_type in injury_risk_mapping['High']:
        return 3
    elif injury_type in injury_risk_mapping['Medium']:
        return 2
    elif injury_type in injury_risk_mapping['Low']:
        return 1
    return 0  # Unknown injury type (edge case)

df['INJURY_TYPE_RISK_LEVEL'] = df['INJURY_TYPE'].apply(map_injury_risk_level)
#  Feature 2: Injury Body Part Risk Level
def map_body_part_risk_level(body_part):
    """Assign risk level to body part: High = 3, Medium = 2, Low = 1"""
    if body_part in body_part_risk_mapping['High']:
        return 3
    elif body_part in body_part_risk_mapping['Medium']:
        return 2
    elif body_part in body_part_risk_mapping['Low']:
        return 1
    return 0  # Unknown body part (edge case)

df['INJURY_BODY_PART_RISK_LEVEL'] = df['INJURY_BODY_PART'].apply(map_body_part_risk_level)

#  Feature 3: Combined Risk Score
# Combine injury type risk and body part risk for a unified risk score
df['RISK_SCORE'] = df['INJURY_TYPE_RISK_LEVEL'] + df['INJURY_BODY_PART_RISK_LEVEL']

#  Feature 4: High Risk Flag
# Flag claims as high risk if the combined risk score is greater than or equal to a threshold
HIGH_RISK_THRESHOLD = 5  # Threshold is configurable (e.g., 5 means (3+2) or (3+3))
df['HIGH_RISK_FLAG'] = (df['RISK_SCORE'] >= HIGH_RISK_THRESHOLD).astype(int)

#  Additional Features
# Create feature interactions for better model performance
df['HIGH_RISK_BODY_PART_FLAG'] = df['INJURY_BODY_PART_RISK_LEVEL'].apply(lambda x: 1 if x == 3 else 0)
df['HIGH_RISK_INJURY_TYPE_FLAG'] = df['INJURY_TYPE_RISK_LEVEL'].apply(lambda x: 1 if x == 3 else 0)


#  Feature 5: Behavioral Features
print("Generating behavioral features...")
df['MULTIPLE_SAME_DAY_CLAIMS'] = df.groupby(['CUST_ID_CLAIMANT', 'CLM_OCCR_DT'])['CLM_DTL_ID'].transform('count') > 1
df['PROVIDER_WEEKEND_CLAIMS'] = df.groupby('CUST_ID_MED_PROV')['REPORT_DAY_OF_WEEK'].apply(lambda x: (x > 4).sum())
df['FREQUENT_LATE_CLAIMS'] = (df['DAYS_BETWEEN_REPORT_OCCUR'] > 30).astype(int)
df['SHORT_REPORT_TIME'] = (df['DAYS_BETWEEN_REPORT_OCCUR'] < 1).astype(int)

#  Feature 6: Include all 60+ Fraud Rule Indicators
print("Including all fraud rule indicators...")
fraud_rule_columns = [col for col in df.columns if 'Fraud_Rule' in col]
print(f"Total Fraud Rule Indicators Identified: {len(fraud_rule_columns)}")

#  Feature 7: Aggregated Fraud Indicators
df['FRAUD_RULE_SUM'] = df[fraud_rule_columns].sum(axis=1)
df['FRAUD_RULE_COUNT'] = (df[fraud_rule_columns] > 0).sum(axis=1)
df['FRAUD_RULE_RATIO'] = df['FRAUD_RULE_COUNT'] / len(fraud_rule_columns)

#  Feature 8: Interaction Features
df['REPORT_HOUR_DAY_COMBO'] = df['REPORT_HOUR'] * df['REPORT_DAY_OF_WEEK']
df['CLAIM_TO_POLICY_RATIO'] = df['CLM_AMT'] / (df['PLCY_CLAIM_LIMIT'] + 1e-9)  # Avoid division by zero
df['RISK_LEVEL_NUMERIC'] = df['RISK_LEVEL'].astype('category').cat.codes

#  Time-Based Features
df['DAYS_BETWEEN_REPORT_OCCUR'] = (df['CLM_RPT_DT'] - df['CLM_OCCR_DT']).dt.days
us_holidays = holidays.US()
df['HOLIDAY_CLAIM'] = df['CLM_RPT_DT'].dt.date.isin(us_holidays).astype(int)
df['WEEKEND_CLAIM'] = df['CLM_RPT_DT'].dt.dayofweek.apply(lambda x: 1 if x in [5, 6] else 0)


# Save Feature-Engineered Data
df.to_csv(FEATURED_FILE, index=False)
print(f"Feature-engineered dataset saved as {FEATURED_FILE}")
