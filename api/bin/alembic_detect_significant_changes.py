import argparse
import ast
import pathlib

IMPORTANT = (
    "drop_column",
    "DROP COLUMN"
    "alter_type",
    "ALTER TYPE"
    "drop_table",
    "DROP TABLE"
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

                if stripped_line.startswith('def upgrade('):
                    in_upgrade = True
                if stripped_line.startswith('def downgrade('):
                    in_upgrade = False

                if in_upgrade:
                    # Split by '#' to ignore code comments
                    code_part = line.split('#')[0]
                    if code_part != "\n":
                        for op in operation_group:
                            if op in code_part:
                                operations.append(f"[{operation_level}] Migration de type {op}")

    except Exception as exc:
        print(f"Could not parse {file_path}: {exc}")
        raise exc

    return operations


def main(file_name, level):
    return check_migration(file_name, level)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name", type=str)
    parser.add_argument("level", type=str, default="important")
    args = parser.parse_args()

    main(file_name=args.file_name, level=args.level)
