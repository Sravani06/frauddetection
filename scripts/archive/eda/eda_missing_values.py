import pandas as pd
import os

# Load the unified dataset
DATA_PATH = os.path.join(os.getcwd(), 'data', 'Unified_Customer_Policy_Claim_Details.csv')
df = pd.read_csv(DATA_PATH)

# Calculate missing values
missing_values = df.isnull().sum()
total_rows = len(df)
missing_percentage = (missing_values / total_rows) * 100

# Display missing data for columns with at least 1 missing value
missing_data_report = pd.DataFrame({
    'Column': missing_values.index,
    'Missing Values': missing_values.values,
    'Missing Percentage': missing_percentage.values
})

# Filter to show only columns with missing values
missing_data_report = missing_data_report[missing_data_report['Missing Values'] > 0]
missing_data_report.sort_values(by='Missing Percentage', ascending=False, inplace=True)

# Display the missing data report
print("\n🚀 Missing Data Report:")
print(missing_data_report)
