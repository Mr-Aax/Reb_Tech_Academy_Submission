import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Executive Payment Operations Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv(r"E:\CODING\Py\submission_02_reb_tech_academy\clean_dataset.csv")
    df['payment_date'] = pd.to_datetime(df['payment_date'])
    return df

df = load_data()

# 2. Interactive Slicers & Filters
st.sidebar.title("🔍 Interactive Dashboard Filters")
year_filter = st.sidebar.multiselect(
    "Select Year(s):",
    options=sorted(df['order_year'].dropna().unique()),
    default=sorted(df['order_year'].dropna().unique())
)
method_filter = st.sidebar.multiselect(
    "Select Payment Method:",
    options=sorted(df['payment_method'].unique()),
    default=sorted(df['payment_method'].unique())
)
status_filter = st.sidebar.multiselect(
    "Select Payment Status:",
    options=sorted(df['payment_status'].unique()),
    default=sorted(df['payment_status'].unique())
)

filtered_df = df[
    (df['order_year'].isin(year_filter)) &
    (df['payment_method'].isin(method_filter)) &
    (df['payment_status'].isin(status_filter))
]

# 3. Header & Executive KPI Scorecards
st.title("📊 Executive Payment Operations Dashboard")
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)
gross_revenue = filtered_df['amount_paid'].sum()
net_revenue = filtered_df['net_settlement_amount'].sum()
aov = filtered_df['amount_paid'].mean() if len(filtered_df) > 0 else 0
success_rate = (len(filtered_df[filtered_df['payment_status'] == 'Success']) / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
refunds = filtered_df['refund_amount'].sum()

col1.metric("Gross Revenue", f"₹{gross_revenue:,.0f}")
col2.metric("Net Revenue", f"₹{net_revenue:,.0f}")
col3.metric("Avg Order Value (AOV)", f"₹{aov:,.2f}")
col4.metric("Success Rate", f"{success_rate:.1f}%")
col5.metric("Total Refunds Issued", f"₹{refunds:,.0f}")

st.markdown("---")

# 4. Trendline & Channel Visualizations
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📈 Monthly Revenue & Net Settlement Trendline")
    monthly_trend = filtered_df.groupby(['order_year', 'order_month'])[['amount_paid', 'net_settlement_amount']].sum().reset_index()
    monthly_trend['Period'] = monthly_trend['order_year'].astype(str) + "-" + monthly_trend['order_month'].astype(str).str.zfill(2)
    fig_trend = px.area(
        monthly_trend.sort_values('Period'),
        x='Period',
        y=['amount_paid', 'net_settlement_amount'],
        color_discrete_sequence=['#1f77b4', '#2ca02c']
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("💳 Revenue Share by Channel")
    fig_pie = px.pie(
        filtered_df,
        names='payment_method',
        values='amount_paid',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 5. Status Breakdown & Net Settlement Explorer
c3, c4 = st.columns(2)

with c3:
    st.subheader("📊 Payment Status Distribution (%)")
    status_ct = pd.crosstab(filtered_df['payment_method'], filtered_df['payment_status'], normalize='index') * 100
    fig_bar = px.bar(status_ct.reset_index(), x='payment_method', y=status_ct.columns, barmode='stack')
    st.plotly_chart(fig_bar, use_container_width=True)

with c4:
    st.subheader("💰 Net Settlement Distribution")
    fig_box = px.box(
        filtered_df[filtered_df['net_settlement_amount'] > 0],
        x='payment_method',
        y='net_settlement_amount',
        log_y=True,
        color='payment_method'
    )
    st.plotly_chart(fig_box, use_container_width=True)

# 6. Detailed Table Drill-Down
st.markdown("---")
st.subheader("📋 Transaction Record Drill-Down")
st.dataframe(
    filtered_df[['payment_id', 'order_id', 'payment_date', 'payment_method',
                 'payment_status', 'amount_paid', 'net_settlement_amount',
                 'profitability_status']].head(100),
    use_container_width=True
)
