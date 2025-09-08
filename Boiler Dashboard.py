import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Boiler Efficiency Dashboard", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv('boiler_efficiency_dashboard.csv', parse_dates=['Date'])
    return df

df = load_data()

st.title("Boiler Efficiency Monitoring Dashboard")

# Date filter
min_date, max_date = df['Date'].min(), df['Date'].max()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Filter data by selected range
filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

# Show basic metrics
st.header("Key Metrics Summary")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Average Efficiency (%)", f"{filtered_df['Efficiency'].mean():.2f}")
col2.metric("Average Conversion Rate", f"{filtered_df['Conversion_Rate'].mean():.2f}")
col3.metric("Average Boiler Yield", f"{filtered_df['Boiler_Yield'].mean():.2f}")
col4.metric("Average Adjusted NG Consumption", f"{filtered_df['Adjusted_NG_Consumption'].mean():.2f}")

# Display raw data expandable
with st.expander("Show Data Table"):
    st.dataframe(filtered_df)

# Plot efficiency over time
st.header("Efficiency and Key Parameters Over Time")
fig, ax1 = plt.subplots(figsize=(12, 5))

ax1.plot(filtered_df['Date'], filtered_df['Efficiency'], color='tab:blue', label='Efficiency (%)')
ax1.set_xlabel('Date')
ax1.set_ylabel('Efficiency (%)', color='tab:blue')
ax1.tick_params(axis='y', labelcolor='tab:blue')

ax2 = ax1.twinx()
ax2.plot(filtered_df['Date'], filtered_df['boiler_steam_tons'], color='tab:green', label='Steam Tons')
ax2.set_ylabel('Steam Tons', color='tab:green')
ax2.tick_params(axis='y', labelcolor='tab:green')

fig.legend(loc='upper right')
st.pyplot(fig)

# Feature correlation selection
st.header("Feature Correlations with Efficiency")
feature = st.selectbox("Select Feature", options=[
    'ng_skid_converted', 'ng_skid_unconverted', 'ng_meter_m3',
    'boiler_steam_tons', 'Feed_Water_Temp_C_mean', 'NG_CV_kcal_per_Nm3_mean'
])

st.line_chart(data=filtered_df.set_index('Date')[[feature, 'Efficiency']])

st.markdown("""
---
Data Courtesy: Boiler plant sensors and daily operational measurements.
""")
