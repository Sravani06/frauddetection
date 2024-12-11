CREATE TABLE IF NOT EXISTS Claim_Details (
    CLAIM_ID INTEGER PRIMARY KEY AUTOINCREMENT,           -- Unique identifier for each claim
    CLAIM_NUMBER VARCHAR(20) UNIQUE,                     -- Unique claim number (CLMYYYYMMDDXXXX)
    CLAIM_OCCUR_DATE DATE NOT NULL,                      -- Date the claim occurred
    CLAIM_STATE VARCHAR(2) CHECK (CLAIM_STATE IN ('CA', 'VA', 'NY', 'TX', 'FL', 'WA', 'MA', 'NV', 'OH', 'MI', 'WV', 'NJ')),
    CLAIM_AMOUNT DECIMAL(10, 2) NOT NULL,                -- Amount of the claim

    POLICY_START_DATE DATE NOT NULL,                     -- Start date of the policy
    POLICY_END_DATE DATE NOT NULL,                       -- End date of the policy
    POLICY_RISK_LEVEL VARCHAR(10) CHECK (POLICY_RISK_LEVEL IN ('Low', 'Medium', 'High')),
    POLICY_CLAIM_LIMIT DECIMAL(10, 2) NOT NULL,          -- Maximum claim limit for the policy

    CLAIMANT_FIRST_NAME VARCHAR(50) NOT NULL,            -- Claimant's first name
    CLAIMANT_LAST_NAME VARCHAR(50) NOT NULL,             -- Claimant's last name
    CLAIMANT_STATE VARCHAR(2) CHECK (CLAIMANT_STATE IN ('CA', 'VA', 'NY', 'TX', 'FL', 'WA', 'MA', 'NV', 'OH', 'MI', 'WV', 'NJ')),
    CLAIMANT_INDUSTRY VARCHAR(50),                      -- Industry where the claimant works

    INSURED_FIRST_NAME VARCHAR(50) NOT NULL,             -- Insured's first name
    INSURED_LAST_NAME VARCHAR(50) NOT NULL,              -- Insured's last name
    INSURED_STATE VARCHAR(2) CHECK (INSURED_STATE IN ('CA', 'VA', 'NY', 'TX', 'FL', 'WA', 'MA', 'NV', 'OH', 'MI', 'WV', 'NJ')),
    INSURED_INDUSTRY VARCHAR(50),                       -- Industry of the insured

    MEDICAL_PROVIDER_FIRST_NAME VARCHAR(50) NOT NULL,    -- Medical provider's first name
    MEDICAL_PROVIDER_LAST_NAME VARCHAR(50) NOT NULL,     -- Medical provider's last name
    MEDICAL_PROVIDER_STATE VARCHAR(2) CHECK (MEDICAL_PROVIDER_STATE IN ('CA', 'VA', 'NY', 'TX', 'FL', 'WA', 'MA', 'NV', 'OH', 'MI', 'WV', 'NJ')),

    INJURY_BODY_PART VARCHAR(50) CHECK (INJURY_BODY_PART IN (
        'Head', 'Back', 'Arm', 'Leg', 'Shoulder', 'Hand', 'Foot',
        'Neck', 'Chest', 'Abdomen', 'Hip', 'Knee', 'Elbow', 'Ankle',
        'Wrist', 'Neck and Spine', 'Toes', 'Fingers', 'Teeth',
        'Ears', 'Eyes', 'Internal Organs', 'Pelvis', 'Groin'
    )),
    INJURY_TYPE VARCHAR(50) CHECK (INJURY_TYPE IN (
        'Fracture', 'Burn', 'Sprain', 'Cut', 'Bruise', 'Amputation',
        'Dislocation', 'Puncture', 'Contusion', 'Crush Injury', 'Tear',
        'Laceration', 'Concussion', 'Whiplash', 'Electric Shock',
        'Frostbite', 'Poisoning', 'Radiation Exposure', 'Chemical Exposure',
        'Nerve Damage', 'Soft Tissue Injury', 'Eye Injury', 'Hearing Loss'
    )),
    INJURY_SEVERITY VARCHAR(10) CHECK (INJURY_SEVERITY IN ('Low', 'Medium', 'High')),
    TREATMENT_REQUIRED VARCHAR(3) CHECK (TREATMENT_REQUIRED IN ('Yes', 'No')),
    DAYS_LOST INTEGER,                                   -- Number of days lost due to the injury
    PRESCRIBER_NOTES TEXT,                               -- Notes provided by the medical prescriber

    DATE_SUBMITTED DATE DEFAULT CURRENT_DATE            -- Date the claim was submitted
);
