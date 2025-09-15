import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Boiler Performance Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 1rem;
        color: #555;
    }
    .metric-card h2 {
        margin: 0.5rem 0 0 0;
        font-size: 1.8rem;
        color: #1E88E5;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .divider {
        border-top: 1px solid #ddd;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data
@st.cache_data
def generate_sample_data():
    dates = pd.date_range(start="2025-09-01", end="2025-10-03")
    np.random.seed(42)  # For consistent data
    
    # Create realistic boiler data with some correlation
    base_fuel = np.random.uniform(100, 500, len(dates))
    efficiency = 85 - (base_fuel - 300) ** 2 / 8000 + np.random.normal(0, 3, len(dates))
    efficiency = np.clip(efficiency, 65, 95)
    
    data = {
        "Date": dates,
        "Total_Fuel_Corrected": base_fuel,
        "Efficiency_X": efficiency,
        "Temperature": np.random.uniform(60, 120, len(dates)),
        "Pressure": np.random.uniform(10, 50, len(dates)),
        "Operating_Hours": np.random.uniform(8, 24, len(dates)),
        "Steam_Output": base_fuel * 2.5 + np.random.normal(0, 50, len(dates))
    }
    return pd.DataFrame(data)

# Main app function
def main():
    # Header
    st.markdown('<h1 class="main-header">🔥 Boiler Performance Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for filters and actions
    with st.sidebar:
        st.markdown("### ⚙️ Controls Panel")
        
        # Date range selector
        st.markdown("**Date Range Filter**")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start", value=datetime(2025, 9, 1), key="start")
        with col2:
            end_date = st.date_input("End", value=datetime(2025, 10, 3), key="end")
        
        st.markdown("---")
        
        # Additional filters
        st.markdown("**Display Options**")
        show_trendline = st.checkbox("Show Trendlines", value=True)
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("**Quick Actions**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", help="Refresh data"):
                st.rerun()
        with col2:
            if st.button("📊 Report", help="Generate report"):
                st.success("Report generation started!")
    
    # Load or generate data
    df = generate_sample_data()
    
    # Filter data based on date selection
    mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
    filtered_df = df.loc[mask]
    
    if filtered_df.empty:
        st.warning("No data available for the selected date range.")
        return
    
    # Display KPIs
    st.markdown("## 📊 Performance Overview")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        avg_efficiency = filtered_df['Efficiency_X'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Average Efficiency</h3>
            <h2>{avg_efficiency:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi2:
        total_fuel = filtered_df['Total_Fuel_Corrected'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Fuel Consumed</h3>
            <h2>{total_fuel:.0f} units</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi3:
        avg_temp = filtered_df['Temperature'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Average Temperature</h3>
            <h2>{avg_temp:.1f}°C</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi4:
        avg_pressure = filtered_df['Pressure'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Average Pressure</h3>
            <h2>{avg_pressure:.1f} kPa</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Main charts
    st.markdown("---")
    st.markdown("## 📈 Performance Analysis")
    
    # Create scatter plot with error handling
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Real Consumption vs Efficiency")
        try:
            # Try creating the scatter plot with trendline
            fig = px.scatter(
                filtered_df, 
                x="Total_Fuel_Corrected", 
                y="Efficiency_X",
                title='Fuel Consumption vs Efficiency',
                trendline='ols' if show_trendline else None,
                labels={
                    "Total_Fuel_Corrected": "Total Fuel Consumed (units)",
                    "Efficiency_X": "Efficiency (%)"
                },
                color="Efficiency_X",
                color_continuous_scale=px.colors.sequential.Viridis
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating scatter plot: {str(e)}")
            # Fallback: create a basic scatter plot without trendline
            fig = px.scatter(
                filtered_df, 
                x="Total_Fuel_Corrected", 
                y="Efficiency_X",
                title='Fuel Consumption vs Efficiency (Basic)',
                labels={
                    "Total_Fuel_Corrected": "Total Fuel Consumed (units)",
                    "Efficiency_X": "Efficiency (%)"
                },
                color="Efficiency_X",
                color_continuous_scale=px.colors.sequential.Viridis
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info("Trendline feature unavailable. Please install statsmodels with: 'pip install statsmodels'")
    
    with col2:
        st.markdown("### Efficiency Distribution")
        fig = px.histogram(
            filtered_df, 
            x="Efficiency_X",
            nbins=10,
            title="Efficiency Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Key Statistics")
        st.dataframe(
            filtered_df[["Efficiency_X", "Total_Fuel_Corrected", "Temperature", "Pressure"]].describe(),
            use_container_width=True
        )
    
    # Additional visualizations
    st.markdown("---")
    st.markdown("## 📅 Time Series Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Time series of efficiency
        fig = px.line(
            filtered_df, 
            x="Date", 
            y="Efficiency_X",
            title="Efficiency Over Time",
            labels={"Efficiency_X": "Efficiency (%)"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Time series of fuel consumption
        fig = px.line(
            filtered_df, 
            x="Date", 
            y="Total_Fuel_Corrected",
            title="Fuel Consumption Over Time",
            labels={"Total_Fuel_Corrected": "Fuel Consumed (units)"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation heatmap
    st.markdown("---")
    st.markdown("## 🔍 Correlation Analysis")
    
    numeric_df = filtered_df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Correlation Between Metrics"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("---")
    st.markdown("## 📋 Raw Data")
    st.dataframe(filtered_df, use_container_width=True)

# Run the app
if __name__ == "__main__":
    main()
