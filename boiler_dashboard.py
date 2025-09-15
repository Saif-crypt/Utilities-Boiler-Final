# boiler_dashboard.py
# Streamlit Dashboard for Boiler Efficiency Monitoring

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Boiler Efficiency Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .alert-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load and preprocess data"""
    try:
        df = pd.read_csv('boiler_data_with_efficiency.csv', index_col='Date', parse_dates=['Date'])
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found. Please make sure 'boiler_data_with_efficiency.csv' is in the same directory.")
        st.stop()

def calculate_metrics(df):
    """Calculate key performance metrics"""
    metrics = {
        'avg_efficiency': df['Efficiency_%'].mean(),
        'max_efficiency': df['Efficiency_%'].max(),
        'min_efficiency': df['Efficiency_%'].min(),
        'best_day': df['Efficiency_%'].idxmax(),
        'worst_day': df['Efficiency_%'].idxmin(),
        'total_days': len(df),
        'period_start': df.index.min(),
        'period_end': df.index.max()
    }
    
    if 'boiler_steam_tons' in df.columns:
        metrics['total_steam'] = df['boiler_steam_tons'].sum()
        metrics['avg_daily_steam'] = df['boiler_steam_tons'].mean()
    
    if 'Total_Fuel_Corrected' in df.columns:
        metrics['total_fuel'] = df['Total_Fuel_Corrected'].sum()
        metrics['avg_daily_fuel'] = df['Total_Fuel_Corrected'].mean()
    
    return metrics

def create_alert_system(df, metrics):
    """Create alert system based on thresholds"""
    alerts = []
    
    # Low efficiency alert (bottom 25%)
    low_eff_threshold = df['Efficiency_%'].quantile(0.25)
    latest_eff = df['Efficiency_%'].iloc[-1]
    
    if latest_eff < low_eff_threshold:
        alerts.append({
            'type': '⚠️ LOW EFFICIENCY',
            'message': f'Current efficiency ({latest_eff:.1f}%) below threshold ({low_eff_threshold:.1f}%)',
            'severity': 'high'
        })
    
    # High fuel consumption alert
    if 'Total_Fuel_Corrected' in df.columns:
        high_fuel_threshold = df['Total_Fuel_Corrected'].quantile(0.75)
        latest_fuel = df['Total_Fuel_Corrected'].iloc[-1]
        
        if latest_fuel > high_fuel_threshold:
            alerts.append({
                'type': '⚠️ HIGH FUEL CONSUMPTION',
                'message': f'Current fuel consumption ({latest_fuel:.0f}) above threshold ({high_fuel_threshold:.0f})',
                'severity': 'medium'
            })
    
    return alerts

def main():
    # Load data
    df = load_data()
    metrics = calculate_metrics(df)
    alerts = create_alert_system(df, metrics)
    
    # Sidebar
    with st.sidebar:
        st.title("🔥 Boiler Dashboard")
        st.write("---")
        
        st.subheader("Date Range Filter")
        date_range = st.date_input(
            "Select date range:",
            value=(metrics['period_start'].date(), metrics['period_end'].date()),
            min_value=metrics['period_start'].date(),
            max_value=metrics['period_end'].date()
        )
        
        st.write("---")
        st.subheader("Quick Actions")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("📊 Download Report"):
            # Create and download report
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                label="Download CSV Report",
                data=csv,
                file_name="boiler_efficiency_report.csv",
                mime="text/csv"
            )
    
    # Main content
    st.markdown('<h1 class="main-header">Boiler Efficiency Dashboard</h1>', unsafe_allow_html=True)
    
    # Alert section
    if alerts:
        st.warning("## 🚨 Active Alerts")
        for alert in alerts:
            st.markdown(f"""
            <div class="alert-card">
                <strong>{alert['type']}</strong><br>
                {alert['message']}
            </div>
            """, unsafe_allow_html=True)
    
    # Key metrics
    st.write("## 📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Average Efficiency</h3>
            <h2>{metrics['avg_efficiency']:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⭐ Best Efficiency</h3>
            <h2>{metrics['max_efficiency']:.1f}%</h2>
            <small>{metrics['best_day'].date()}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📉 Worst Efficiency</h3>
            <h2>{metrics['min_efficiency']:.1f}%</h2>
            <small>{metrics['worst_day'].date()}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅 Analysis Period</h3>
            <h2>{metrics['total_days']} days</h2>
            <small>{metrics['period_start'].date()} to {metrics['period_end'].date()}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts and Visualizations
    st.write("## 📈 Performance Charts")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Efficiency Trend", "Distribution", "Correlations", "Detailed Analysis"])
    
    with tab1:
        st.plotly_chart(
            px.line(df, x=df.index, y='Efficiency_%', 
                   title='Efficiency Trend Over Time',
                   labels={'Efficiency_%': 'Efficiency (%)', 'index': 'Date'}),
            use_container_width=True
        )
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                px.histogram(df, x='Efficiency_%', 
                           title='Efficiency Distribution',
                           nbins=20),
                use_container_width=True
            )
        with col2:
            efficiency_ranges = pd.cut(df['Efficiency_%'], bins=5)
            range_counts = efficiency_ranges.value_counts().sort_index()
            st.plotly_chart(
                px.bar(x=[str(x) for x in range_counts.index], y=range_counts.values,
                      title='Efficiency Range Analysis',
                      labels={'x': 'Efficiency Range', 'y': 'Number of Days'}),
                use_container_width=True
            )
    
    with tab3:
        if 'Total_Fuel_Corrected' in df.columns and 'boiler_steam_tons' in df.columns:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    px.scatter(df, x='Total_Fuel_Corrected', y='Efficiency_%',
                             title='Fuel Consumption vs Efficiency',
                             trendline='ols'),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    px.scatter(df, x='boiler_steam_tons', y='Efficiency_%',
                             title='Steam Production vs Efficiency',
                             trendline='ols'),
                    use_container_width=True
                )
    
    with tab4:
        st.write("### Detailed Data Table")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    
    # Recommendations Section
    st.write("## 💡 Optimization Recommendations")
    
    if 'Total_Fuel_Corrected' in df.columns:
        fuel_efficiency = df['boiler_steam_tons'].sum() / df['Total_Fuel_Corrected'].sum() if 'boiler_steam_tons' in df.columns else 0
        
        rec_col1, rec_col2 = st.columns(2)
        
        with rec_col1:
            st.info("""
            **🎯 Immediate Actions:**
            - Monitor daily efficiency trends
            - Check fuel quality regularly
            - Maintain optimal steam pressure
            - Schedule regular boiler maintenance
            """)
        
        with rec_col2:
            st.success("""
            **📈 Improvement Opportunities:**
            - Implement predictive maintenance
            - Optimize fuel-air ratio
            - Reduce heat losses
            - Improve insulation
            - Train operators on best practices
            """)
    
    # Footer
    st.write("---")
    st.write("**📊 Dashboard Features:** Real-time monitoring • Alert system • Performance analytics • Optimization recommendations")
    st.write("**🔄 Auto-update:** Configure to refresh daily with new data")

if __name__ == "__main__":
    main()
