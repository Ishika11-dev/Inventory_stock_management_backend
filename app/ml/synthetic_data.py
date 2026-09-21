"""Synthetic training data used until enough completed real orders exist."""
import random

FEATURE_NAMES = [
    "order_quantity",
    "number_of_items",
    "order_value",
    "current_stock",
    "shortage_quantity",
    "reorder_level",
    "supplier_lead_time",
    "supplier_historical_delay",
    "processing_time",
    "shipping_time",
    "day_of_week",
    "month",
]


def generate_synthetic_training_data(size: int = 600, seed: int = 42):
    generator = random.Random(seed)
    rows = []
    targets = []
    for _ in range(size):
        quantity = generator.randint(1, 80)
        item_count = generator.randint(1, 8)
        order_value = round(generator.uniform(20, 8000), 2)
        current_stock = generator.randint(0, 500)
        shortage = generator.randint(0, quantity // 2)
        reorder_level = generator.randint(5, 80)
        lead_time = generator.randint(1, 21)
        supplier_delay = generator.randint(0, 8)
        processing = generator.randint(1, 4)
        shipping = generator.randint(1, 7)
        day = generator.randint(0, 6)
        month = generator.randint(1, 12)
        rows.append([
            quantity, item_count, order_value, current_stock, shortage,
            reorder_level, lead_time, supplier_delay, processing, shipping,
            day, month,
        ])
        targets.append(max(1, processing + shipping + lead_time + supplier_delay + shortage // 10))
    return rows, targets
