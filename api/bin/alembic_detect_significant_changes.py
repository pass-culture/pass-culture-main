import argparse
import pathlib


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


def check_migration(file_name: str, operation_level: str = "important") -> list[str]:
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
                                operations.append(f"[{file_name.split('_')[1]}] {op}")

    except Exception as exc:
        print(f"Could not parse {file_path}: {exc}")
        raise exc

    return operations


def detect_changes(file_names) -> str | None:
    important_changes = []
    notable_changes = []
    for file_name in file_names:
        important_changes += check_migration(file_name, operation_level="important")
        notable_changes += check_migration(file_name, operation_level="notable")
    if important_changes or notable_changes:
        text = ""
        if important_changes:
            text += "===== Migrations importantes =====\\n"
            text += "\\n".join(important_changes)
            text += "\\n"
        if notable_changes:
            text += "===== Migrations notables =====\\n"
            text += "\\n".join(notable_changes)
        return text

    return None


def main(file_names):
    print(detect_changes(file_names))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=str)
    args = parser.parse_args()

    main(file_names=args.files)
