# ------------------------------------------------------------
# SuperKart sales-forecast REST API (Flask)
# ------------------------------------------------------------
import joblib                                  # load the serialized pipeline
import pandas as pd                            # build model input DataFrames
from flask import Flask, request, jsonify      # web framework

# Create the Flask application
superkart_api = Flask("SuperKart")

# Load the trained pipeline once at start-up (preprocessing + tuned Random Forest)
model = joblib.load("superkart_model.joblib")

# Features the model expects, in training order
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type", "Product_Id_char",
    "Store_Age_Years", "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    """Health-check / landing route."""
    return "Welcome to the SuperKart Sales Forecast API"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online inference: predict sales for one product-store record sent as JSON."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Reject requests with missing features
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Build a one-row DataFrame in the expected column order
    input_data = pd.DataFrame([{f: data[f] for f in FEATURES}])

    # Predict and return the value rounded to 2 decimals
    prediction = float(model.predict(input_data)[0])
    return jsonify({"Sales": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Batch inference: predict sales for every row of an uploaded CSV file."""
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file under the key 'file'"}), 400

    # Read the uploaded CSV into a DataFrame
    input_data = pd.read_csv(request.files["file"])

    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    # Predict for all rows at once
    predictions = model.predict(input_data[FEATURES])

    # Map row index -> predicted sales
    return jsonify({str(i): round(float(p), 2) for i, p in enumerate(predictions)})


# Local development entry point (in Docker the app is served by gunicorn)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
