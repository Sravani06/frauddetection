import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Step 1: Load the enhanced dataset
print("Loading the enhanced unified dataset...")
df = pd.read_csv('data/unified_dataset_enhanced.csv')

# Step 2: Initialize the fraud indicator column with 0 (non-fraudulent)
df['FRAUD_INDICATOR'] = 0

# Step 3: Apply the conditions for each of the use cases available in the enhanced data list

# 1. PENDING_180_DAYS
df.loc[df['PENDING_180_DAYS'] == 1, 'FRAUD_INDICATOR'] = 1

# 2. DECLINED_WITH_PAYMENTS
df.loc[df['DECLINED_WITH_PAYMENTS'] == 1, 'FRAUD_INDICATOR'] = 1

# 3. MAXIMUM_POLICY_AMOUNT_EXCEEDED
df.loc[df['MAXIMUM_POLICY_AMOUNT_EXCEEDED'] == 1, 'FRAUD_INDICATOR'] = 1

# 4. MULTIPLE_INJURIES
df.loc[df['MULTIPLE_INJURIES'] == 1, 'FRAUD_INDICATOR'] = 1

# 5. CUSTOMER_WITH_MULTIPLE_JURISDICTIONS
df.loc[df['CUSTOMER_WITH_MULTIPLE_JURISDICTIONS'] == 1, 'FRAUD_INDICATOR'] = 1

# 6. LONG_PENDING_CLAIMS
df.loc[df['LONG_PENDING_CLAIMS'] == 1, 'FRAUD_INDICATOR'] = 1

# 7. POLICY_PREMIUM_TOO_LOW
df.loc[df['POLICY_PREMIUM_TOO_LOW'] == 1, 'FRAUD_INDICATOR'] = 1

# 8. CUSTOMER_WITH_HIGH_AGE
df.loc[df['CUSTOMER_WITH_HIGH_AGE'] == 1, 'FRAUD_INDICATOR'] = 1

# 9. CUSTOMER_WITH_LOW_AGE
df.loc[df['CUSTOMER_WITH_LOW_AGE'] == 1, 'FRAUD_INDICATOR'] = 1

# 10. SUPERVISOR_NOT_LISTED
df.loc[df['SUPERVISOR_NOT_LISTED'] == 1, 'FRAUD_INDICATOR'] = 1

# 11. CLAIM_BEFORE_POLICY_EFFECTIVE
df.loc[df['CLAIM_BEFORE_POLICY_EFFECTIVE'] == 1, 'FRAUD_INDICATOR'] = 1

# 12. INJURY_REPORTED_AFTER_30_DAYS
df.loc[df['INJURY_REPORTED_AFTER_30_DAYS'] == 1, 'FRAUD_INDICATOR'] = 1

# 13. HIGH_PAYMENT_AMOUNT_RELATIVE_TO_CLAIM
df.loc[df['HIGH_PAYMENT_AMOUNT_RELATIVE_TO_CLAIM'] == 1, 'FRAUD_INDICATOR'] = 1

# 14. MULTIPLE_DECLINED_STATUS_UPDATES
df.loc[df['MULTIPLE_DECLINED_STATUS_UPDATES'] == 1, 'FRAUD_INDICATOR'] = 1

# 15. MULTIPLE_CLAIMS_FROM_SAME_ADDRESS
df.loc[df['MULTIPLE_CLAIMS_FROM_SAME_ADDRESS'] == 1, 'FRAUD_INDICATOR'] = 1

# 16. INJURY_NOT_WORK_RELATED
df.loc[df['INJURY_NOT_WORK_RELATED'] == 1, 'FRAUD_INDICATOR'] = 1

# 17. OUT_OF_JURISDICTION
df.loc[df['OUT_OF_JURISDICTION'] == 1, 'FRAUD_INDICATOR'] = 1

# 18. OCCURRED_ON_WEEKEND
df.loc[df['OCCURRED_ON_WEEKEND'] == 1, 'FRAUD_INDICATOR'] = 1

# 19. CUSTOMER_TOTAL_CLAIMS
df.loc[df['CUSTOMER_TOTAL_CLAIMS'] > 5, 'FRAUD_INDICATOR'] = 1

# 30. INJURY_REPORTED_AFTER_30_DAYS
df.loc[df['INJURY_REPORTED_AFTER_30_DAYS'] == 1, 'FRAUD_INDICATOR'] = 1

# 37. HIGH_PAYMENT_AMOUNT_RELATIVE_TO_CLAIM
df.loc[df['HIGH_PAYMENT_AMOUNT_RELATIVE_TO_CLAIM'] == 1, 'FRAUD_INDICATOR'] = 1

# 38. MULTIPLE_DECLINED_STATUS_UPDATES
df.loc[df['MULTIPLE_DECLINED_STATUS_UPDATES'] == 1, 'FRAUD_INDICATOR'] = 1

# 40. MULTIPLE_CLAIMS_FROM_SAME_ADDRESS
df.loc[df['MULTIPLE_CLAIMS_FROM_SAME_ADDRESS'] == 1, 'FRAUD_INDICATOR'] = 1


# 43. INJURY_NOT_WORK_RELATED
df.loc[df['INJURY_NOT_WORK_RELATED'] == 1, 'FRAUD_INDICATOR'] = 1



# Step 4: Control the Fraud Rate (Keep fraud rate at 30%)
fraudulent_claims = df[df['FRAUD_INDICATOR'] == 1]
non_fraudulent_claims = df[df['FRAUD_INDICATOR'] == 0]

desired_fraud_count = int(0.30 * len(df))

if len(fraudulent_claims) > desired_fraud_count:
    # If too many fraudulent claims, randomly select only 30% of them
    print("Too many fraudulent claims detected, downsampling to 30%...")
    selected_fraudulent_claims = fraudulent_claims.sample(n=desired_fraud_count, random_state=42)
    df['FRAUD_INDICATOR'] = 0
    df.loc[selected_fraudulent_claims.index, 'FRAUD_INDICATOR'] = 1

elif len(fraudulent_claims) < desired_fraud_count:
    # If too few fraudulent claims, randomly add additional frauds
    print("Too few fraudulent claims detected, upsampling to 30%...")
    additional_frauds_needed = desired_fraud_count - len(fraudulent_claims)
    extra_fraud_claims = non_fraudulent_claims.sample(n=additional_frauds_needed, random_state=42)
    df.loc[extra_fraud_claims.index, 'FRAUD_INDICATOR'] = 1

# Step 5: Save the final dataset
print(f"Exporting final dataset with fraud flags to 'data/final_fraud_dataset.csv'...")

