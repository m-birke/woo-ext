from woocommerce import API


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
