from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import joblib
import os

app = Flask(__name__)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/science")
def science():
    return render_template("science.html")

def load_model():
    model_path = "models/model.pkl"
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print("Model loaded successfully!")
        print("Model features:", model.feature_names_in_)
        return model
    else:
        # Training data - create with the exact feature order we want
        feature_names = [
            'Age', 'Gender_Male', 'Genotype_AA', 'BloodGroup_AB', 
            'Temperature', 'Humidity', 'AirQualityIndex', 'Gender_Female', 
            'Genotype_AS', 'Genotype_SS', 'BloodGroup_A', 'BloodGroup_B', 'BloodGroup_O'
        ]
        
        X_train = pd.DataFrame(columns=feature_names)
        for col in feature_names:
            if col == 'Age':
                X_train[col] = np.random.randint(1, 80, 100)
            elif col in ['Temperature']:
                X_train[col] = np.random.uniform(-10, 40, 100)
            elif col in ['Humidity']:
                X_train[col] = np.random.uniform(0, 100, 100)
            elif col in ['AirQualityIndex']:
                X_train[col] = np.random.randint(0, 500, 100)
            else:
                X_train[col] = np.random.choice([0, 1], 100)
        
        y_train = np.random.choice([0, 1], 100)
        
        # Train model
        model = XGBClassifier().fit(X_train, y_train)
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, model_path)
        print("New model trained and saved!")
        print("Model features:", model.feature_names_in_)
        return model

model = load_model()

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get form data
        data = request.form
        print("Received form data:", dict(data))
        
        age = int(data["age"])
        gender = data["gender"]
        genotype = data["genotype"]
        blood_group = data["blood_group"]
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        air_quality = int(data["air_quality"])

        # Create a DataFrame with all features set to 0, in the correct order
        input_data = pd.DataFrame(0, index=[0], columns=model.feature_names_in_)
        
        # Set the basic numeric values
        input_data["Age"] = age
        input_data["Temperature"] = temperature
        input_data["Humidity"] = humidity
        input_data["AirQualityIndex"] = air_quality
        
        # Set the categorical values (one-hot encoded)
        gender_col = f"Gender_{gender}"
        genotype_col = f"Genotype_{genotype}"
        blood_group_col = f"BloodGroup_{blood_group}"
        
        # Ensure these columns exist in the model
        if gender_col in input_data.columns:
            input_data[gender_col] = 1
        if genotype_col in input_data.columns:
            input_data[genotype_col] = 1
        if blood_group_col in input_data.columns:
            input_data[blood_group_col] = 1

        print("Input data for prediction:")
        print(input_data)
        print("Data types:", input_data.dtypes)

        # Predict
        prediction = model.predict(input_data)[0]
        prediction_proba = model.predict_proba(input_data)[0]
        
        result = {
            "prediction": "High risk of catching a cold ❌" if prediction == 1 else "Low risk of catching a cold ✅",
            "confidence": f"{max(prediction_proba) * 100:.1f}%",
            "details": f"Probability: {prediction_proba[1] * 100:.1f}% risk, {prediction_proba[0] * 100:.1f}% safe"
        }

        return result
        
    except Exception as e:
        print("Error occurred:", str(e))
        import traceback
        traceback.print_exc()
        return {"error": f"Prediction failed: {str(e)}"}, 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)