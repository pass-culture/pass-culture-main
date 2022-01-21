from unittest.mock import patch

import sqlalchemy as sqla

from pcapi.alembic.run_migrations import include_object


class RunMigrationsTest:
    @patch(
        "pcapi.alembic.run_migrations.IGNORED_COLUMNS_BY_TABLE",
        {"table_3": ("ignored_name", "ignored_name_2")},
    )
    def test_exclude_columns_defined_in_ignored_columns_by_table(self, caplog):
        m = sqla.MetaData()
        price = sqla.Column("price", sqla.Float)
        sqla.Table("table_1", m, price)
        token = sqla.Column("token", sqla.Text)
        not_to_be_ignored_column = sqla.Column("ignored_name", sqla.Integer)
        sqla.Table("table_2", m, token, not_to_be_ignored_column)
        status = sqla.Column("status", sqla.Boolean)
        ignored_column = sqla.Column("ignored_name", sqla.Boolean)
        ignored_column_2 = sqla.Column("ignored_name_2", sqla.Boolean)
        sqla.Table("table_3", m, ignored_column, ignored_column_2, status, schema=None)

        # table_1 columns
        assert include_object(object=price, name="price", type_="column", reflected=False, compare_to=None)
        # table_2 columns
        assert include_object(object=token, name="token", type_="column", reflected=False, compare_to=None)
        assert include_object(
            object=not_to_be_ignored_column, name="ignored_name", type_="column", reflected=False, compare_to=None
        )
        # table_3 columns
        assert include_object(object=status, name="status", type_="column", reflected=False, compare_to=None)
        assert not include_object(
            object=ignored_column, name="ignored_name", type_="column", reflected=False, compare_to=None
        )
        assert not include_object(
            object=ignored_column_2, name="ignored_name_2", type_="column", reflected=False, compare_to=None
        )
        assert caplog.messages == [
            ">>>>> Ignoring column 'ignored_name' in table 'table_3' from IGNORED_COLUMNS_BY_TABLE <<<<<",
            ">>>>> Ignoring column 'ignored_name_2' in table 'table_3' from IGNORED_COLUMNS_BY_TABLE <<<<<",
        ]

    @patch(
        "pcapi.alembic.run_migrations.IGNORED_TABLES",
        ("ignored_table_name",),
    )
    def test_exclude_tables_defined_in_ignored_tables(self, caplog):
        m = sqla.MetaData()
        table_1 = sqla.Table("table_1", m)
        table_2 = sqla.Table("table_2", m)
        table_3 = sqla.Table("ignored_table_name", m)

        assert include_object(object=table_1, name="table_1", type_="table", reflected=False, compare_to=None)
        assert include_object(object=table_2, name="table_2", type_="table", reflected=False, compare_to=None)
        assert not include_object(
            object=table_3, name="ignored_table_name", type_="table", reflected=False, compare_to=None
        )
        assert caplog.messages == [
            ">>>>> Ignoring table 'ignored_table_name' from IGNORED_TABLES <<<<<",
        ]

    def test_exclude_tables_to_be_dropped(self, caplog):
        m = sqla.MetaData()
        table_1 = sqla.Table("table_1", m)
        table_2 = sqla.Table("table_2", m)
        table_to_be_dropped = sqla.Table("table_to_be_dropped", m)

        assert include_object(object=table_1, name="table_1", type_="table", reflected=False, compare_to=None)
        assert include_object(object=table_2, name="table_2", type_="table", reflected=False, compare_to=None)
        assert not include_object(
            object=table_to_be_dropped, name="ignored_table_name", type_="table", reflected=True, compare_to=None
        )
        assert caplog.messages == [
            ">>>>> Ignoring DROP TABLE for table 'table_to_be_dropped' <<<<<",
        ]
