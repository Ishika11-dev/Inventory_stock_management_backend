def build_delivery_features(
    order_quantity: int,
    number_of_items: int,
    current_stock: int,
    reorder_level: int,
    supplier_lead_time: int,
    processing_time: int,
    shipping_time: int,
) -> dict:

    shortage_quantity = max(
        order_quantity - current_stock,
        0
    )

    return {
        "order_quantity": order_quantity,
        "number_of_items": number_of_items,
        "current_stock": current_stock,
        "reorder_level": reorder_level,
        "shortage_quantity": shortage_quantity,
        "supplier_lead_time": supplier_lead_time,
        "processing_time": processing_time,
        "shipping_time": shipping_time,
    }