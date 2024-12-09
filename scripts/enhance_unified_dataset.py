import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

# Load the unified dataset
print("Loading unified dataset...")
df = pd.read_csv('data/unified_dataset.csv')

# 1. DAYS_TO_REPORT: Calculate days from occurrence to report date
print("Calculating days to report...")
df['DAYS_TO_REPORT'] = (pd.to_datetime(df['CLM_RPT_DT']) - pd.to_datetime(df['CLM_OCCR_DT'])).dt.days

# 2. OCCURRED_ON_WEEKEND: Check if the occurrence date was on a weekend
print("Flagging claims that occurred on a weekend...")
df['OCCURRED_ON_WEEKEND'] = pd.to_datetime(df['CLM_OCCR_DT']).dt.dayofweek.isin([5, 6]).astype(int)

# 3. PENDING_180_DAYS: Check if the claim is pending for over 180 days
print("Flagging claims pending for over 180 days...")
df['PENDING_180_DAYS'] = ((pd.to_datetime('today') - pd.to_datetime(df['CLM_STS_START_DT'], errors='coerce')).dt.days > 180).astype(int)

# 5. CUSTOMER_TOTAL_CLAIMS: Count total claims filed by each customer
print("Counting total claims filed by each customer...")
df['CUSTOMER_TOTAL_CLAIMS'] = df.groupby('CUST_ID')['CLM_DTL_ID'].transform('count')

# 6. OUT_OF_JURISDICTION: Check if the claim was filed outside of the customer's home state
print("Flagging out-of-jurisdiction claims...")
df['OUT_OF_JURISDICTION'] = (df['CLM_OCCR_STATE'] != df['CUST_STATE']).astype(int)

# 7. OCCURRED_ON_HOLIDAY: Check if the occurrence date was on a public holiday
print("Flagging claims that occurred on public holidays...")
calendar = USFederalHolidayCalendar()
holidays = calendar.holidays(start=df['CLM_OCCR_DT'].min(), end=df['CLM_OCCR_DT'].max())
df['OCCURRED_ON_HOLIDAY'] = pd.to_datetime(df['CLM_OCCR_DT']).isin(holidays).astype(int)

# 8. MULTIPLE_INJURIES: Flag claims with multiple injuries
print("Flagging claims with multiple injuries...")
df['MULTIPLE_INJURIES'] = (df['NUM_INJURIES'] > 2).astype(int)

# 9. DECLINED_WITH_PAYMENTS: Flag declined claims where payments were still made
print("Flagging declined claims with payments...")
df['DECLINED_WITH_PAYMENTS'] = ((df['FINAL_STATUS'] == 'Declined') & (df['TOTAL_PAYMENT_AMOUNT'] > 0)).astype(int)

# 11. MAXIMUM_POLICY_AMOUNT_EXCEEDED: Check if the claim amount exceeds the policy's maximum coverage
print("Flagging claims where policy maximum coverage is exceeded...")
df['MAXIMUM_POLICY_AMOUNT_EXCEEDED'] = (df['CLM_AMT'] > df['CLAIM_LIMIT']).astype(int)

# 14. CUSTOMER_WITH_MULTIPLE_JURISDICTIONS: Flag customers filing claims in multiple states
print("Flagging customers with multiple jurisdiction claims...")
df['CUSTOMER_WITH_MULTIPLE_JURISDICTIONS'] = df.groupby('CUST_ID')['CLM_OCCR_STATE'].transform('nunique') > 1

# 18. LONG_PENDING_CLAIMS: Flag claims pending for more than 180 days
print("Flagging long-pending claims...")
df['LONG_PENDING_CLAIMS'] = ((pd.to_datetime('today') - pd.to_datetime(df['CLM_STS_START_DT'], errors='coerce')).dt.days > 180).astype(int)

# 20. POLICY_PREMIUM_TOO_LOW: Flag if policy premium is unusually low for the claim amount
print("Flagging claims with low policy premiums for high claim amounts...")
df['POLICY_PREMIUM_TOO_LOW'] = (df['PREMIUM_AMT'] < df['CLM_AMT'] * 0.05).astype(int)

# 22. CUSTOMER_WITH_HIGH_AGE: Flag if customer is 70+ years old
print("Flagging high-age customers...")
df['CUSTOMER_WITH_HIGH_AGE'] = (df['CUST_AGE'] > 70).astype(int)

# 23. CUSTOMER_WITH_LOW_AGE: Flag if customer is under 18
print("Flagging low-age customers...")
df['CUSTOMER_WITH_LOW_AGE'] = (df['CUST_AGE'] < 18).astype(int)

# 25. SUPERVISOR_NOT_LISTED: Flag if no supervisor is listed
print("Flagging claims with no listed supervisor...")
df['SUPERVISOR_NOT_LISTED'] = df['SUPERVISOR_NAME'].isnull().astype(int)

# 29. CLAIM_BEFORE_POLICY_EFFECTIVE: Flag claims that occurred before policy start date
print("Flagging claims that occurred before the policy start date...")
df['CLAIM_BEFORE_POLICY_EFFECTIVE'] = (pd.to_datetime(df['CLM_OCCR_DT']) < pd.to_datetime(df['PLCY_STRT_DT'])).astype(int)

# 30. INJURY_REPORTED_AFTER_30_DAYS: Flag if the injury was reported more than 30 days after occurrence
print("Flagging injuries reported after 30 days of occurrence...")
df['INJURY_REPORTED_AFTER_30_DAYS'] = (df['DAYS_TO_REPORT'] > 30).astype(int)

# 37. HIGH_PAYMENT_AMOUNT_RELATIVE_TO_CLAIM: Flag if any payment amount is unusually high
print("Flagging payments that are unusually high relative to claim amount...")
df['HIGH_PAYMENT_AMOUNT_RELATIVE_TO_CLAIM'] = (df['TOTAL_PAYMENT_AMOUNT'] > (df['CLM_AMT'] * 1.2)).astype(int)

# 38. MULTIPLE_DECLINED_STATUS_UPDATES: Flag if there are multiple "Declined" status updates
print("Flagging multiple 'Declined' status updates for a single claim...")
df['MULTIPLE_DECLINED_STATUS_UPDATES'] = df.groupby('CLM_DTL_ID')['CLM_STS_CD'].transform(lambda x: (x == 'Declined').sum()) > 1

# 40. MULTIPLE_CLAIMS_FROM_SAME_ADDRESS: Flag multiple claims originating from the same address
print("Flagging multiple claims from the same address...")
df['MULTIPLE_CLAIMS_FROM_SAME_ADDRESS'] = df.groupby('CLM_OCCR_ADDR')['CLM_DTL_ID'].transform('count') > 3

# 43. INJURY_NOT_WORK_RELATED: Flag claims where the injury doesn't match the work description
print("Flagging injuries that are not work-related...")
df['INJURY_NOT_WORK_RELATED'] = df.apply(
    lambda x: 1 if 'Office' in str(x['CLMT_JOB_TTL']) and 'Fracture' in str(x['INJURY_TYP_CD']) else 0,
    axis=1
)

# Final cleanup of NaN and NULLs
print("Cleaning up NaN values...")
df.fillna(0, inplace=True)

# Export the final enhanced unified dataset
print("Exporting enhanced unified dataset to 'data/unified_dataset_enhanced.csv'...")
df.to_csv('data/unified_dataset_enhanced.csv', index=False)

print(f"Enhanced unified dataset successfully saved with {df.shape[0]} rows and {df.shape[1]} columns.")
