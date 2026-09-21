from pathlib import Path

import joblib
from xgboost import XGBRegressor

from app.ml.synthetic_data import generate_training_data


MODEL_PATH = Path(
    "app/ml/models/delivery_model.pkl"
)


def train_model():

    df = generate_training_data(1000)

    features = [
        "order_quantity",
        "number_of_items",
        "current_stock",
        "reorder_level",
        "shortage_quantity",
        "supplier_lead_time",
        "processing_time",
        "shipping_time",
    ]

    X = df[features]
    y = df["fulfillment_days"]

    model = XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        random_state=42
    )

    model.fit(X, y)

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": model,
            "features": features,
            "training_data_type": "synthetic"
        },
        MODEL_PATH
    )


if __name__ == "__main__":
    train_model()