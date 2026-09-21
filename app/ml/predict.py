from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(
    "app/ml/models/delivery_model.pkl"
)


def predict_delivery_days(features: dict) -> float:

    saved = joblib.load(MODEL_PATH)

    model = saved["model"]
    feature_names = saved["features"]

    data = pd.DataFrame(
        [features],
        columns=feature_names
    )

    prediction = model.predict(data)[0]

    return max(
        1.0,
        float(prediction)
    )