import streamlit as st
import pandas as pd

df = pd.read_csv('boiler_efficiency_dashboard.csv')

st.set_page_config(page_title="Boiler Efficiency Summary", layout="centered")
st.title("Boiler Efficiency Summary")

# Print all columns for debugging
st.write("Columns:", df.columns.tolist())

if not df.empty:
    row = df.iloc
    # Change these names as needed based on actual columns available
    efficiency_col = [col for col in df.columns if 'efficiency' in col.lower()]
    conversion_col = [col for col in df.columns if 'conversion' in col.lower()]
    yield_col = [col for col in df.columns if 'yield' in col.lower()]

    col1, col2, col3 = st.columns(3)
    col1.metric("Efficiency", f"{row[efficiency_col]:.2f}")
    col2.metric("Conversion Rate", f"{row[conversion_col]:.2f}")
    col3.metric("Boiler Yield", f"{row[yield_col]:.2f}")

    with st.expander("Show All Input Details"):
        st.dataframe(df)
else:
    st.error("No data found in CSV.")
