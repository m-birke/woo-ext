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
