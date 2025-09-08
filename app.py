import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# --------------------------------
# Boiler Constants
# --------------------------------
STEAM_ENERGY = 600  # kcal/kg approx

# --------------------------------
# Streamlit App
# --------------------------------
st.set_page_config(page_title="Boiler Efficiency Dashboard", layout="wide")
st.title("🔥 Boiler Efficiency & Anomaly Detection Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload Boiler Dataset (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # -------------------------------
    # Phase 2: Efficiency Calculation
    # -------------------------------
    df["Boiler1_Efficiency_%"] = (
        (df["Boiler1_Steam_Production_tons"] * 1000 * STEAM_ENERGY) /
        (df["Boiler1_NG_Consumption_Nm3"] * df["NG_CV_kcal_per_Nm3"] + 1e-6) * 100
    )

    df["Boiler2_Efficiency_%"] = (
        (df["Boiler2_Steam_Production_tons"] * 1000 * STEAM_ENERGY) /
        (df["Boiler2_NG_Consumption_Nm3"] * df["NG_CV_kcal_per_Nm3"] + 1e-6) * 100
    )

    df["Overall_Efficiency_%"] = (
        ((df["Boiler1_Steam_Production_tons"] + df["Boiler2_Steam_Production_tons"]) * 1000 * STEAM_ENERGY) /
        ((df["Boiler1_NG_Consumption_Nm3"] + df["Boiler2_NG_Consumption_Nm3"]) * df["NG_CV_kcal_per_Nm3"] + 1e-6) * 100
    )

    st.subheader("📊 Calculated Efficiencies")
    st.dataframe(df[["Boiler1_Efficiency_%", "Boiler2_Efficiency_%", "Overall_Efficiency_%"]].head())

    # -------------------------------
    # Phase 4: Anomaly Detection
    # -------------------------------
    features_for_anomaly = df[["Boiler1_Efficiency_%", "Boiler2_Efficiency_%", "Overall_Efficiency_%"]]

    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    df["Anomaly"] = iso_forest.fit_predict(features_for_anomaly)
    df["Anomaly"] = df["Anomaly"].map({1: "Normal", -1: "Anomaly"})

    st.subheader("🚨 Anomaly Detection")
    st.write(df["Anomaly"].value_counts())
    st.dataframe(df[df["Anomaly"] == "Anomaly"])

    # -------------------------------
    # Phase 4: Prediction (RandomForest)
    # -------------------------------
    X = df[[
        "Boiler1_Steam_Production_tons",
        "Boiler2_Steam_Production_tons",
        "Boiler1_NG_Consumption_Nm3",
        "Boiler2_NG_Consumption_Nm3",
        "NG_CV_kcal_per_Nm3"
    ]]
    y = df["Overall_Efficiency_%"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    st.subheader("🤖 Prediction Results")
    st.write("Mean Absolute Error:", mae)
    st.write("R² Score:", r2)

    st.dataframe(pd.DataFrame({"Actual": y_test, "Predicted": y_pred}).reset_index(drop=True).head())

    # -------------------------------
    # Visualization
    # -------------------------------
    st.subheader("📈 Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Efficiency Trends")
        fig, ax = plt.subplots(figsize=(8,4))
        df[["Boiler1_Efficiency_%", "Boiler2_Efficiency_%", "Overall_Efficiency_%"]].plot(ax=ax)
        st.pyplot(fig)

    with col2:
        st.write("Actual vs Predicted Efficiency")
        fig, ax = plt.subplots(figsize=(6,4))
        ax.scatter(y_test, y_pred, alpha=0.7, edgecolors="k")
        ax.plot([y.min(), y.max()], [y.min(), y.max()], "r--")
        ax.set_xlabel("Actual Efficiency (%)")
        ax.set_ylabel("Predicted Efficiency (%)")
        st.pyplot(fig)

else:
    st.info("👆 Please upload a CSV file to start.")
