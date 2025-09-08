import streamlit as st
import pandas as pd

df = pd.read_csv('boiler_efficiency_dashboard.csv')

st.set_page_config(page_title="Boiler Efficiency Summary", layout="centered")
st.title("Boiler Efficiency Summary")

# Correct check for non-empty DataFrame
if len(df) > 0:  # or df.shape > 0
    row = df.iloc  # Extract the first row safely
    col1, col2, col3 = st.columns(3)

    col1.metric("Efficiency (%)", f"{row['Efficiency']:.2f}")
    col2.metric("Conversion Rate", f"{row['Conversion_Rate']:.2f}")
    col3.metric("Boiler Yield", f"{row['Boiler_Yield']:.2f}")

    with st.expander("Show All Input Details"):
        st.write(df)

    with open('boiler_efficiency_dashboard.csv', 'r') as file:
        csv_data = file.read()

    st.download_button(
        label="Download Efficiency Data as CSV",
        data=csv_data,
        file_name='boiler_efficiency.csv',
        mime='text/csv'
    )
else:
    st.error("No data found in CSV.")
