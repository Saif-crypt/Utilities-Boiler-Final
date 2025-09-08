import streamlit as st
import pandas as pd

df = pd.read_csv('boiler_efficiency_dashboard.csv')

st.set_page_config(page_title="Boiler Efficiency Summary", layout="centered")
st.title("Boiler Efficiency Summary")

# Use column names as in your dataframe
# Replace these example column names with exact names from your df
key_metrics = ['Efficiency', 'Conversion_Rate', 'Boiler_Yield']

# Pick columns if present
if all(col in df.columns for col in key_metrics):
    row = df.iloc
    col1, col2, col3 = st.columns(3)
    col1.metric("Efficiency (%)", f"{row['Efficiency']:.2f}")
    col2.metric("Conversion Rate", f"{row['Conversion_Rate']:.2f}")
    col3.metric("Boiler Yield", f"{row['Boiler_Yield']:.2f}")
else:
    st.error("Key metric columns missing from file. Please check CSV column names.")

with st.expander("Show All Input Details"):
    st.dataframe(df)

with open('boiler_efficiency_dashboard.csv', 'r') as file:
    csv_data = file.read()
st.download_button(
    label="Download Efficiency Data as CSV",
    data=csv_data,
    file_name='boiler_efficiency.csv',
    mime='text/csv'
)
