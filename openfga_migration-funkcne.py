import requests
import mysql.connector
import json

# 🔧 Konfigurácia
OLD_FGA_API = "http://localhost:8080"
NEW_FGA_API = "http://localhost:8081"

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "dhjkvLVlHc"
MYSQL_DB = "openfga_eng"

ALLOWED_SCHEMA_VERSIONS = ["1.1", "1.2"]
DEFAULT_SCHEMA_VERSION = "1.1"

# 🔌 Pripojenie k DB
db_conn = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)

def get_stores():
    r = requests.get(f"{OLD_FGA_API}/stores")
    r.raise_for_status()
    return r.json().get("stores", [])

def get_latest_model(store_id):
    resp = requests.get(f"{OLD_FGA_API}/stores/{store_id}/authorization-models").json()
    models = resp.get("authorization_models", [])
    if not models:
        return None, None
    latest = models[-1]
    model_id = latest["id"]
    full_model = requests.get(f"{OLD_FGA_API}/stores/{store_id}/authorization-models/{model_id}").json()
    return full_model.get("authorization_model", full_model), model_id

def get_tuples_from_db(store_id):
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT object_type, object_id, relation, _user
        FROM tuple
        WHERE store = %s
    """, (store_id,))
    results = []
    for row in cursor.fetchall():
        obj = f"{row['object_type']}:{row['object_id']}"
        user = row['_user']
        results.append({
            "user": user,
            "relation": row["relation"],
            "object": obj
        })
    return results

def has_this_relation(relation_def):
    if not isinstance(relation_def, dict):
        return False
    if "this" in relation_def:
        return True
    for key in ["union", "intersection", "difference"]:
        if key in relation_def:
            children = relation_def[key].get("child", [])
            return any(has_this_relation(child) for child in children if isinstance(child, dict))
    if "rewrite" in relation_def:
        return has_this_relation(relation_def["rewrite"])
    return False

def fix_schema_version_and_metadata(model, tuples):
    version = model.get("schema_version")
    if version not in ALLOWED_SCHEMA_VERSIONS:
        print(f"⚠️ Fixing schema_version from '{version}' → '{DEFAULT_SCHEMA_VERSION}'")
        model["schema_version"] = DEFAULT_SCHEMA_VERSION

    all_assignable_relations = set()

    for t in model.get("type_definitions", []):
        t.setdefault("relations", {})
        used = set(t["relations"].keys())

        def find_relations(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "relation" and isinstance(v, str):
                        used.add(v)
                    find_relations(v)
            elif isinstance(obj, list):
                for item in obj:
                    find_relations(item)

        find_relations(t["relations"])

        for r in used:
            if r not in t["relations"]:
                print(f"➕ Adding missing relation '{r}' to type '{t['type']}'")
                t["relations"][r] = { "this": {} }

        metadata = {"relations": {}}
        for r, rel_def in t["relations"].items():
            if has_this_relation(rel_def):
                metadata["relations"][r] = {
                    "directly_related_user_types": [{ "type": "user" }]
                }
                all_assignable_relations.add(r)

        t["metadata"] = metadata

    user_type = next((t for t in model["type_definitions"] if t["type"] == "user"), None)
    if user_type:
        user_type.setdefault("relations", {})
        user_type.setdefault("metadata", { "relations": {} })

        for rel in all_assignable_relations:
            if rel not in user_type["relations"]:
                print(f"🛠️ Patching assignable relation '{rel}' into type 'user'")
                user_type["relations"][rel] = { "this": {} }
            if rel not in user_type["metadata"]["relations"]:
                user_type["metadata"]["relations"][rel] = {
                    "directly_related_user_types": [{ "type": "user" }]
                }

    return model

def create_store(store_name):
    r = requests.post(f"{NEW_FGA_API}/stores", json={"name": store_name})
    if not r.ok:
        print(f"❌ Failed to create store '{store_name}': {r.text}")
        return None
    return r.json()["id"]

def upload_model(store_id, model):
    r = requests.post(f"{NEW_FGA_API}/stores/{store_id}/authorization-models", json=model)
    if not r.ok:
        print(f"❌ Failed to upload model to store {store_id}: {r.text}")
        return False
    return True

def write_tuples(store_id, tuples):
    BATCH = 100
    for i in range(0, len(tuples), BATCH):
        batch = tuples[i:i+BATCH]
        payload = {
            "writes": {
                "tuple_keys": [
                    {
                        "user": t["user"],
                        "relation": t["relation"],
                        "object": t["object"]
                    } for t in batch
                ]
            }
        }
        r = requests.post(f"{NEW_FGA_API}/stores/{store_id}/write", json=payload)
        if not r.ok:
            print(f"❌ Failed to write tuples: {r.text}")

def migrate_store(store):
    store_id = store["id"]
    print(f"\n➡️ Migrating store: {store_id}")

    model, model_id = get_latest_model(store_id)
    if not model:
        print(f"⚠️ No model found for store {store_id}")
        return

    tuples = get_tuples_from_db(store_id)
    patched_model = fix_schema_version_and_metadata(model, tuples)

    new_store_id = create_store(store_id)
    if not new_store_id:
        return

    if not upload_model(new_store_id, patched_model):
        return

    write_tuples(new_store_id, tuples)
    print(f"✅ Done: {store_id} ➝ {new_store_id} | {len(tuples)} tuples migrated")

def main():
    stores = get_stores()
    for store in stores:
        migrate_store(store)

if __name__ == "__main__":
    main()
