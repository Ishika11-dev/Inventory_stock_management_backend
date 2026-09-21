from pathlib import Path

import joblib
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from app.ml.synthetic_data import generate_training_data


MODEL_PATH = Path(
    "app/ml/models/delivery_model.pkl"
)

MODEL_VERSION = "xgboost-v1"

TRAINING_DATA_TYPE = "synthetic"

FEATURES = [
    "order_quantity",
    "number_of_items",
    "current_stock",
    "reorder_level",
    "shortage_quantity",
    "supplier_lead_time",
    "processing_time",
    "shipping_time",
]


def train_model():

    print("Generating synthetic training data...")

    df = generate_training_data(
        rows=1000
    )

    X = df[FEATURES]

    y = df["fulfillment_days"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    print("Training XGBoost model...")

    model = XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        objective="reg:squarederror",
        random_state=42,
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    print(
        f"Mean Absolute Error: {mae:.2f} days"
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    model_data = {
        "model": model,
        "features": FEATURES,
        "model_version": MODEL_VERSION,
        "training_data_type": TRAINING_DATA_TYPE,
    }

    joblib.dump(
        model_data,
        MODEL_PATH
    )

    print(
        f"Model saved to: {MODEL_PATH}"
    )

    print(
        f"Model version: {MODEL_VERSION}"
    )

    print(
        f"Training data: {TRAINING_DATA_TYPE}"
    )


if __name__ == "__main__":
    train_model()