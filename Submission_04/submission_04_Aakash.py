import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from IPython.display import display

# 1. Load dataset
df = pd.read_csv("E:\\CODING\\Py\\submission_02_reb_tech_academy\\clean_dataset.csv")

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 11})

# STEP 1: SUMMARY DESCRIPTIVE STATISTICS
num_cols = ['amount_paid', 'transaction_fee', 'refund_amount',
            'net_settlement_amount', 'retention_margin_pct']

desc_stats = df[num_cols].describe().T
desc_stats['median'] = df[num_cols].median()
desc_stats['skewness'] = df[num_cols].skew()

print("=" * 110)
print("\nSUMMARY DESCRIPTIVE STATISTICS\n")
display(desc_stats[['count', 'mean', 'std', 'min', '25%', 'median',
                    '75%', 'max', 'skewness']])

# STEP 2: HYPOTHESIS TESTING
contingency = pd.crosstab(df['payment_method'], df['payment_status'])
chi2, p_val_h1, dof, _ = stats.chi2_contingency(contingency)

succ_df = df[df['payment_status'] == 'Success']
r_val, p_val_h2 = stats.pearsonr(succ_df['amount_paid'], succ_df['transaction_fee'])

refunded_df = df[df['refund_amount'] > 0]
refund_groups = [group['refund_amount'].values for _, group in refunded_df.groupby('payment_method')]
kw_stat, p_val_h3 = stats.kruskal(*refund_groups)

print("=" * 110)
print("\nSTATISTICAL HYPOTHESIS RESULTS\n")
print(f"H1 (Payment Method vs Status) : Chi2 = {chi2:.2f}, p-value = {p_val_h1:.4e} -> "
      f"{'Reject H0' if p_val_h1 < 0.05 else 'Fail to Reject H0'}")
print(f"H2 (Amount Paid vs Fee)       : Pearson r = {r_val:.4f}, p-value = {p_val_h2:.4e} -> "
      f"{'Reject H0' if p_val_h2 < 0.05 else 'Fail to Reject H0'}")
print(f"H3 (Refund Amount by Method)  : Kruskal-Wallis H = {kw_stat:.4f}, p-value = {p_val_h3:.4f} -> "
      f"{'Reject H0' if p_val_h3 < 0.05 else 'Fail to Reject H0'}")

# STEP 3: VISUALIZATIONS
# Page 1
fig1, axes1 = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
sns.histplot(df['amount_paid'], bins=50, kde=True, ax=axes1[0], color='#1f77b4')
axes1[0].set_yscale('log'); axes1[0].set_title('A. Distribution of Amount Paid (Log-Scaled)', fontweight='bold')
axes1[0].set_xlabel('Amount Paid (₹)'); axes1[0].set_ylabel('Count')

status_pct = pd.crosstab(df['payment_method'], df['payment_status'], normalize='index') * 100
status_pct.plot(kind='bar', stacked=True, ax=axes1[1], colormap='viridis', legend=False)
axes1[1].set_title('B. Payment Status Breakdown by Method', fontweight='bold')
axes1[1].set_ylabel('Percentage (%)'); axes1[1].set_ylim(0, 100)
axes1[1].tick_params(axis='x', rotation=45)
axes1[1].legend(title='Status', bbox_to_anchor=(1.05, 1), loc='upper left')

fig1.savefig("page1_plots.png", dpi=300, bbox_inches='tight')
plt.close(fig1)

# Page 2
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
sns.heatmap(df[num_cols].corr(), annot=True, fmt=".2f", cmap='coolwarm', ax=axes2[0])
axes2[0].set_title('C. Correlation Heatmap (Financial Features)', fontweight='bold')

sns.boxplot(x='payment_method', y='net_settlement_amount',
            data=df[df['net_settlement_amount'] > 0],
            ax=axes2[1], palette='Set2', hue=None)
axes2[1].set_yscale('log'); axes2[1].tick_params(axis='x', rotation=45)
axes2[1].set_title('D. Net Settlement Amount Distribution by Method', fontweight='bold')
axes2[1].set_ylabel('Net Settlement Amount (₹)')

fig2.savefig("page2_plots.png", dpi=300, bbox_inches='tight')
plt.close(fig2)

# STEP 4: EXPORT RESULTS TO EXCEL WITH EMBEDDED IMAGES
hypothesis_results = pd.DataFrame({
    'Hypothesis': [
        'Payment Method vs Status',
        'Amount Paid vs Fee',
        'Refund Amount by Method'
    ],
    'Test Statistic': [chi2, r_val, kw_stat],
    'p-value': [p_val_h1, p_val_h2, p_val_h3],
    'Decision': [
        'Reject H0' if p_val_h1 < 0.05 else 'Fail to Reject H0',
        'Reject H0' if p_val_h2 < 0.05 else 'Fail to Reject H0',
        'Reject H0' if p_val_h3 < 0.05 else 'Fail to Reject H0'
    ]
})

# Use XlsxWriter to embed images
with pd.ExcelWriter("submission_04_result.xlsx", engine="xlsxwriter") as writer:
    desc_stats.to_excel(writer, sheet_name="Descriptive Statistics")
    hypothesis_results.to_excel(writer, sheet_name="Hypothesis Results")

    workbook = writer.book
    # Add images into a separate sheet
    worksheet = workbook.add_worksheet("Plots")
    worksheet.insert_image("B2", "page1_plots.png")
    worksheet.insert_image("B22", "page2_plots.png")

print("\nExcel file 'submission_04_result.xlsx' has been generated successfully with embedded plots.")
