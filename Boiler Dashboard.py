import streamlit as st
import pandas as pd

df = pd.read_csv('boiler_efficiency_dashboard.csv')

st.set_page_config(page_title="Boiler Efficiency Summary", layout="centered")
st.title("Boiler Efficiency Summary")

# Show columns for debugging
st.write("Columns:", df.columns.tolist())
st.write("First row data:", df.head(1))

if len(df) > 0:
    # It's safest to use .iloc, check if columns exist
    try:
        efficiency_value = df.iloc[df.columns.get_loc('Efficiency')]
        conversion_rate_value = df.iloc[df.columns.get_loc('Conversion_Rate')]
        boiler_yield_value = df.iloc[df.columns.get_loc('Boiler_Yield')]
    except Exception as e:
        st.error(f"Column indexing error: {e}")
        st.stop()
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Efficiency (%)", f"{efficiency_value:.2f}")
    col2.metric("Conversion Rate", f"{conversion_rate_value:.2f}")
    col3.metric("Boiler Yield", f"{boiler_yield_value:.2f}")

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
