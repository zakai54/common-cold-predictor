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
        return joblib.load(model_path)
    else:
        # Training data
        X_train = pd.DataFrame({
            'Age': np.random.randint(1, 80, 100),
            'Gender_Male': np.random.choice([0, 1], 100),
            'Gender_Female': np.random.choice([0, 1], 100),
            'Genotype_AA': np.random.choice([0, 1], 100),
            'Genotype_AS': np.random.choice([0, 1], 100),
            'Genotype_SS': np.random.choice([0, 1], 100),
            'BloodGroup_A': np.random.choice([0, 1], 100),
            'BloodGroup_B': np.random.choice([0, 1], 100),
            'BloodGroup_AB': np.random.choice([0, 1], 100),
            'BloodGroup_O': np.random.choice([0, 1], 100),
            'Temperature': np.random.uniform(-10, 40, 100),
            'Humidity': np.random.uniform(0, 100, 100),
            'AirQualityIndex': np.random.randint(0, 500, 100)
        })
        y_train = np.random.choice([0, 1], 100)
        
        # Train model
        model = XGBClassifier().fit(X_train, y_train)
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, model_path)
        return model

model = load_model()

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get form data
        data = request.form
        age = int(data["age"])
        gender = data["gender"]
        genotype = data["genotype"]
        blood_group = data["blood_group"]
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        air_quality = int(data["air_quality"])

        # Prepare input DataFrame
        input_data = pd.DataFrame({
            "Age": [age],
            f"Gender_{gender}": [1],
            f"Genotype_{genotype}": [1],
            f"BloodGroup_{blood_group}": [1],
            "Temperature": [temperature],
            "Humidity": [humidity],
            "AirQualityIndex": [air_quality]
        })

        # Ensure all columns exist
        for col in model.feature_names_in_:
            if col not in input_data.columns:
                input_data[col] = 0

        # Predict
        prediction = model.predict(input_data)[0]
        result = "High risk of catching a cold ❌" if prediction == 1 else "Low risk of catching a cold ✅"

        return {"prediction": result}
    except Exception as e:
        return {"error": str(e)}, 400

if __name__ == "__main__":
    app.run(debug=True)