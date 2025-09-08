import streamlit as st
import pandas as pd

# Load the single-day efficiency dataset
df = pd.read_csv('boiler_efficiency_dashboard.csv')

st.title("Boiler Efficiency Summary")

# Display the entire data in a clean table
st.table(df)

# Highlight key metrics from the first (and only) row
st.markdown(f"### Efficiency: {df['Efficiency'].iloc[0]:.2f}%")
st.markdown(f"### Conversion Rate: {df['Conversion_Rate'].iloc[0]:.2f}")
st.markdown(f"### Boiler Yield: {df['Boiler_Yield'].iloc[0]:.2f}")

# Download button for the CSV file
with open('boiler_efficiency_dashboard.csv', 'r') as file:
    csv_data = file.read()

st.download_button(
    label="Download Efficiency Data as CSV",
    data=csv_data,
    file_name='boiler_efficiency.csv',
    mime='text/csv',
)
