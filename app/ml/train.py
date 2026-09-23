from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


DATA_PATH = Path(
    "app/ml/data/fulfillment_historical_data.csv"
)

MODEL_PATH = Path(
    "app/ml/models/delivery_model.pkl"
)

MODEL_VERSION = "xgboost-v2"

TRAINING_DATA_TYPE = "dummy_historical_csv"

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

TARGET = "fulfillment_days"


def train_model():

    print("=" * 50)
    print("DELIVERY PREDICTION MODEL TRAINING")
    print("=" * 50)

    # -----------------------------
    # 1. Load dataset
    # -----------------------------

    print("\nLoading historical dataset...")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    print(
        f"Dataset loaded successfully: "
        f"{len(df)} rows"
    )

    # -----------------------------
    # 2. Validate dataset
    # -----------------------------

    required_columns = FEATURES + [TARGET]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{missing_columns}"
        )

    if df[required_columns].isnull().any().any():
        raise ValueError(
            "Dataset contains missing values "
            "in required columns."
        )

    # -----------------------------
    # 3. Prepare features and target
    # -----------------------------

    X = df[FEATURES]

    y = df[TARGET]

    print(
        f"\nFeatures: {len(FEATURES)}"
    )

    print(
        f"Target: {TARGET}"
    )

    # -----------------------------
    # 4. Train/test split
    # -----------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
    )

    print(
        f"\nTraining records: {len(X_train)}"
    )

    print(
        f"Testing records: {len(X_test)}"
    )

    # -----------------------------
    # 5. Create XGBoost model
    # -----------------------------

    print("\nTraining XGBoost model...")

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

    # -----------------------------
    # 6. Predictions
    # -----------------------------

    predictions = model.predict(
        X_test
    )

    # -----------------------------
    # 7. Model evaluation
    # -----------------------------

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

    absolute_errors = abs(
        y_test.to_numpy() - predictions
    )

    accuracy_within_1_day = (
        absolute_errors <= 1
    ).mean() * 100

    accuracy_within_2_days = (
        absolute_errors <= 2
    ).mean() * 100

    # -----------------------------
    # 8. Print evaluation
    # -----------------------------

    print("\n")
    print("=" * 50)
    print("MODEL EVALUATION")
    print("=" * 50)

    print(
        f"Mean Absolute Error : "
        f"{mae:.2f} days"
    )

    print(
        f"Root Mean Squared Error : "
        f"{rmse:.2f} days"
    )

    print(
        f"R² Score : "
        f"{r2:.4f}"
    )

    print(
        f"Accuracy within ±1 day : "
        f"{accuracy_within_1_day:.2f}%"
    )

    print(
        f"Accuracy within ±2 days : "
        f"{accuracy_within_2_days:.2f}%"
    )

    # -----------------------------
    # 9. Save model
    # -----------------------------

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

    print("\n")
    print("=" * 50)
    print("MODEL SAVED")
    print("=" * 50)

    print(
        f"Model path: {MODEL_PATH}"
    )

    print(
        f"Model version: {MODEL_VERSION}"
    )

    print(
        f"Training data: {TRAINING_DATA_TYPE}"
    )


if __name__ == "__main__":
    train_model()