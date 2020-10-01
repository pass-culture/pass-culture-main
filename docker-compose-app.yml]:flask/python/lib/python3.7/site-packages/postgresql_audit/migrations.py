import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from .expressions import jsonb_change_key_name


def get_activity_table(schema=None):
    return sa.Table(
        'activity',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('table_name', sa.String),
        sa.Column('verb', sa.String),
        sa.Column('old_data', JSONB),
        sa.Column('changed_data', JSONB),
        schema=schema,
    )


def alter_column(conn, table, column_name, func, schema=None):
    """
    Run given callable against given table and given column in activity table
    jsonb data columns. This function is useful when you want to reflect type
    changes in your schema to activity table.

    In the following example we change the data type of User's age column from
    string to integer.


    ::

        from alembic import op
        from postgresql_audit import alter_column


        def upgrade():
            op.alter_column(
                'user',
                'age',
                type_=sa.Integer
            )

            alter_column(
                op,
                'user',
                'age',
                lambda value, activity_table: sa.cast(value, sa.Integer)
            )


    :param conn:
        An object that is able to execute SQL (either SQLAlchemy Connection,
        Engine or Alembic Operations object)
    :param table:
        The table to run the column name changes against
    :param column_name:
        Name of the column to run callable against
    :param func:
        A callable to run against specific column in activity table jsonb data
        columns. The callable should take two parameters the jsonb value
        corresponding to given column_name and activity table object.
    :param schema:
        Optional name of schema to use.
    """
    activity_table = get_activity_table(schema=schema)
    query = (
        activity_table
        .update()
        .values(
            old_data=(
                activity_table.c.old_data +
                sa.cast(sa.func.json_build_object(
                    column_name,
                    func(
                        activity_table.c.old_data[column_name],
                        activity_table
                    )
                ), JSONB)
            ),
            changed_data=(
                activity_table.c.changed_data +
                sa.cast(sa.func.json_build_object(
                    column_name,
                    func(
                        activity_table.c.changed_data[column_name],
                        activity_table
                    )
                ), JSONB)
            )
        )
        .where(activity_table.c.table_name == table)
    )
    return conn.execute(query)


def change_column_name(
    conn,
    table,
    old_column_name,
    new_column_name,
    schema=None
):
    """
    Changes given `activity` jsonb data column key. This function is useful
    when you want to reflect column name changes to activity table.

    ::

        from alembic import op
        from postgresql_audit import change_column_name


        def upgrade():
            op.alter_column(
                'my_table',
                'my_column',
                new_column_name='some_column'
            )

            change_column_name(op, 'my_table', 'my_column', 'some_column')


    :param conn:
        An object that is able to execute SQL (either SQLAlchemy Connection,
        Engine or Alembic Operations object)
    :param table:
        The table to run the column name changes against
    :param old_column_name:
        Name of the column to change
    :param new_column_name:
        New colum name
    :param schema:
        Optional name of schema to use.
    """
    activity_table = get_activity_table(schema=schema)
    query = (
        activity_table
        .update()
        .values(
            old_data=jsonb_change_key_name(
                activity_table.c.old_data,
                old_column_name,
                new_column_name
            ),
            changed_data=jsonb_change_key_name(
                activity_table.c.changed_data,
                old_column_name,
                new_column_name
            )
        )
        .where(activity_table.c.table_name == table)
    )
    return conn.execute(query)


def add_column(conn, table, column_name, default_value=None, schema=None):
    """
    Adds given column to `activity` table jsonb data columns.

    In the following example we reflect the changes made to our schema to
    activity table.

    ::

        import sqlalchemy as sa
        from alembic import op
        from postgresql_audit import add_column


        def upgrade():
            op.add_column('article', sa.Column('created_at', sa.DateTime()))
            add_column(op, 'article', 'created_at')


    :param conn:
        An object that is able to execute SQL (either SQLAlchemy Connection,
        Engine or Alembic Operations object)
    :param table:
        The table to remove the column from
    :param column_name:
        Name of the column to add
    :param default_value:
        The default value of the column
    :param schema:
        Optional name of schema to use.
    """
    activity_table = get_activity_table(schema=schema)
    data = {column_name: default_value}
    query = (
        activity_table
        .update()
        .values(
            old_data=sa.case(
                [
                    (
                        sa.cast(activity_table.c.old_data, sa.Text) != '{}',
                        activity_table.c.old_data + data
                    ),
                ],
                else_=sa.cast({}, JSONB)
            ),
            changed_data=sa.case(
                [
                    (
                        sa.and_(
                            sa.cast(
                                activity_table.c.changed_data,
                                sa.Text
                            ) != '{}',
                            activity_table.c.verb != 'update'
                        ),
                        activity_table.c.changed_data + data
                    )
                ],
                else_=activity_table.c.changed_data
            ),
        )
        .where(activity_table.c.table_name == table)
    )
    return conn.execute(query)


def remove_column(conn, table, column_name, schema=None):
    """
    Removes given `activity` jsonb data column key. This function is useful
    when you are doing schema changes that require removing a column.

    Let's say you've been using PostgreSQL-Audit for a while for a table called
    article. Now you want to remove one audited column called 'created_at' from
    this table.

    ::

        from alembic import op
        from postgresql_audit import remove_column


        def upgrade():
            op.remove_column('article', 'created_at')
            remove_column(op, 'article', 'created_at')


    :param conn:
        An object that is able to execute SQL (either SQLAlchemy Connection,
        Engine or Alembic Operations object)
    :param table:
        The table to remove the column from
    :param column_name:
        Name of the column to remove
    :param schema:
        Optional name of schema to use.
    """
    activity_table = get_activity_table(schema=schema)
    remove = sa.cast(column_name, sa.Text)
    query = (
        activity_table
        .update()
        .values(
            old_data=activity_table.c.old_data - remove,
            changed_data=activity_table.c.changed_data - remove,
        )
        .where(activity_table.c.table_name == table)
    )
    return conn.execute(query)


def rename_table(conn, old_table_name, new_table_name, schema=None):
    """
    Renames given table in activity table. You should remember to call this
    function whenever you rename a versioned table.

    ::

        from alembic import op
        from postgresql_audit import rename_table


        def upgrade():
            op.rename_table('article', 'article_v2')
            rename_table(op, 'article', 'article_v2')


    :param conn:
        An object that is able to execute SQL (either SQLAlchemy Connection,
        Engine or Alembic Operations object)
    :param old_table_name:
        The name of table to rename
    :param new_table_name:
        New name of the renamed table
    :param schema:
        Optional name of schema to use.
    """
    activity_table = get_activity_table(schema=schema)
    query = (
        activity_table
        .update()
        .values(table_name=new_table_name)
        .where(activity_table.c.table_name == old_table_name)
    )
    return conn.execute(query)
