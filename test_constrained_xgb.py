import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

F = [
    "rainfall_24h",
    "rainfall_7d",
    "elevation",
    "slope",
    "historical_landslides",
]

d = pd.read_csv(r"backend\data\processed\training.csv").dropna()
X = d[F].astype(float)
y = d["target"].astype(int)

Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

m = XGBClassifier(
    n_estimators=350,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.9,
    eval_metric="logloss",
    random_state=42,
    n_jobs=4,
    monotone_constraints=(1, 1, 0, 0, 0),
)

m.fit(Xtr, ytr)

print("=== CONSTRAINED XGBOOST RAINFALL TEST ===")

base = {
    "rainfall_24h": 10,
    "rainfall_7d": 100,
    "elevation": 700,
    "slope": 20,
    "historical_landslides": 2,
}

for rainfall in [0, 10, 25, 50, 75, 100, 150, 200, 300, 400, 500]:
    row = {**base, "rainfall_24h": rainfall}
    probability = float(
        m.predict_proba(pd.DataFrame([row], columns=F))[0][1]
    ) * 100
    print(f"{rainfall:>3} mm -> {probability:.2f}%")
