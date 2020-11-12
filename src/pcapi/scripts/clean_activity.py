from typing import List

from pcapi.models.db import db


def delete_tables_from_activity(tables: List[str]):
    tables_with_quotes = [f"'{table}'" for table in tables]
    tables_as_str = ", ".join(tables_with_quotes)
    query = f"""
        DELETE FROM activity WHERE table_name IN ({tables_as_str})
    """
    db.engine.execute(query)
