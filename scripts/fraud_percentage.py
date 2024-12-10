import pandas as pd

# Load the enhanced fraud detection dataset
df = pd.read_csv('data/Enhanced_Fraud_Detection.csv')

# Calculate the total number of claims
total_claims = len(df)

# Count the number of fraudulent claims
fraudulent_claims = df['CLM_FRAUD_IND'].sum()  # Sum of 1s in CLM_FRAUD_IND gives the total fraudulent claims

# Calculate the percentage of fraud claims
fraud_percentage = (fraudulent_claims / total_claims) * 100

# Print the results
print(f" Total Claims: {total_claims}")
print(f" Fraudulent Claims: {fraudulent_claims}")
print(f" Fraud Percentage: {fraud_percentage:.2f}%")

# Check if the fraud percentage matches the target (15%)
if abs(fraud_percentage - 15) <= 1:  # Allowing for 1% tolerance
    print(" The fraud rate is within the acceptable range (around 15%).")
else:
    print(f" The fraud rate is {fraud_percentage:.2f}%, which is outside the target range of 15%.")
