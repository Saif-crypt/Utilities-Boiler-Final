import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# ---------------------------
# Load Data
# ---------------------------
st.title("🔥 Boiler Performance Dashboard")

uploaded_file = st.file_uploader("Upload cleaned boiler dataset (CSV)", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Ensure Steam Flow column
    if "SteamFlow_TPH" not in df.columns and "NG_Consumption_Nm3" in df.columns:
        CV = 9400  # kcal/Nm3
        eta = 0.85
        hsteam = 660  # kcal/kg
        df["SteamFlow_TPH"] = (df["NG_Consumption_Nm3"] * CV * eta) / (hsteam * 1000)

    st.subheader("📊 Dataset Preview")
    st.write(df.head())

    # ---------------------------
    # Visualization
    # ---------------------------
    st.subheader("📈 Steam vs Fuel Consumption")
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(df["Timestamp"], df["SteamFlow_TPH"], label="Steam Flow (TPH)")
    if "NG_Consumption_Nm3" in df.columns:
        ax.plot(df["Timestamp"], df["NG_Consumption_Nm3"], label="NG Consumption (Nm³)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Values")
    ax.set_title("Steam vs Fuel Over Time")
    ax.legend()
    st.pyplot(fig)

    # ---------------------------
    # Machine Learning Model
    # ---------------------------
    st.subheader("🤖 Steam Flow Prediction Model")

    possible_features = [
        "NG_Consumption_Nm3",
        "FeedWater_Temperature_C", 
        "Boiler_Pressure_kgcm2", 
        "FlueGas_Temperature_C",
        "Oxygen_Percent", 
        "Stack_Temperature_C"
    ]
    features = [f for f in possible_features if f in df.columns]

    if len(features) > 0:
        X = df[features]
        y = df["SteamFlow_TPH"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        rf = RandomForestRegressor(n_estimators=200, random_state=42)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)

        # Feature Importance
        importance = rf.feature_importances_
        fig2, ax2 = plt.subplots()
        sns.barplot(x=importance, y=features, ax=ax2, palette="viridis")
        ax2.set_title("Feature Importance")
        st.pyplot(fig2)

        # Prediction vs Actual
        fig3, ax3 = plt.subplots()
        ax3.scatter(y_test, y_pred, alpha=0.7, color="orange")
        ax3.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
        ax3.set_xlabel("Actual Steam Flow (TPH)")
        ax3.set_ylabel("Predicted Steam Flow (TPH)")
        ax3.set_title("Prediction vs Actual")
        st.pyplot(fig3)

        st.success("✅ Model trained and results displayed")

    else:
        st.warning("⚠️ No additional features found in dataset (only NG_Consumption available).")
