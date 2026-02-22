import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from woocommerce import API

_API_TIMEOUT_RETRIES = 3
_API_TIMEOUT_SECONDS = 5
_API_VERSION = "wc/v3"


@retry(stop=stop_after_attempt(_API_TIMEOUT_RETRIES), wait=wait_fixed(_API_TIMEOUT_SECONDS), reraise=True)
def init_wc_client(url: str, consumer_key: str, consumer_secret: str, version: str = _API_VERSION) -> API:
    if not url or not consumer_key or not consumer_secret:
        msg = "To init the WooCommerce API client, 'url', 'consumer_key' and 'consumer_secret' must be set"
        raise ValueError(msg)

    wc_client = API(url=url, consumer_key=consumer_key, consumer_secret=consumer_secret, wp_api=True, version=version)
    wc_client.get("")  # to test connection

    return wc_client


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


def check_line_items(order: dict) -> bool:  # TODO make no line items a parameter
    """Checks whether exactly 1 line item with quantity 1 is present in order

    If yes returns True, else False
    """

    if len(order["line_items"]) != 1:
        return False

    if order["line_items"][0]["quantity"] != 1:
        return False

    return True


def get_paid_orders_after(wc_client: API, after: str) -> list[dict]:
    """View all the orders after a specific date which were paid.

    :param wc_client: initialized woocommerce API
    :param after: Limit response to resources published after a given ISO8601 (2022-01-04T22:18:45) compliant date.
    """
    if not after:
        msg = "To get the paid orders after a specific date, 'after' must have a valid value"
        raise ValueError(msg)

    orders_after = get_orders_after(wc_client, after)
    paid_orders = []
    for order in orders_after:
        if order["date_paid"] is not None:
            paid_orders.append(order)

    return paid_orders


def get_orders_after(wc_client: API, after: str) -> list[dict]:
    """View all the orders after a specific date

    :param wc_client: initialized woocommerce API
    :param after: Limit response to resources published after a given ISO8601 (2022-01-04T22:18:45) compliant date.
    """

    filtered_orders = get_orders_from_all_pages(wc_client, filter_str=f"&after={after}")
    return filtered_orders


def get_customer_mails(wc_client) -> list[str]:
    all_customer_mails = []

    all_orders = get_orders_from_all_pages(wc_client)

    for order in all_orders:
        billing_mail = order["billing"]["email"]
        if billing_mail != "":
            all_customer_mails.append(billing_mail.lower())

    return all_customer_mails


def get_orders_from_all_pages(wc_client, filter_str: str = "") -> list[dict]:
    """Given a filter string, all orders from all pages are fetched
    docs: https://woocommerce.github.io/woocommerce-rest-api-docs/?python#list-all-orders

    :param filter: given filter, various filters have to be separated by '&', must start with an '&', defaults to empty
    """

    orders = []
    page_number = 1

    while True:
        order_batch = wc_client.get(f"orders?page={page_number}{filter_str}").json()

        if len(order_batch) == 0:
            break

        orders.extend(order_batch)
        page_number += 1

    return orders


def get_field_of_all_orders(wc_client, key: str):
    """gets all values for a first level key in order dictionary"""
    all_values = []

    page_number = 1

    while True:
        order_batch = wc_client.get(f"orders?page={page_number}").json()

        if len(order_batch) == 0:
            break

        all_values += [order[key] for order in order_batch]

        page_number += 1

    return all_values


def test_connection(url: str, consumer_key: str, consumer_secret: str, version: str) -> None:
    woo = init_wc_client(url=url, consumer_key=consumer_key, consumer_secret=consumer_secret, version=version)

    try:
        response = woo.get("")
    except requests.exceptions.ConnectionError as e:
        print(f"Failed with exception: {e}")  # noqa T201
        return

    if response.status_code >= 200 and response.status_code < 210:  # noqa PLR2004
        print("Success")  # noqa T201
        return

    print(f"Status Code: {response.status_code}, Response: {response.text}")  # noqa T201
