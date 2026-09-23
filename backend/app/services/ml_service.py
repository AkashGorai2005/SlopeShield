from pathlib import Path
import math, joblib, pandas as pd
from app.config import get_settings
from app.services.risk_engine import classify_probability

FEATURES=[
    "rainfall_24h",
    "rainfall_7d",
    "elevation",
    "slope",
    "historical_landslides",
]

class MLService:
    def __init__(self):
        self.settings=get_settings(); self.model=None; self.model_source="untrained"; self.metadata={}; self._load()

    def _load(self):
        path=self.settings.resolved_model_path
        if path.exists():
            self.model=joblib.load(path)
            self.metadata=getattr(self.model,"metadata",{}) if hasattr(self.model,"metadata") else {}
            if not self.metadata and isinstance(self.model,dict):
                self.metadata=self.model.get("metadata",{})
            self.model_source=self.metadata.get("model_name","trained-model")

    @property
    def trained(self):
        return self.model is not None

    @property
    def feature_schema(self):
        return FEATURES

    def predict(self,features,simulated=False):
        if self.model is not None:
            model=self.model.get("model") if isinstance(self.model,dict) else self.model
            row=pd.DataFrame([{k:float(features.get(k,0) or 0) for k in FEATURES}])
            probability=float(model.predict_proba(row)[0][1])
            source=self.model_source

        else:
            raise RuntimeError("No trained model is available. Run the real-data pipeline first.")

        used_features = {
            key: float(features.get(key, 0) or 0)
            for key in FEATURES
        }

        return {
            "probability":probability,
            "riskLevel":classify_probability(probability),
            "modelSource":source,
            "factors":self._factor_explanations(features),
            "simulated":simulated,
            "features":used_features
        }

    @staticmethod
    def _factor_explanations(features):
        factors=[]

        rainfall_24h=float(features.get("rainfall_24h",0) or 0)
        rainfall_7d=float(features.get("rainfall_7d",0) or 0)
        slope=float(features.get("slope",0) or 0)
        historical=float(features.get("historical_landslides",0) or 0)

        if rainfall_24h>=120:
            factors.append("Heavy 24-hour rainfall")
        elif rainfall_24h>=50:
            factors.append("Elevated 24-hour rainfall")

        if rainfall_7d>=300:
            factors.append("High 7-day rainfall accumulation")

        if slope>=30:
            factors.append("Steep slope")

        if historical>=1:
            factors.append("Historical landslide activity")

        if not factors:
            factors.append("No dominant threshold factor")

        return factors

ml_service=MLService()
