# docs under https://developer.woocommerce.com/docs/apis/rest-api/v3/customers/

import requests
from woocommerce import API

from woo_ext.data_models import WooCustomer


def get_customer(wc_client: API, id: int) -> WooCustomer | None:
    """Retrieve a customer by ID.

    Fetches customer information from WooCommerce API and returns it as a
    validated WooCustomer object. If the customer does not exist (404 error),
    returns None instead of raising an exception.

    :param wc_client: initialized woocommerce API client
    :param id: ID of the customer to be fetched, must be a positive integer
    :return: WooCustomer object containing customer data (id, email, first_name, last_name),
             or None if the customer is not found (404 error)
    :raises ValueError: if id is not a positive integer
    :raises HTTPError: if the API request fails for reasons other than customer not found
    """
    if not id or id <= 0:
        msg = "To get a customer, 'id' must be a positive integer"
        raise ValueError(msg)

    try:
        response = wc_client.get(f"customers/{id}")
        response.raise_for_status()
        customer_data = response.json()
        return WooCustomer(**customer_data)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise
