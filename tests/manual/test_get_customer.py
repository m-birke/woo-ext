"""Manual integration test for get_customer function.

This test requires the following environment variables:
    - WOO_URL: WooCommerce site URL (e.g., https://example.com)
    - WOO_CONSUMER_KEY: WooCommerce REST API consumer key
    - WOO_CONSUMER_SECRET: WooCommerce REST API consumer secret
    - WOO_CUSTOMER_ID: Customer ID to fetch (must be a valid integer)

Usage:
    WOO_URL=https://example.com \\
    WOO_CONSUMER_KEY=ck_xxx \\
    WOO_CONSUMER_SECRET=cs_xxx \\
    WOO_CUSTOMER_ID=123 \\
    python tests/manual/test_get_customer.py
"""

import os
import sys

from woo_ext.customers import get_customer
from woo_ext.utils import init_wc_client


def main() -> None:
    """Run manual integration test for get_customer."""
    # Get environment variables
    woo_url = os.getenv("WOO_URL")
    woo_consumer_key = os.getenv("WOO_CONSUMER_KEY")
    woo_consumer_secret = os.getenv("WOO_CONSUMER_SECRET")
    woo_customer_id = os.getenv("WOO_CUSTOMER_ID")

    # Validate environment variables
    if not woo_url:
        print("Error: WOO_URL environment variable not set", file=sys.stderr)
        sys.exit(1)

    if not woo_consumer_key:
        print("Error: WOO_CONSUMER_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    if not woo_consumer_secret:
        print("Error: WOO_CONSUMER_SECRET environment variable not set", file=sys.stderr)
        sys.exit(1)

    if not woo_customer_id:
        print("Error: WOO_CUSTOMER_ID environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Parse customer ID
    try:
        customer_id = int(woo_customer_id)
    except ValueError:
        print(f"Error: WOO_CUSTOMER_ID must be a valid integer, got: {woo_customer_id}", file=sys.stderr)
        sys.exit(1)

    # Initialize WooCommerce API client
    print("Initializing WooCommerce API client...")
    try:
        wc_client = init_wc_client(
            url=woo_url,
            consumer_key=woo_consumer_key,
            consumer_secret=woo_consumer_secret,
        )
        print("✓ API client initialized successfully")
    except Exception as e:
        print(f"Error: Failed to initialize API client: {e}", file=sys.stderr)
        sys.exit(1)

    # Fetch customer
    print(f"\nFetching customer with ID: {customer_id}...")
    try:
        customer = get_customer(wc_client, customer_id)
        print("✓ Customer fetched successfully\n")
    except ValueError as e:
        print(f"Error: Invalid input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to fetch customer: {e}", file=sys.stderr)
        sys.exit(1)

    if customer is None:
        print(f"Error: No customer found with ID: {customer_id}", file=sys.stderr)
        sys.exit(1)

    # Print customer object
    print("=" * 60)
    print("WooCustomer Object:")
    print("=" * 60)
    print(customer)
    print("=" * 60)
    print("\nFormatted Output:")
    print(f"  ID:         {customer.id}")
    print(f"  Email:      {customer.email}")
    print(f"  First Name: {customer.first_name or 'N/A'}")
    print(f"  Last Name:  {customer.last_name or 'N/A'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
