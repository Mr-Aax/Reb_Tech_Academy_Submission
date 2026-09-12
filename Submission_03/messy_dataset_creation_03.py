import pandas as pd
import numpy as np

# Load the original dataset
df = pd.read_csv(r"E:\Intern\My submissions\Submission 03\payments_india.csv")

# --- 1. Corrupt in place (missing values) ---
df.loc[df.sample(frac=0.10, random_state=1).index, 'payment_id'] = np.nan
df.loc[df.sample(frac=0.02, random_state=2).index, 'order_id'] = np.nan
df.loc[df.sample(frac=0.20, random_state=3).index, 'payment_date'] = np.nan
df.loc[df.sample(frac=0.40, random_state=4).index, 'payment_method'] = np.nan
df.loc[df.sample(frac=0.12, random_state=5).index, 'payment_status'] = np.nan
df.loc[df.sample(frac=0.12, random_state=6).index, 'amount_paid'] = np.nan
df.loc[df.sample(frac=0.08, random_state=7).index, 'transaction_fee'] = np.nan
df.loc[df.sample(frac=0.20, random_state=8).index, 'refund_amount'] = np.nan

# --- 2. Conditional row additions (duplications) ---
# Payment ID duplication (3%)
payment_id_dupes = df.sample(frac=0.03, random_state=9)
df = pd.concat([df, payment_id_dupes], ignore_index=True)

# Order ID duplication (12%)
order_id_dupes = df.sample(frac=0.12, random_state=10)
df = pd.concat([df, order_id_dupes], ignore_index=True)

# --- 3. Report ---
print(f"Final Messy Dataset Shape: {df.shape}")
print("Missing Values:\n", df.isnull().sum())
print("Duplicate Rows Count:", df.duplicated().sum())

# --- 4. Save ---
df.to_csv(r"E:\Intern\My submissions\Submission 03\messy_dataset_custom.csv", index=False)
print("Custom messy dataset saved as messy_dataset_custom.csv")
