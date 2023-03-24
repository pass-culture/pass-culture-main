import sqlalchemy as sqla

from pcapi.alembic.run_migrations import include_object


class RunMigrationsTest:
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
