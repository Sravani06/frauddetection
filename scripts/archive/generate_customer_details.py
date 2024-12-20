import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, datetime, timedelta

# Initialize Faker
fake = Faker()
np.random.seed(42)

# Number of customer records to generate
num_customers = 6000  # 2000 medical providers, 2000 insureds, 2000 injured workers

# Function to generate CUSTOMER_DETAILS dataset
def generate_customer_details(num_records):
    customer_details = []

    for i in range(1, num_records + 1):
        # CUST_ID: Unique ID
        cust_id = i

        # CUST_TYP: Assign 'prsn' for injured workers, 'busn' for insureds and medical providers
        if i <= 2000:  # First 2000 are medical providers
            cust_typ = 'busn'
            cust_role = 'Medical Provider'
        elif i <= 4000:  # Next 2000 are insureds
            cust_typ = 'busn'
            cust_role = 'Insured'
        else:  # Remaining 2000 are injured workers
            cust_typ = 'prsn'
            cust_role = 'Injured Worker'

        # CUST_FRST_NM and CUST_LST_NM: Random first and last names for individuals, company name for businesses
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

        # CUST_AGE: Age calculated from DOB
        cust_age = None
        if cust_dob:
            cust_age = date.today().year - cust_dob.year

        # CUST_DOD: Date of death for some customers over the age of 50
        cust_dod = None
        if cust_typ == 'prsn' and cust_age is not None and cust_age >= 50:
            # Randomly decide if this customer is deceased (only 20% chance for 50+ age customers)
            if np.random.rand() < 0.2:  # 20% chance
                # Generate a death date at least 50 years after the DOB
                min_death_year = cust_dob.year + 50
                max_death_year = min(date.today().year, cust_dob.year + 80)  # To avoid future dates

                # Check for valid min_death_year and max_death_year range
                if min_death_year < max_death_year:
                    try:
                        cust_dod = fake.date_between(start_date=f'{min_death_year}-01-01', end_date=f'{max_death_year}-12-31')
                    except Exception as e:
                        print(f"⚠️ Skipping CUST_DOD for CUST_ID={cust_id} due to invalid date range ({min_death_year} to {max_death_year}): {e}")

        # CUST_ADDR, CUST_CITY, CUST_STATE, CUST_ZIP: Random address details
        states = ['CA', 'NV', 'FL', 'VA', 'WV', 'MI', 'OH', 'NY', 'NJ']
        cust_addr = fake.street_address()
        cust_city = fake.city()
        cust_state = np.random.choice(states)
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

        # Append the record to the list
        customer_details.append([
            cust_id, cust_typ, cust_frst_nm, cust_lst_nm, cust_gender,
            cust_dob.strftime('%Y-%m-%d') if cust_dob else None,
            cust_dod.strftime('%Y-%m-%d') if cust_dod else None,  # CUST_DOD
            cust_age,  # CUST_AGE
            cust_addr, cust_city, cust_state, cust_zip,
            cust_ph_no, cust_email, cust_tax_id, cust_tax_id_typ
        ])

    # Convert to DataFrame
    return pd.DataFrame(customer_details, columns=[
        'CUST_ID', 'CUST_TYP', 'CUST_FRST_NM', 'CUST_LST_NM', 'CUST_GENDER',
        'CUST_DOB', 'CUST_DOD', 'CUST_AGE',
        'CUST_ADDR', 'CUST_CITY', 'CUST_STATE', 'CUST_ZIP',
        'CUST_PH_NO', 'CUST_EMAIL', 'CUST_TAX_ID', 'CUST_TAX_ID_TYP'
    ])

# Generate the dataset
customer_details_df = generate_customer_details(num_customers)

# Save the dataset to a CSV file
customer_details_df.to_csv('data/CUSTOMER_DETAILS.csv', index=False)

print("✅ CUSTOMER_DETAILS dataset generated and saved with CUST_DOD as 'data/CUSTOMER_DETAILS.csv'.")
