from woocommerce import API

from woo_ext.data_models import WooMetaDatum


def parse_woo_order_meta_data(meta_data: list[dict]) -> list[WooMetaDatum]:
    return [WooMetaDatum(id=el["id"], key=el["key"], value=el["value"]) for el in meta_data]


def get_order_meta_data(wc_client: API, order_id: int) -> list[WooMetaDatum]:
    order = wc_client.get(f"orders/{order_id}").json()
    return parse_woo_order_meta_data(order["meta_data"])


def extract_order_meta_data_from_key(meta_data: list[WooMetaDatum], meta_data_key: str) -> WooMetaDatum | None:
    for el in meta_data:
        if el.key == meta_data_key:
            return el
    return None


def add_order_meta_data(wc_client: API, order_id: int, meta_datum: WooMetaDatum) -> None:
    payload = {"meta_data": [{"key": meta_datum.key, "value": meta_datum.value}]}
    response = wc_client.put(f"orders/{order_id}", payload)
    response.raise_for_status()


def delete_order_meta_data(wc_client: API, order_id: int, meta_data_key: str) -> None:
    meta_data = get_order_meta_data(wc_client=wc_client, order_id=order_id)

    meta_datum = extract_order_meta_data_from_key(meta_data=meta_data, meta_data_key=meta_data_key)
    if not meta_datum:
        msg = f"Did not find {meta_data_key} in meta_data of order {order_id}"
        raise ValueError(msg)

    data = {"meta_data": [{"id": meta_datum.id, "value": None}]}

    response = wc_client.put(f"orders/{order_id}", data)
    response.raise_for_status()


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
