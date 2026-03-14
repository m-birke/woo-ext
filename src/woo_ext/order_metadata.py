def pseudonymize_order_data(order: dict) -> dict:
    """Pseudonymizes the order data by only keeping the order_id and removing all other
    personally identifiable information (PII)"""
    pseudonymized_order = {"order_id": ""}
    if not order:
        return pseudonymized_order

    pseudonymized_order["order_id"] = order.get("order_id", "")

    return pseudonymized_order


def condense_order_data(order: dict, metadata_keys: list[str] | None = None) -> dict:
    """Extracts the important meta data out of a woocommerce order item

    At the moment:

    * order_id
    * mail_addr
    * date_paid
    * payment_method
    * product_id
    * status
    * coupon [optional]
    * Additional keys from the order's meta_data section

    Additionally adds a field named 'system' with value 'woocommerce' for better traceability.

    """

    order_meta = {"order_id": order["id"]}
    order_meta["date_paid"] = order["date_paid"]
    order_meta["mail_addr"] = order["billing"]["email"]
    order_meta["payment_method"] = order["payment_method"]
    order_meta["status"] = order["status"]
    order_meta["system"] = "woocommerce"
    try:
        order_meta["product_id"] = order["line_items"][0]["product_id"]
    except IndexError:
        order_meta["product_id"] = None

    if order["coupon_lines"]:
        # TODO what if there are more than one coupons ?
        order_meta["coupon"] = order["coupon_lines"][0]["code"]

    if not metadata_keys:
        return order_meta

    wc_order_metadata_list: list[dict] = order["meta_data"]
    for el in wc_order_metadata_list:
        for key in metadata_keys:
            if el.get("key") == key:
                order_meta[key] = el["value"]

    return order_meta
