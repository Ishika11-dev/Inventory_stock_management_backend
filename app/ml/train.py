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

from app.ml.synthetic_data import save_historical_dataset

DATA_PATH = Path("app/ml/data/fulfillment_historical_data.csv")
MODEL_PATH = Path("app/ml/models/delivery_model.pkl")

MODEL_VERSION = "xgboost-v3"
TRAINING_DATA_TYPE = "historical_fulfillment_csv_with_weather_and_distance"

FEATURES = [
    "order_quantity",
    "number_of_items",
    "current_stock",
    "reorder_level",
    "shortage_quantity",
    "distance_km",
    "shipping_mode",
    "rainy_days_in_transit",
    "supplier_lead_time",
    "processing_time",
]

TARGET = "fulfillment_days"


def train_model():
    print("=" * 60)
    print("DELIVERY PREDICTION MODEL TRAINING (XGBOOST)")
    print("=" * 60)

    # 1. Ensure dataset exists and has updated schema
    if not DATA_PATH.exists():
        print("Dataset not found. Generating fresh historical dataset...")
        save_historical_dataset(rows=5000)

    df = pd.read_csv(DATA_PATH)

    # If old columns exist, regenerate
    required_columns = FEATURES + [TARGET]
    if any(col not in df.columns for col in required_columns):
        print("Dataset schema outdated. Regenerating fresh historical dataset...")
        save_historical_dataset(rows=5000)
        df = pd.read_csv(DATA_PATH)

    print(f"\nDataset loaded: {len(df)} rows across {len(FEATURES)} features")

    # 2. Prepare Features & Target
    X = df[FEATURES]
    y = df[TARGET]

    # 3. Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"Training samples: {len(X_train)} | Test samples: {len(X_test)}")

    # 4. Train XGBoost Regressor
    print("\nFitting XGBRegressor...")
    model = XGBRegressor(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="reg:squarederror",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # 5. Evaluate Performance
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    abs_errors = abs(y_test.to_numpy() - predictions)
    acc_1_day = (abs_errors <= 1.0).mean() * 100
    acc_2_days = (abs_errors <= 2.0).mean() * 100

    print("\n" + "=" * 60)
    print("MODEL EVALUATION RESULTS")
    print("=" * 60)
    print(f"Mean Absolute Error (MAE)  : {mae:.2f} days")
    print(f"Root Mean Squared Error    : {rmse:.2f} days")
    print(f"R² Score                   : {r2:.4f}")
    print(f"Accuracy within ±1.0 day   : {acc_1_day:.2f}%")
    print(f"Accuracy within ±2.0 days  : {acc_2_days:.2f}%")

    # 6. Save Model Bundle
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model_data = {
        "model": model,
        "features": FEATURES,
        "model_version": MODEL_VERSION,
        "training_data_type": TRAINING_DATA_TYPE,
        "metrics": {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 4),
            "acc_1_day": round(acc_1_day, 2),
        }
    }
    joblib.dump(model_data, MODEL_PATH)

    print("\n" + "=" * 60)
    print("MODEL ARTIFACT SAVED")
    print("=" * 60)
    print(f"Model path: {MODEL_PATH}")
    print(f"Version   : {MODEL_VERSION}")


if __name__ == "__main__":
    train_model()