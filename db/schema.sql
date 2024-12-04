CREATE TABLE IF NOT EXISTS policy_details (
    PLCY_NO TEXT PRIMARY KEY,       -- Policy number
    PLCY_STRT_DT DATE,              -- Policy start date
    PLCY_END_DT DATE                -- Policy end date
);

CREATE TABLE IF NOT EXISTS customer_details (
    CUST_ID INTEGER PRIMARY KEY,    -- Customer ID (numeric)
    CUST_TYP TEXT,                  -- Customer type: 'prsn' or 'busn'
    CUST_FRST_NM TEXT,              -- First name
    CUST_LST_NM TEXT,               -- Last name
    CUST_GENDER TEXT,               -- Gender
    CUST_DOB DATE,                  -- Date of birth
    CUST_DOD DATE,                  -- Date of death
    CUST_ADDR TEXT,                 -- Address
    CUST_CITY TEXT,                 -- City
    CUST_STATE TEXT,                -- State
    CUST_ZIP INTEGER,               -- Zip code
    CUST_PH_NO TEXT,                -- Phone number
    CUST_EMAIL TEXT,                -- Email address
    CUST_TAX_ID TEXT,               -- Tax ID
    CUST_TAX_ID_TYP TEXT            -- Tax ID type
);

CREATE TABLE IF NOT EXISTS claim_details (
    CLM_DTL_ID INTEGER PRIMARY KEY, -- Claim detail ID (numeric)
    CLM_NO INTEGER,                 -- Claim number
    PLCY_NO TEXT,                   -- Policy number (FK to policy_details)
    CLM_JUR_TYP_CD TEXT,            -- Jurisdiction type code
    CLM_RPT_DT DATE,                -- Claim reported date
    CLM_OCCR_DT DATE,               -- Claim occurrence date
    CLM_OCCR_ADDR TEXT,             -- Claim occurrence address
    CLM_OCCR_CITY TEXT,             -- Claim occurrence city
    CLM_OCCR_ZIP INTEGER,           -- Claim occurrence zip code
    CLM_OCCR_STATE TEXT,            -- Claim occurrence state
    CLM_TYP TEXT,                   -- Claim type: 'medical' or 'indemnity'
    CLM_AMT REAL,                   -- Claim amount
    FOREIGN KEY (PLCY_NO) REFERENCES policy_details (PLCY_NO)
);

CREATE TABLE IF NOT EXISTS claim_status (
    CLM_STS_ID INTEGER PRIMARY KEY, -- Claim status ID (numeric)
    CLM_DTL_ID INTEGER,             -- Claim detail ID (FK to claim_details)
    CLM_STS_CD TEXT,                -- Claim status code
    CLM_STS_START_DT DATE,          -- Claim status start date
    CLM_STS_END_DT DATE,            -- Claim status end date
    FOREIGN KEY (CLM_DTL_ID) REFERENCES claim_details (CLM_DTL_ID)
);

CREATE TABLE IF NOT EXISTS claim_participant (
    CLM_PTCP_ID INTEGER PRIMARY KEY, -- Claim participant ID (numeric)
    CLM_DTL_ID INTEGER,              -- Claim detail ID (FK to claim_details)
    CUST_ID INTEGER,                 -- Customer ID (FK to customer_details)
    PTCP_TYP TEXT,                   -- Participant type: 'clmt', 'insured', etc.
    FOREIGN KEY (CLM_DTL_ID) REFERENCES claim_details (CLM_DTL_ID),
    FOREIGN KEY (CUST_ID) REFERENCES customer_details (CUST_ID)
);

CREATE TABLE IF NOT EXISTS claim_additional_details (
    CLM_ID INTEGER PRIMARY KEY,     -- Claim ID (numeric, FK to claim_details)
    CLMT_HIRE_DT DATE,              -- Claimant hire date
    CLMT_JOB_TTL TEXT,              -- Job title
    CLMT_JOB_TYP TEXT,              -- Job type: 'fulltime' or 'parttime'
    CLMT_DISAB_BGN_DT DATE,         -- Disability start date
    CLMT_AVG_WKLY_WAGE REAL,        -- Average weekly wage
    WORK_LOC TEXT,                  -- Work location
    INDUSTRY TEXT,                  -- Industry
    FOREIGN KEY (CLM_ID) REFERENCES claim_details (CLM_DTL_ID)
);

CREATE TABLE IF NOT EXISTS payment_details (
    PAYMENT_ID INTEGER PRIMARY KEY, -- Payment ID (numeric)
    CLM_ID INTEGER,                 -- Claim ID (FK to claim_details)
    PAYMENT_DATE DATE,              -- Payment date
    PAYMENT_AMOUNT REAL,            -- Payment amount
    PAYMENT_STATUS TEXT,            -- Payment status
    PAYMENT_METHOD TEXT,            -- Payment method: 'check', 'wire transfer', etc.
    PAYMENT_TYP TEXT,               -- Payment type: 'medical' or 'indemnity'
    BNFT_TYP_CD TEXT,               -- Benefit type code
    FOREIGN KEY (CLM_ID) REFERENCES claim_details (CLM_DTL_ID)
);

CREATE TABLE IF NOT EXISTS injury_details (
    CLM_INJ_ID INTEGER PRIMARY KEY, -- Unique injury ID
    CLM_ID INTEGER,                 -- Claim ID (FK to claim_details)
    INJURY_POB TEXT,                -- Place of injury
    INJURY_SEVERITY TEXT,           -- Severity of injury
    INJURY_TYP_CD TEXT,             -- Injury type code
    PRESCRIBER_NOTES TEXT,          -- Notes from prescriber
    FOREIGN KEY (CLM_ID) REFERENCES claim_details (CLM_DTL_ID) ON DELETE CASCADE
);
