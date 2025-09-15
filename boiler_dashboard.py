import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Boiler Dashboard",
    page_icon="🔥",
    layout="wide"
)

# App title
st.title("🔥 Boiler Dashboard")

# Generate sample data if needed
@st.cache_data
def generate_sample_data():
    dates = pd.date_range(start="2025-09-01", end="2025-10-03")
    data = {
        "Date": dates,
        "Total_Fuel_Corrected": np.random.uniform(100, 500, len(dates)),
        "Efficiency_X": np.random.uniform(70, 95, len(dates)),
        "Temperature": np.random.uniform(60, 120, len(dates)),
        "Pressure": np.random.uniform(10, 50, len(dates))
    }
    return pd.DataFrame(data)

# Main app function
def main():
    # Sidebar for filters and actions
    with st.sidebar:
        st.header("Date Range Filter")
        st.write("Select date range:")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start", value=datetime(2025, 9, 1))
        with col2:
            end_date = st.date_input("End", value=datetime(2025, 10, 3))
        
        st.divider()
        
        st.header("Quick Actions")
        if st.button("🔄 Refresh Data"):
            st.rerun()
            
        if st.button("📊 Download Report"):
            st.success("Report download initiated!")
    
    # Main content area
    try:
        # Load or generate data
        df = generate_sample_data()
        
        # Filter data based on date selection
        mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
        filtered_df = df.loc[mask]
        
        if filtered_df.empty:
            st.warning("No data available for the selected date range.")
            return
        
        # Display KPIs
        st.subheader("Performance Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_efficiency = filtered_df['Efficiency_X'].mean()
            st.metric("Average Efficiency", f"{avg_efficiency:.1f}%")
        
        with col2:
            total_fuel = filtered_df['Total_Fuel_Corrected'].sum()
            st.metric("Total Fuel Consumed", f"{total_fuel:.0f} units")
        
        with col3:
            avg_temp = filtered_df['Temperature'].mean()
            st.metric("Average Temperature", f"{avg_temp:.1f}°C")
        
        with col4:
            avg_pressure = filtered_df['Pressure'].mean()
            st.metric("Average Pressure", f"{avg_pressure:.1f} kPa")
        
        st.divider()
        
        # Create scatter plot with error handling
        st.subheader("Real Consumption vs Efficiency")
        
        try:
            # Try creating the scatter plot with trendline
            fig = px.scatter(
                filtered_df, 
                x="Total_Fuel_Corrected", 
                y="Efficiency_X",
                title='Real Consumption vs Efficiency',
                trendline='ols',
                labels={
                    "Total_Fuel_Corrected": "Total Fuel Consumed (units)",
                    "Efficiency_X": "Efficiency (%)"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating scatter plot: {str(e)}")
            # Fallback: create a basic scatter plot without trendline
            fig = px.scatter(
                filtered_df, 
                x="Total_Fuel_Corrected", 
                y="Efficiency_X",
                title='Real Consumption vs Efficiency (Basic)',
                labels={
                    "Total_Fuel_Corrected": "Total Fuel Consumed (units)",
                    "Efficiency_X": "Efficiency (%)"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info("Displaying basic scatter plot without trendline due to technical issues.")
        
        # Additional visualizations
        st.divider()
        st.subheader("Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Time series of efficiency
            fig_eff = px.line(
                filtered_df, 
                x="Date", 
                y="Efficiency_X",
                title="Efficiency Over Time",
                labels={"Efficiency_X": "Efficiency (%)"}
            )
            st.plotly_chart(fig_eff, use_container_width=True)
        
        with col2:
            # Time series of fuel consumption
            fig_fuel = px.line(
                filtered_df, 
                x="Date", 
                y="Total_Fuel_Corrected",
                title="Fuel Consumption Over Time",
                labels={"Total_Fuel_Corrected": "Fuel Consumed (units)"}
            )
            st.plotly_chart(fig_fuel, use_container_width=True)
            
    except Exception as e:
        st.error("An error occurred while processing the data.")
        st.info("Please try refreshing the data or selecting a different date range.")
        # Log the error for debugging (in a real app, you'd use proper logging)
        st.code(f"Error details: {str(e)}")

# Run the app
if __name__ == "__main__":
    main()
