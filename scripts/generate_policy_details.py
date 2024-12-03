import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, timedelta

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Number of records to generate
num_policies = 1000

# Function to generate POLICY_DETAILS dataset
def generate_policy_details(num_records):
    policy_details = []
    policy_id_start = 40001  # Starting ID for PLCY_DTL_ID

    # Convert start_date and end_date to datetime.date
    start_date = date(2006, 1, 1)
    end_date = date(2024, 12, 31)

    for _ in range(num_records):
        # PLCY_DTL_ID: Incremental unique ID
        plcy_dtl_id = policy_id_start
        policy_id_start += 1

        # PLCY_NO: Unique policy number starting with "COF" + 7 random digits
        plcy_no = f"COF{np.random.randint(1000000, 9999999)}"

        # PLCY_STRT_DT: Random start date between start_date and end_date
        plcy_strt_dt = fake.date_between(start_date=start_date, end_date=end_date)

        # PLCY_END_DT: One year from the start date
        plcy_end_dt = plcy_strt_dt + timedelta(days=365)

        # Append the record
        policy_details.append([plcy_dtl_id, plcy_no, plcy_strt_dt, plcy_end_dt])

    # Convert to DataFrame
    return pd.DataFrame(policy_details, columns=[
        'PLCY_DTL_ID', 'PLCY_NO', 'PLCY_STRT_DT', 'PLCY_END_DT'
    ])

# Generate the dataset
policy_details_df = generate_policy_details(num_policies)

# Save the dataset to a CSV file
policy_details_df.to_csv('data/POLICY_DETAILS.csv', index=False)

print("POLICY_DETAILS dataset generated and saved as 'data/POLICY_DETAILS.csv'.")
