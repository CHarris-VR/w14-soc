import requests
import os
from typing import Any


NETBOX_API_URL = "https://my.api.mockaroo.com/ironclad/netbox/inventory.json"
QUALYS_API_URL = "https://my.api.mockaroo.com/ironclad/qualys/inventory.json"
CROWDSTRIKE_API_URL = "https://my.api.mockaroo.com/ironclad/crowdstrike/inventory.json"


def fetch_json(url: str) -> list[dict[str, Any]]:
    headers = {
        "X-API-Key": os.environ.get("IRONCLAD_API_KEY")
    }
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"GET failed ({r.status_code}): {r.text[:200]}")
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError("Expected a list of records from the API.")
    # ensure dict-like records
    for i, rec in enumerate(data[:3]):
        if not isinstance(rec, dict):
            raise RuntimeError(f"Record {i} is not an object/dict.")
    return data


def preview_dataset(name: str, url: str) -> None:
    data = fetch_json(url)
    print(f"\n=== {name} PREVIEW ===")
    print(f"Records: {len(data)}")
    print("First record:")
    print(data[0])
    print("Fields:")
    for k in data[0].keys():
        print(" -", k)

def main():
    preview_dataset("NETBOX", NETBOX_API_URL)
    preview_dataset("QUALYS", QUALYS_API_URL)
    preview_dataset("CROWDSTRIKE", CROWDSTRIKE_API_URL)

    # Test Successful up to this pointt.