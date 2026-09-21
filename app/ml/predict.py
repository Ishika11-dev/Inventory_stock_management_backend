from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(
    "app/ml/models/delivery_model.pkl"
)


def predict_delivery_days(
    features: dict
) -> dict:

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Delivery prediction model not found. "
            "Run 'python -m app.ml.train' first."
        )

    saved_model = joblib.load(
        MODEL_PATH
    )

    model = saved_model["model"]

    feature_names = saved_model["features"]

    model_version = saved_model[
        "model_version"
    ]

    training_data_type = saved_model[
        "training_data_type"
    ]

    data = pd.DataFrame(
        [features],
        columns=feature_names
    )

    prediction = model.predict(
        data
    )[0]

    predicted_days = max(
        1.0,
        float(prediction)
    )

    return {
        "predicted_fulfillment_days": predicted_days,
        "model_version": model_version,
        "training_data_type": training_data_type,
    }