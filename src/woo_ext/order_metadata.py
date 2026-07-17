from woocommerce import API

from woo_ext.data_models import (
    WooLineItem,
    WooMetaDatum,
    WooOrderCondensed,
    WooOrderPseudonomyzed,
)


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


def pseudonymize_order_data(order: WooOrderCondensed) -> WooOrderPseudonomyzed:
    """Pseudonymizes the order data by only keeping the order_id and removing all other
    personally identifiable information (PII)"""
    return WooOrderPseudonomyzed(order_id=order.order_id)


def parse_woo_line_items(line_items: list[dict]) -> list[WooLineItem]:
    """Convert WooCommerce `line_items` dicts into a list of `WooLineItem` models.

    - Skips entries without a valid `product_id`/`quantity`.
    - Coerces numeric fields when possible.
    """
    parsed: list[WooLineItem] = []
    for el in line_items or []:
        product_id = el.get("product_id")
        quantity = el.get("quantity", 0)

        if product_id is None:
            continue

        product_id = int(product_id)

        try:
            quantity = int(quantity)
        except Exception:
            quantity = 0

        name = el.get("name")

        price = el.get("price")
        if price is not None and price != "":
            try:
                price = float(price)
            except Exception:
                price = None

        parsed.append(WooLineItem(product_id=product_id, quantity=quantity, name=name, price=price))

    return parsed


def condense_order_data(order: dict) -> WooOrderCondensed:
    """Extracts the important meta data out of a woocommerce order item

    Additional keys from the order's meta_data section
    """

    line_items_parsed = parse_woo_line_items(order.get("line_items", []))

    if order["coupon_lines"]:
        # TODO handle more than one coupons
        coupon = order["coupon_lines"][0]["code"]
    else:
        coupon = None

    return WooOrderCondensed(
        order_id=order["id"],
        status=order["status"],
        date_paid=order["date_paid"],
        payment_method=order["payment_method"],
        line_items=line_items_parsed,
        mail_address=order["billing"]["email"],
        coupon=coupon,
    )
