import streamlit as st
import pandas as pd

df = pd.read_csv('boiler_efficiency_dashboard.csv')

st.set_page_config(page_title="Boiler Efficiency Summary", layout="centered")

st.title("Boiler Efficiency Summary")

# Extract the first row (for single day)
row = df.iloc

# Display key metrics in columns for better visibility
col1, col2, col3 = st.columns(3)

col1.metric("Efficiency (%)", f"{row['Efficiency']:.2f}")
col2.metric("Conversion Rate", f"{row['Conversion_Rate']:.2f}")
col3.metric("Boiler Yield", f"{row['Boiler_Yield']:.2f}")

# More primary details (can expand as needed)
with st.expander("Show All Input Details"):
    st.write(df)

# CSV Download button (as before)
with open('boiler_efficiency_dashboard.csv', 'r') as file:
    csv_data = file.read()

st.download_button(
    label="Download Efficiency Data as CSV",
    data=csv_data,
    file_name='boiler_efficiency.csv',
    mime='text/csv'
)

st.markdown("""
_If you want to visualize more days, upload or merge daily records together!_
""")
