  SELECT i.PLCY_NO, i.PLCY_STRT_DT, i.PLCY_END_DT, i.RISK_LEVEL, i.PLCY_CLAIM_LIMIT,
               p.CUST_TAX_ID, p.CUST_STATE, p.CUST_FRST_NM, i.BUSINESS_TYPE
        FROM policy_details i
        JOIN claim_details s on s.plcy_no = i.PLCY_NO
        JOIN customer_details p ON s.CUST_ID_INSURED = p.CUST_ID


  SELECT CUST_FRST_NM, CUST_LST_NM, CUST_STATE
        FROM customer_details
        WHERE CUST_TAX_ID = 688438108


  select * from claim_details where PLCY_NO = 'COF2576353';

select * from customer_details where cust_id == '3334'

select * from Claim_Details_submission

alter table Claim_Details_submission add column INSURED_STATE