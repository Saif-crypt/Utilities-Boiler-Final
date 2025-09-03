# ============================================
# 📌 PHASE 3 (Streamlit): Boiler Plant Dashboard
# Save as app.py and run: streamlit run app.py
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Data
df = pd.read_csv("boiler_phase3_dashboard.csv")

st.title("🔥 Boiler Plant Monitoring Dashboard")

# ============================================
# 1️⃣ KPIs
# ============================================
st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)
col1.metric("Avg Efficiency (%)", round(df["Overall_Efficiency_%"].mean(),2))
col2.metric("Total Fuel Used (m³)", int(df["Boiler1_FuelConsumption_m3"].sum() + df["Boiler2_FuelConsumption_m3"].sum()))
col3.metric("Total Steam (Tons)", int(df["Boiler1_Steam_Tons"].sum() + df["Boiler2_Steam_Tons"].sum()))

# ============================================
# 2️⃣ Efficiency Trend
# ============================================
st.subheader("Efficiency Trend (Actual vs Predicted)")
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(df["Timestamp"], df["Overall_Efficiency_%"], label="Actual Efficiency", color="blue")
ax.plot(df["Timestamp"], df["Efficiency_Pred"], label="Predicted Efficiency", color="orange")
ax.set_xlabel("Timestamp")
ax.set_ylabel("Efficiency (%)")
ax.legend()
st.pyplot(fig)

# ============================================
# 3️⃣ Efficiency vs O2%
# ============================================
st.subheader("Efficiency vs O₂% with Anomalies")
fig, ax = plt.subplots(figsize=(8,5))
sns.scatterplot(x="O2_Percent", y="Overall_Efficiency_%", hue="Anomaly", data=df, palette="coolwarm", ax=ax)
st.pyplot(fig)

# ============================================
# 4️⃣ Fuel vs Steam
# ============================================
st.subheader("Fuel Consumption vs Steam Generation")
df["Total_Fuel"] = df["Boiler1_FuelConsumption_m3"] + df["Boiler2_FuelConsumption_m3"]
df["Total_Steam"] = df["Boiler1_Steam_Tons"] + df["Boiler2_Steam_Tons"]

fig, ax = plt.subplots(figsize=(8,5))
sns.scatterplot(x="Total_Fuel", y="Total_Steam", data=df, ax=ax)
st.pyplot(fig)

st.success("✅ Dashboard Ready! Use filters and check KPIs.")
