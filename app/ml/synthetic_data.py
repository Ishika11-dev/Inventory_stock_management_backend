import numpy as np
import pandas as pd


def generate_training_data(rows: int = 1000) -> pd.DataFrame:
    rng = np.random.default_rng(42)

    order_quantity = rng.integers(
        1,
        10,
        rows
    )

    number_of_items = rng.integers(
        1,
        5,
        rows
    )

    current_stock = rng.integers(
        0,
        30,
        rows
    )

    reorder_level = rng.integers(
        2,
        15,
        rows
    )

    supplier_lead_time = rng.integers(
        1,
        10,
        rows
    )

    processing_time = rng.integers(
        1,
        4,
        rows
    )

    shipping_time = rng.integers(
        1,
        6,
        rows
    )

    shortage_quantity = np.maximum(
        order_quantity - current_stock,
        0
    )

    # Synthetic target.
    # This is only for bootstrapping the first model.
    fulfillment_days = (
        processing_time
        + shipping_time
        + shortage_quantity * 0.5
        + supplier_lead_time * (shortage_quantity > 0)
        + rng.normal(0, 0.5, rows)
    )

    fulfillment_days = np.maximum(
        fulfillment_days,
        1
    )

    return pd.DataFrame(
        {
            "order_quantity": order_quantity,
            "number_of_items": number_of_items,
            "current_stock": current_stock,
            "reorder_level": reorder_level,
            "shortage_quantity": shortage_quantity,
            "supplier_lead_time": supplier_lead_time,
            "processing_time": processing_time,
            "shipping_time": shipping_time,
            "fulfillment_days": fulfillment_days,
        }
    )