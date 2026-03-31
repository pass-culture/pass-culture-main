import argparse
import json
import pathlib
import re
import urllib.request

IMPORTANT = (
    "drop_column",
    "DROP COLUMN",
    "alter_type",
    "ALTER TYPE",
    "drop_table",
    "DROP TABLE",
    "rename_table",
    "RENAME TO",
    "new_column_name",
    "RENAME COLUMN",
)
NOTABLE = (
    "add_column",
    "ADD COLUMN",
    "create_table",
    "CREATE TABLE",
)
CREATION_OPS = ("create_table", "CREATE TABLE")

REPO_TREE_URL = "https://api.github.com/repos/pass-culture/data-gcp/git/trees/"
SQL_PREFIX = "orchestration/dags/dependencies/applicative_database/sql/"
EXCLUDED_SUBFOLDERS = ["history"]

BRANCH_ENV = {"production": "prod", "master": "stg", "test-fake-table": "fake-env"}


def fetch_data_imported_tables(branch: str) -> set[str]:
    with urllib.request.urlopen(f"{REPO_TREE_URL}{branch}?recursive=1") as response:
        tree = json.load(response)["tree"]
    return {
        item["path"].split("/")[-1].replace(".sql", "")
        for item in tree
        if item["path"].startswith(SQL_PREFIX)
        and item["path"].endswith(".sql")
        and not any(f"/{folder}/" in item["path"] for folder in EXCLUDED_SUBFOLDERS)
    }


def extract_table_name(code_part: str) -> str | None:
    match = re.search(r'op\.(?!execute)\w+\(\s*["\'](\w+)["\']', code_part)
    if match:
        return match.group(1)
    match = re.search(r'(?:CREATE|ALTER|DROP|RENAME)\s+TABLE\s+(\w+)', code_part, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def check_migration(file_name: str, operation_level: str = "important") -> list[dict]:
    operation_group = IMPORTANT if operation_level == "important" else NOTABLE
    file_path = pathlib.Path(file_name)
    operations = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            in_upgrade = False
            for line in f:
                stripped_line = line.strip()
                if stripped_line.startswith("def upgrade("):
                    in_upgrade = True
                if stripped_line.startswith("def downgrade("):
                    in_upgrade = False
                if in_upgrade:
                    # Split by '#' to ignore code comments
                    code_part = line.split("#")[0]
                    if code_part != "\n":
                        for op in operation_group:
                            if op in code_part:
                                # the hash in the migration file name
                                operations.append({
                                    "hash": file_name.split("_")[1],
                                    "op": op,
                                    "table": extract_table_name(code_part),
                                })
    except Exception as exc:
        print(f"Could not parse {file_path}: {exc}")
        raise exc
    return operations


def detect_changes(file_names, tables_subset) -> str | None:
    important_changes = []
    notable_changes = []
    for file_name in file_names:
        important_changes += check_migration(file_name, operation_level="important")
        notable_changes += check_migration(file_name, operation_level="notable")

    important_changes = [
        c for c in important_changes
        if c["table"] in tables_subset
    ]
    notable_changes = [
        c for c in notable_changes
        if c["op"] in CREATION_OPS
        or c["table"] in tables_subset
    ]

    if important_changes or notable_changes:
        text = ""
        if important_changes:
            text += "===== Migrations importantes =====\\n"
            text += "\\n".join(f"[{c['hash']}] {c['op']} ({c['table']})" for c in important_changes)
            text += "\\n"
        if notable_changes:
            text += "===== Migrations notables =====\\n"
            text += "\\n".join(f"[{c['hash']}] {c['op']} ({c['table']})" for c in notable_changes)
            text += "\\n"
        return text
    return None


def main(file_names):
    import sys
    results = []
    for branch, env in BRANCH_ENV.items():
        imported_tables = fetch_data_imported_tables(branch)
        print(f"[DEBUG] {branch}: {imported_tables}", file=sys.stderr)  # ← temp
        result = detect_changes(file_names, imported_tables)
        if result:
            results.append(f"[{env.upper()}]\\n{result}")
    if results:
        print("\\n".join(results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=str)
    args = parser.parse_args()
    main(file_names=args.files)
