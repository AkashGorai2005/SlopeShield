import joblib
import pandas as pd

model = joblib.load(r"backend\models\landslide_model.joblib")

base = {
    "rainfall_24h": 10,
    "rainfall_7d": 100,
    "elevation": 700,
    "slope": 20,
    "historical_landslides": 2,
}

rainfalls = [0, 10, 25, 50, 75, 100, 150, 200, 300, 400, 500]

for rainfall in rainfalls:
    row = {**base, "rainfall_24h": rainfall}
    df = pd.DataFrame([row])
    probability = float(model.predict_proba(df)[0][1]) * 100
    print(f"{rainfall:>3} mm -> {probability:.2f}%")
