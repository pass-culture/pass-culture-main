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

OP_DISPLAY = {
    "drop_column": "drop_column",
    "DROP COLUMN": "drop_column",
    "alter_type": "alter_type",
    "ALTER TYPE": "alter_type",
    "drop_table": "drop_table",
    "DROP TABLE": "drop_table",
    "rename_table": "rename_table",
    "RENAME TO": "rename_table",
    "new_column_name": "rename_column",
    "RENAME COLUMN": "rename_column",
    "add_column": "add_column",
    "ADD COLUMN": "add_column",
    "create_table": "create_table",
    "CREATE TABLE": "create_table",
}

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


def extract_operation_details(code_part: str) -> dict:
    # batch_alter_table('table')
    match = re.search(r'op\.batch_alter_table\(\s*["\'](\w+)["\']', code_part)
    if match:
        return {"table": match.group(1), "column": None, "rename_to": None}

    # op.add_column('table', sa.Column('column', ...))
    match = re.search(r'op\.(?!execute)\w+\(\s*["\'](\w+)["\'](?:,\s*(?:\w+\.)*\w+\(["\'](\w+)["\'])?', code_part)
    if match:
        return {"table": match.group(1), "column": match.group(2), "rename_to": None}

    # raw SQL: ALTER TABLE table RENAME COLUMN old TO new
    match = re.search(r'(?:ALTER|DROP|RENAME)\s+TABLE\s+(?:\w+\.)?(\w+)\s*(?:RENAME\s+COLUMN\s+(\w+)\s+TO\s+(\w+))?', code_part, re.IGNORECASE)
    if match:
        return {"table": match.group(1), "column": match.group(2), "rename_to": match.group(3)}

    # CREATE TABLE
    match = re.search(r'CREATE\s+TABLE\s+(?:\w+\.)?(\w+)', code_part, re.IGNORECASE)
    if match:
        return {"table": match.group(1), "column": None, "rename_to": None}

    return {"table": None, "column": None, "rename_to": None}


def format_change(c: dict) -> str:
    table = c["table"] or "unknown"
    op = c["op"]
    col = c["column"]
    rename_to = c["rename_to"]

    if op == "rename_column" and col and rename_to:
        detail = f"{table}.{col} → {table}.{rename_to}"
    elif col:
        detail = f"{table}.{col}"
    else:
        detail = table

    return f"[{c['hash']}] {op} ({detail})"


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
                                details = extract_operation_details(code_part)
                                operations.append({
                                    "hash": file_name.split("_")[1],
                                    "op": OP_DISPLAY[op],
                                    "table": details["table"],
                                    "column": details["column"],
                                    "rename_to": details["rename_to"],
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
            text += "\\n".join(format_change(c) for c in important_changes)
            text += "\\n"
        if notable_changes:
            text += "===== Migrations notables =====\\n"
            text += "\\n".join(format_change(c) for c in notable_changes)
            text += "\\n"
        return text
    return None



def main(file_names):
    import sys
    results = []
    for branch, env in BRANCH_ENV.items():
        imported_tables = fetch_data_imported_tables(branch)
        result = detect_changes(file_names, imported_tables)
        print(f"Checked against {env} imported tables: {imported_tables}", file=sys.stderr)
        if result:
            results.append(f"[{env.upper()}]\\n{result}")
    if results:
        print("\\n".join(results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=str)
    args = parser.parse_args()
    main(file_names=args.files)
