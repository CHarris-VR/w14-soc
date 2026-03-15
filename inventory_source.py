from typing import Any
from asset import Asset
import requests
import os

NETBOX_API_URL = "https://my.api.mockaroo.com/ironclad/netbox/inventory.json"
QUALYS_API_URL = "https://my.api.mockaroo.com/ironclad/qualys/inventory.json"
CROWDSTRIKE_API_URL = "https://my.api.mockaroo.com/ironclad/crowdstrike/inventory.json"


class InventorySource:
    name: str = "base"

    def __init__(self, api_url: str):
        self.api_url = api_url

    def fetch_raw(self):
        headers = {
            "X-API-Key": os.environ.get("IRONCLAD_API_KEY")
        }
        r = requests.get(self.api_url, headers=headers, timeout=10)
        if r.status_code != 200:
            raise RuntimeError(f"{self.name} fetch failed ({r.status_code}): {r.text[:200]}")
        data = r.json()
        if not isinstance(data, list):
            raise RuntimeError(f"{self.name} returned unexpected JSON (expected list).")
        return data

    def normalize(self, record: dict[str, Any]) -> Asset:
        raise NotImplementedError
    
    def fetch_assets(self) -> list[Asset]:
        raw = self.fetch_raw()
        results = []
        for each_record in raw:
            results.append(self.normalize(each_record))

        return results
    
# Added Netbox Inventory Source class with normalization logic.
    
class NetboxInventorySource(InventorySource):
    name = "netbox"

    def normalize(self, record: dict[str, Any]) -> Asset:
        # TODO: Map NetBox schema fields based on your preview output.
        # Suggested schema fields (from your Mockaroo design):
        # id, device_name, primary_ip, platform, environment, tenant, ...
        return Asset(
            asset_id=str(record.get("id")),                 # TODO confirm key
            hostname=str(record.get("device_name")),        # TODO confirm key
            ip_address=record.get("primary_ip"),            # TODO confirm key
            os=record.get("platform"),                      # TODO confirm key
            environment=record.get("environment"),          # TODO confirm key
            owner_context=record.get("tenant"),             # TODO confirm key
            source=self.name,
            raw=record,
        )

 # Added Qualys Inventory Source class with normalization logic.
 #    
class QualysInventorySource(InventorySource):
    name = "qualys"

    def normalize(self, record: dict[str, Any]) -> Asset:
        # TODO: Map Qualys schema fields based on your preview output.
        # Suggested schema fields:
        # asset_id (UUID), hostname, ip_address, operating_system, asset_group, criticality, ...
        return Asset(
            asset_id=str(record.get("asset_id")),           # TODO confirm key
            hostname=str(record.get("hostname")),           # TODO confirm key
            ip_address=record.get("ip_address"),            # TODO confirm key
            os=record.get("operating_system"),              # TODO confirm key
            environment=record.get("asset_group"),          # TODO map group -> environment
            owner_context=None,                             # TODO if your schema has owner/team, map it
            source=self.name,
            raw=record,
        )
    
class CrowdstrikeInventorySource(InventorySource):
    name = "crowdstrike"

    def normalize(self, record: dict[str, Any]) -> Asset:
        # TODO: Map crowdstrike schema fields based on your preview output.
        # Suggested schema fields:
        # sensor_id, hostname, local_ip, os_version, logged_in_user, policy_applied, ...
        return Asset(
            asset_id=str(record.get("sensor_id")),          # TODO confirm key
            hostname=str(record.get("hostname")),           # TODO confirm key
            ip_address=record.get("local_ip"),              # TODO choose local_ip as primary
            os=record.get("os_version"),                    # TODO confirm key
            environment=None,                               # TODO if you have env-like field, map it
            owner_context=record.get("logged_in_user"),     # TODO confirm key
            source=self.name,
            raw=record,
        )


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


if __name__ == "__main__":

    NETBOX_URL = "https://my.api.mockaroo.com/netbox_inventory.json"
    QUALYS_URL = "https://my.api.mockaroo.com/qualys_inventory.json"
    CROWDSTRIKE_URL = "https://my.api.mockaroo.com/crowdstrike_inventory.json"

    preview_dataset("Netbox", NETBOX_URL)
    preview_dataset("Qualys", QUALYS_URL)
    preview_dataset("Crowdstrike", CROWDSTRIKE_URL)