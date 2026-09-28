# ------------------------------------------------------------
# SuperKart sales-forecast UI (Streamlit)
# ------------------------------------------------------------
import os
import pandas as pd
import requests
import streamlit as st

# Backend address: "backend" is the Flask container name on the shared Docker network.
# It can be overridden with the BACKEND_URL environment variable.
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒")
st.title("SuperKart Sales Forecast")
st.write("Enter product and store details to forecast the total sales of a product in a store.")

# ---------------- Single prediction ----------------
st.subheader("Single prediction")
col1, col2 = st.columns(2)
with col1:
    Product_Weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66)
    Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    Product_Allocated_Area = st.number_input("Product Allocated Area (0-1)", min_value=0.0, max_value=1.0, value=0.027, format="%.3f")
    Product_MRP = st.number_input("Product MRP", min_value=0.0, value=117.08)
    Product_Id_char = st.selectbox("Product ID Prefix (FD=Food, DR=Drinks, NC=Non-consumable)", ["FD", "DR", "NC"])
with col2:
    Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    Store_Type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
    Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, max_value=100, value=16)
    Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

# JSON payload for the API
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category,
}

if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
        if response.status_code == 200:
            st.success(f"Predicted Product Store Sales Total: {response.json()['Sales']:,.2f}")
        else:
            st.error(f"API error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to reach the prediction API: {e}")

# ---------------- Batch prediction ----------------
st.subheader("Batch prediction")
uploaded_file = st.file_uploader("Upload a CSV file with the 10 feature columns", type=["csv"])

if uploaded_file is not None and st.button("Predict for Batch", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files={"file": uploaded_file.getvalue()}, timeout=60)
        if response.status_code == 200:
            # Attach predictions to the uploaded rows so users see inputs and outputs together
            uploaded_file.seek(0)
            result_df = pd.read_csv(uploaded_file)
            preds = response.json()
            result_df["Predicted_Sales"] = [preds[str(i)] for i in range(len(result_df))]
            st.success("Predictions completed successfully!")
            st.dataframe(result_df, use_container_width=True)
            # Let the user download the results
            st.download_button("Download predictions", result_df.to_csv(index=False), "superkart_predictions.csv", "text/csv")
        else:
            st.error(f"API error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to reach the prediction API: {e}")
