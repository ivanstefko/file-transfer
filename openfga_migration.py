import requests
import json
import pymysql
import traceback

OLD_FGA_API = "http://localhost:8080"
NEW_FGA_API = "http://localhost:8081"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "dhjkvLVlHc",
    "database": "openfga_eng",
    "port": 3306
}

def get_stores(api_url):
    r = requests.get(f"{api_url}/stores")
    return r.json()["stores"]

def get_models_from_api(store_id):
    r = requests.get(f"{OLD_FGA_API}/stores/{store_id}/authorization-models")
    models = r.json().get("authorization_models", [])
    out = {}
    for m in models:
        mid = m["id"]
        detail = requests.get(f"{OLD_FGA_API}/stores/{store_id}/authorization-models/{mid}").json()
        defs = detail.get("authorization_model", {}).get("type_definitions", [])
        out.setdefault(store_id, {})[mid] = defs
    return out

def get_tuples_from_db(store_id):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT `_user`, relation, object FROM tuple WHERE store = %s", (store_id,))
            rows = cur.fetchall()
            return [{"user": u, "relation": r, "object": o} for u, r, o in rows]
    except Exception as e:
        print(f"  ERROR reading tuples for store {store_id}: {e}")
        traceback.print_exc()
        return []
    finally:
        conn.close()

def create_store():
    name = "migrated_store"
    r = requests.post(f"{NEW_FGA_API}/stores", json={"name": name})
    if r.status_code != 201:
        print("  ERROR creating store:", r.status_code, r.text)
        raise Exception("Store creation failed")
    data = r.json()
    if "id" not in data:
        print("  ERROR: Response missing 'id' key:", data)
        raise KeyError("Response missing 'id' field")
    return data["id"]

def create_model(store_id, body):
    r = requests.post(f"{NEW_FGA_API}/stores/{store_id}/authorization-models", json=body)
    if r.status_code != 201:
        print(f"  Model body:", json.dumps(body, indent=2))
        raise Exception(f"Model creation failed: {r.status_code} {r.text}")
    return r.json()["authorization_model_id"]

def create_tuples(store_id, tuples):
    chunk_size = 25
    for i in range(0, len(tuples), chunk_size):
        chunk = tuples[i:i+chunk_size]
        r = requests.post(f"{NEW_FGA_API}/stores/{store_id}/write", json={"writes": {"tuple_keys": chunk}})
        if r.status_code != 200:
            print(f"  ERROR writing tuples chunk: {r.status_code} {r.text}")

def fix_schema_version_and_metadata(defs):
    fixed = []
    for td in defs:
        if "relations" in td:
            if td.get("metadata") is None:
                td["metadata"] = {}
            if "relations" not in td["metadata"]:
                td["metadata"]["relations"] = {}
            for r in td["relations"]:
                if r not in td["metadata"]["relations"]:
                    td["metadata"]["relations"][r] = {"directly_related_user_types": ["user"]}
                elif not td["metadata"]["relations"][r].get("directly_related_user_types"):
                    td["metadata"]["relations"][r]["directly_related_user_types"] = ["user"]
        fixed.append(td)
    return fixed

def migrate():
    stores = get_stores(OLD_FGA_API)
    print(f"Migrating {len(stores)} stores...\n")
    for s in stores:
        old_store = s["id"]
        print(f"Store: {old_store}")
        new_store = create_store()
        print(f"Created new store: {new_store}")

        models = get_models_from_api(old_store)
        if old_store in models:
            for _, defs in models[old_store].items():
                if not defs:
                    print("  Skipping empty model definition")
                    continue
                fixed_model = fix_schema_version_and_metadata(defs)
                body = {"schema_version": "1.1", "type_definitions": fixed_model}
                try:
                    model_id = create_model(new_store, body)
                    print(f"  Created model: {model_id}")
                except Exception as e:
                    print(f"  Failed to create model: {e}")

        tuples = get_tuples_from_db(old_store)
        if tuples:
            create_tuples(new_store, tuples)
            print(f"  Migrated {len(tuples)} tuples")

if __name__ == "__main__":
    migrate()
