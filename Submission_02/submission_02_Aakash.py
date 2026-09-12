import pandas as pd
import numpy as np
import io, sys
from fpdf import FPDF

# Load raw dataset
df = pd.read_csv(r"E:\CODING\Py\submission_02_reb_tech_academy\retail-orders-raw.csv")

# Step 1: Capture output
buffer = io.StringIO()
sys.stdout = buffer

print("=" * 70)
print("                  DATA QUALITY PROFILING REPORT                  ")
print("=" * 70)

# 1. COMPLETENESS CHECK
print("\n[1] COMPLETENESS CHECK")
null_counts = df.isnull().sum()
missing_fields = null_counts[null_counts > 0]
if len(missing_fields) > 0:
    for col, count in missing_fields.items():
        pct = (count / len(df)) * 100
        print(f"  \n Field '{col}': {count} missing value(s) ({pct:.1f}%)")
else:
    print("   All mandatory fields are 100% complete.")
print("\n" + "*" * 70)

# 2. UNIQUENESS CHECK
print("\n[2] UNIQUENESS CHECK")
dup_count = df.duplicated(subset=['order_id']).sum()
if dup_count > 0:
    print(f"  \n Duplicate order IDs detected: {dup_count} duplicate record(s).")
    print(df[df.duplicated(subset=['order_id'], keep=False)][['order_id', 'order_date', 'customer_segment']])
else:
    print("   All order_id records are unique.")
print("\n" + "*" * 70)

# 3. VALIDITY & FORMAT CHECK
print("\n[3] VALIDITY & RANGE CHECKS")


# Quantity Check
print("\n [3.1] QUANTITY CHECK")
for idx, val in df['quantity'].items():
    try:
        q_val = float(val)
        if q_val <= 0:
            print(f"  \n Row {idx} (Order {df.loc[idx, 'order_id']}): Invalid quantity = {val} (Must be > 0)")
    except ValueError:
        print(f"  \n Row {idx} (Order {df.loc[idx, 'order_id']}): Non-numeric quantity = '{val}'")
print("\n" + "-" * 70)

# Discount Check
print("\n [3.2] DISCOUNT CHECK")
for idx, val in df['discount_pct'].items():
    if pd.notnull(val) and (val < 0 or val > 100):
        print(f"  \n Row {idx} (Order {df.loc[idx, 'order_id']}): Invalid discount = {val}% (Allowed: 0-100%)")
print("\n" + "-" * 70)

# Date Format Check
print("\n [3.3] DATE FORMAT CHECK")
for idx, val in df['order_date'].items():
    if pd.notnull(val):
        try:
            pd.to_datetime(val, format='%Y-%m-%d', errors='raise')
        except Exception:
            print(f"  \n Row {idx} (Order {df.loc[idx, 'order_id']}): Non-ISO date format = '{val}'")

print("\n" + "=" * 70)

# Restore normal printing
sys.stdout = sys.__stdout__
output_text = buffer.getvalue()

# Restore normal printing
sys.stdout = sys.__stdout__
output_text = buffer.getvalue()   # now buffer exists, so no error

pdf = FPDF()
pdf.add_page()

# Use the full path if needed
pdf.add_font("DejaVu", "", r"E:\CODING\Py\submission_02_reb_tech_academy\DejaVuSans.ttf")
pdf.set_font("DejaVu", size=10)

# Add code
with open(__file__, "r", encoding="utf-8") as f:
    code_text = f.read()
pdf.multi_cell(0, 5, "Python Code:\n\n" + code_text)

# Add output
pdf.multi_cell(0, 5, "\nOutput:\n\n" + output_text)

pdf.output("data_quality_report.pdf")
