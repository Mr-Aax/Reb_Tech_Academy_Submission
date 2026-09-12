import pandas as pd
import numpy as np

# 1. Load raw messy dataset into Pandas
df_raw = pd.read_csv(r"E:\Intern\My submissions\Submission 03\raw_messy_created_dataset.csv")


print("=" * 70)
print("                  RAW DATASET OVERVIEW                  ")
print(f"Total Rows: {len(df_raw):,}")
print(f"Total Columns: {len(df_raw.columns)}")
print("=" * 70)

# Audit missing values and duplicates
print("\n                  MISSING VALUE AUDIT                  ")
print(df_raw.isnull().sum())
print("\n" + "*" * 70)
print(f"Exact Duplicate Rows: {df_raw.duplicated().sum():,}")
print(f"Duplicate Payment IDs: {df_raw['payment_id'].duplicated().sum():,}")

# 2. Create a working copy for cleaning
df_clean = df_raw.copy()

# Step 1: Handle Missing & Duplicate Primary Keys
df_clean = df_clean.dropna(subset=['payment_id'])
df_clean = df_clean.drop_duplicates(subset=['payment_id'], keep='first')

# Step 2: Impute Missing Order IDs
df_clean['order_id'] = df_clean['order_id'].fillna('ORD_UNKNOWN')

# Step 3: Handle Payment Dates & Parse to Datetime
df_clean['payment_date'] = pd.to_datetime(df_clean['payment_date'], errors='coerce')
df_clean['payment_date'] = df_clean['payment_date'].ffill().bfill()

# Step 4: Clean & Impute Categorical Columns
df_clean['payment_method'] = df_clean['payment_method'].fillna('Unknown').str.strip().str.title()
df_clean['payment_status'] = df_clean['payment_status'].fillna('Pending').str.strip().str.title()

# Step 5: Convert and Impute Numerical Fields
for col in ['amount_paid', 'transaction_fee', 'refund_amount']:
    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

median_amount = df_clean['amount_paid'].median()
df_clean['amount_paid'] = df_clean['amount_paid'].fillna(median_amount)
df_clean['transaction_fee'] = df_clean['transaction_fee'].fillna(0.0)
df_clean['refund_amount'] = df_clean['refund_amount'].fillna(0.0)

print("=" * 70)
print("\n                  POST-CLEANING AUDIT                  ")
print(f"Clean Records Retained: {len(df_clean):,}")
print("Remaining Missing Values:")
print(df_clean.isnull().sum())

# 3. Create an Excel Workbook with Raw, Clean, and Audit sheets
audit_summary = pd.DataFrame({
    'Metric': [
        'Total Raw Records',
        'Missing Primary Key (payment_id)',
        'Duplicate Records Removed',
        'Missing Dates Fixed',
        'Missing Methods Imputed',
        'Missing Status Imputed',
        'Missing Amounts Imputed',
        'Final Clean Records'
    ],
    'Count': [
        len(df_raw),
        df_raw['payment_id'].isnull().sum(),
        df_raw['payment_id'].duplicated().sum(),
        df_raw['payment_date'].isnull().sum(),
        df_raw['payment_method'].isnull().sum(),
        df_raw['payment_status'].isnull().sum(),
        df_raw['amount_paid'].isnull().sum(),
        len(df_clean)
    ]
})

with pd.ExcelWriter('Data_Cleaning_Report_Task3.xlsx', engine='openpyxl') as writer:
    df_raw.to_excel(writer, sheet_name='Raw Messy Data', index=False)
    df_clean.to_excel(writer, sheet_name='Clean Standardized Data', index=False)
    audit_summary.to_excel(writer, sheet_name='Data Audit Summary', index=False)

print("\n"+"*" * 70)
print("Excel export complete: 'Data_Cleaning_Report_Task3.xlsx'")

# 4. Feature Engineering
df_clean['order_month'] = df_clean['payment_date'].dt.month
df_clean['order_month_name'] = df_clean['payment_date'].dt.strftime('%B')
df_clean['order_year'] = df_clean['payment_date'].dt.year
df_clean['quarter'] = df_clean['payment_date'].dt.to_period('Q').astype(str)

df_clean['net_settlement_amount'] = df_clean['amount_paid'] - df_clean['transaction_fee'] - df_clean['refund_amount']
df_clean['retention_margin_pct'] = np.where(
    df_clean['amount_paid'] > 0,
    (df_clean['net_settlement_amount'] / df_clean['amount_paid']) * 100,
    0.0
)
df_clean['profitability_status'] = np.where(
    df_clean['net_settlement_amount'] > 0, 'Profitable',
    np.where(df_clean['net_settlement_amount'] == 0, 'Break-Even', 'Loss')
)

print("=" * 110)
print("\n                                      FEATURE ENGINEERING COMPLETE                                      ")
print(df_clean[['payment_id', 'order_month_name', 'order_year',
                'net_settlement_amount', 'retention_margin_pct',
                'profitability_status']].head())

# 5. Final Export to CSV
df_clean.to_csv('clean_dataset.csv', index=False)
print("\n"+"*" * 110)
print("Assignment Step Completed: Exported clean_dataset.csv")
print("=" * 110)
