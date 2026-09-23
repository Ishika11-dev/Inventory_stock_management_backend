from pathlib import Path

import joblib
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
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

    # --------------------------------------------------
    # MODEL EVALUATION
    # --------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    # Percentage of predictions within ±1 day
    accuracy_within_1_day = (
        abs(y_test - predictions) <= 1
    ).mean() * 100

    # Percentage of predictions within ±2 days
    accuracy_within_2_days = (
        abs(y_test - predictions) <= 2
    ).mean() * 100

    print()
    print("======================================")
    print("MODEL EVALUATION")
    print("======================================")

    print(
        f"Mean Absolute Error : {mae:.2f} days"
    )

    print(
        f"Root Mean Squared Error : {rmse:.2f} days"
    )

    print(
        f"R² Score : {r2:.4f}"
    )

    print(
        f"Accuracy within ±1 day : "
        f"{accuracy_within_1_day:.2f}%"
    )

    print(
        f"Accuracy within ±2 days : "
        f"{accuracy_within_2_days:.2f}%"
    )

    print("======================================")
    print()

    # --------------------------------------------------
    # SAVE MODEL
    # --------------------------------------------------

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