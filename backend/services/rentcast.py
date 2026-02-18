"""
RentCast API client for property value by address (AVM).
Free tier: 50 requests/month. Get a key at https://rentcast.io/ (developer signup).
"""

import os
import requests

BASE_URL = "https://api.rentcast.io/v1"


def get_api_key() -> str:
    key = os.environ.get("RENTCAST_API_KEY")
    if not key:
        raise ValueError(
            "RENTCAST_API_KEY is not set. "
            "Sign up at https://rentcast.io/ and add your API key to .env"
        )
    return key


def get_value_by_address(address: str) -> dict:
    """
    Get current property value estimate for a US address.

    Address format: "Street, City, State, Zip" (e.g. "123 Main St, Austin, TX, 78701").

    Returns dict with: price, priceRangeLow, priceRangeHigh, formattedAddress,
    and optionally subjectProperty details. Raises ValueError on API error or missing key.
    """
    api_key = get_api_key()
    address = (address or "").strip()
    if not address:
        raise ValueError("Address is required")

    headers = {"X-Api-Key": api_key}
    params = {"address": address}
    resp = requests.get(
        f"{BASE_URL}/avm/value",
        headers=headers,
        params=params,
        timeout=30,
    )

    if resp.status_code == 401:
        raise ValueError("Invalid RENTCAST_API_KEY or key not activated")
    if resp.status_code == 404:
        raise ValueError("Address not found or no value estimate available")
    if resp.status_code == 429:
        raise ValueError("RentCast rate limit exceeded (50 free requests/month)")
    resp.raise_for_status()

    data = resp.json()
    # Normalize response for our API
    subject = data.get("subjectProperty") or {}
    return {
        "address": address,
        "formattedAddress": subject.get("formattedAddress") or address,
        "price": data.get("price"),
        "priceRangeLow": data.get("priceRangeLow"),
        "priceRangeHigh": data.get("priceRangeHigh"),
        "subjectProperty": subject,
    }
