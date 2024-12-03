import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, datetime, timedelta

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Number of records to generate
num_customers = 3000

# Function to generate CUSTOMER_DETAILS dataset
def generate_customer_details(num_records):
    customer_details = []

    for i in range(1, num_records + 1):
        # CUST_ID: Unique ID
        cust_id = i

        # CUST_TYP: Either 'prsn' or 'busn'
        cust_typ = np.random.choice(['prsn', 'busn'])

        # CUST_FRST_NM and CUST_LST_NM: Random first and last names
        cust_frst_nm = fake.first_name() if cust_typ == 'prsn' else fake.company()
        cust_lst_nm = fake.last_name() if cust_typ == 'prsn' else ""

        # CUST_GENDER: Male, Female, or Other (only applicable for 'prsn')
        cust_gender = (
            np.random.choice(['Male', 'Female', 'Other']) if cust_typ == 'prsn' else ""
        )

        # CUST_DOB: Random date of birth for 'prsn', blank for 'busn'
        cust_dob = (
            fake.date_of_birth(minimum_age=18, maximum_age=80)
            if cust_typ == 'prsn'
            else None
        )

        # CUST_DOD: Random date of death (or None if still alive)
        cust_dod = (
            fake.date_between(start_date=cust_dob, end_date=date.today()).strftime('%Y-%m-%d')
            if cust_typ == 'prsn' and np.random.rand() < 0.1
            else None
        ) if cust_dob else None

        # CUST_ADDR, CUST_CITY, CUST_STATE, CUST_ZIP: Random address details
        cust_addr = fake.street_address()
        cust_city = fake.city()
        cust_state = fake.state_abbr()
        cust_zip = fake.zipcode()

        # CUST_PH_NO: Random phone number
        cust_ph_no = fake.phone_number()

        # CUST_EMAIL: Random email address
        cust_email = fake.email() if cust_typ == 'prsn' else fake.company_email()

        # CUST_TAX_ID and CUST_TAX_ID_TYP
        if cust_typ == 'prsn':
            cust_tax_id_typ = 'SSN'
            cust_tax_id = fake.ssn()
        else:
            cust_tax_id_typ = 'EIN'
            cust_tax_id = fake.ein()

        # Append the record
        customer_details.append([
            cust_id, cust_typ, cust_frst_nm, cust_lst_nm, cust_gender,
            cust_dob.strftime('%Y-%m-%d') if cust_dob else None, cust_dod,
            cust_addr, cust_city, cust_state, cust_zip,
            cust_ph_no, cust_email, cust_tax_id, cust_tax_id_typ
        ])

    # Convert to DataFrame
    return pd.DataFrame(customer_details, columns=[
        'CUST_ID', 'CUST_TYP', 'CUST_FRST_NM', 'CUST_LST_NM', 'CUST_GENDER',
        'CUST_DOB', 'CUST_DOD', 'CUST_ADDR', 'CUST_CITY', 'CUST_STATE', 'CUST_ZIP',
        'CUST_PH_NO', 'CUST_EMAIL', 'CUST_TAX_ID', 'CUST_TAX_ID_TYP'
    ])

# Generate the dataset
customer_details_df = generate_customer_details(num_customers)

# Save the dataset to a CSV file
customer_details_df.to_csv('data/CUSTOMER_DETAILS.csv', index=False)

print("CUSTOMER_DETAILS dataset generated and saved as 'data/CUSTOMER_DETAILS.csv'.")
