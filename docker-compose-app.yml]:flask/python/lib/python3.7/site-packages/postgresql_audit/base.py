import os
import string
import warnings
from contextlib import contextmanager
from weakref import WeakSet

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import array, INET, JSONB
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import get_class_by_table

HERE = os.path.dirname(os.path.abspath(__file__))
cached_statements = {}


class ImproperlyConfigured(Exception):
    pass


class ClassNotVersioned(Exception):
    pass


class StatementExecutor(object):
    def __init__(self, stmt):
        self.stmt = stmt

    def __call__(self, target, bind, **kwargs):
        tx = bind.begin()
        bind.execute(self.stmt)
        tx.commit()


def read_file(file_):
    with open(os.path.join(HERE, file_)) as f:
        s = f.read()
    return s


def assign_actor(base, cls, actor_cls):
    if hasattr(cls, 'actor_id'):
        return
    if actor_cls:
        primary_key = sa.inspect(actor_cls).primary_key[0]

        cls.actor_id = sa.Column('actor_id', primary_key.type)
        cls.actor = orm.relationship(
            actor_cls,
            primaryjoin=cls.actor_id == (
                getattr(
                    actor_cls,
                    primary_key.name
                )
            ),
            foreign_keys=[cls.actor_id]
        )
    else:
        cls.actor_id = sa.Column(sa.Text)


def transaction_base(Base, schema):
    class Transaction(Base):
        __abstract__ = True
        __table_args__ = {'schema': schema}
        id = sa.Column(sa.BigInteger, primary_key=True)
        native_transaction_id = sa.Column(sa.BigInteger, index=True)
        issued_at = sa.Column(sa.DateTime)
        client_addr = sa.Column(INET)

        def __repr__(self):
            return '<{cls} id={id!r} issued_at={issued_at!r}>'.format(
                cls=self.__class__.__name__,
                id=self.id,
                issued_at=self.issued_at
            )

    return Transaction


def activity_base(Base, schema, transaction_cls):

    class ActivityBase(Base):
        __abstract__ = True
        __table_args__ = {'schema': schema}
        id = sa.Column(sa.BigInteger, primary_key=True)
        schema_name = sa.Column(sa.Text)
        table_name = sa.Column(sa.Text)
        relid = sa.Column(sa.Integer)
        issued_at = sa.Column(sa.DateTime)
        native_transaction_id = sa.Column(sa.BigInteger)
        verb = sa.Column(sa.Text)
        old_data = sa.Column(JSONB, default={}, server_default='{}')
        changed_data = sa.Column(JSONB, default={}, server_default='{}')

        @declared_attr
        def transaction_id(cls):
            return sa.Column(
                sa.BigInteger,
                sa.ForeignKey(transaction_cls.id)
            )

        @declared_attr
        def transaction(cls):
            return sa.orm.relationship(transaction_cls, backref='activities')

        @hybrid_property
        def data(self):
            data = self.old_data.copy() if self.old_data else {}
            if self.changed_data:
                data.update(self.changed_data)
            return data

        @data.expression
        def data(cls):
            return cls.old_data + cls.changed_data

        @property
        def object(self):
            table = Base.metadata.tables[self.table_name]
            cls = get_class_by_table(Base, table, self.data)
            return cls(**self.data)

        def __repr__(self):
            return (
                '<{cls} table_name={table_name!r} '
                'id={id!r}>'
            ).format(
                cls=self.__class__.__name__,
                table_name=self.table_name,
                id=self.id
            )
    return ActivityBase


def convert_callables(values):
    return {
        key: value() if callable(value) else value
        for key, value in values.items()
    }


class VersioningManager(object):
    _actor_cls = None

    def __init__(
        self,
        actor_cls=None,
        schema_name=None,
        use_statement_level_triggers=True
    ):
        if actor_cls is not None:
            self._actor_cls = actor_cls
        self.values = {}
        self.listeners = (
            (
                orm.mapper,
                'instrument_class',
                self.instrument_versioned_classes
            ),
            (
                orm.mapper,
                'after_configured',
                self.configure_versioned_classes
            ),
            (
                orm.session.Session,
                'before_flush',
                self.receive_before_flush,
            ),
        )
        self.schema_name = schema_name
        self.table_listeners = self.get_table_listeners()
        self.pending_classes = WeakSet()
        self.cached_ddls = {}
        self.use_statement_level_triggers = use_statement_level_triggers

    def get_transaction_values(self):
        return self.values

    @contextmanager
    def disable(self, session):
        current_setting = session.execute(
            "SELECT current_setting('session_replication_role')"
        ).fetchone().current_setting
        session.execute('SET LOCAL session_replication_role = "local"')
        yield
        session.execute('SET LOCAL session_replication_role = "{}"'.format(
            current_setting,
        ))

    def render_tmpl(self, tmpl_name):
        file_contents = read_file(
            'templates/{}'.format(tmpl_name)
        ).replace('%', '%%').replace('$$', '$$$$')
        tmpl = string.Template(file_contents)
        context = dict(schema_name=self.schema_name)

        if self.schema_name is None:
            context['schema_prefix'] = ''
            context['revoke_cmd'] = ''
        else:
            context['schema_prefix'] = '{}.'.format(self.schema_name)
            context['revoke_cmd'] = (
                'REVOKE ALL ON {schema_prefix}activity FROM public;'
            ).format(**context)

        temp = tmpl.substitute(**context)
        return temp

    def create_operators(self, target, bind, **kwargs):
        if bind.dialect.server_version_info < (9, 5, 0):
            StatementExecutor(self.render_tmpl('operators_pre95.sql'))(
                target, bind, **kwargs
            )
        if bind.dialect.server_version_info < (10, 0):
            operators_template = self.render_tmpl('operators_pre100.sql')
            StatementExecutor(operators_template)(target, bind, **kwargs)
        operators_template = self.render_tmpl('operators.sql')
        StatementExecutor(operators_template)(target, bind, **kwargs)

    def create_audit_table(self, target, bind, **kwargs):
        sql = ''
        if (
            self.use_statement_level_triggers and
            bind.dialect.server_version_info >= (10, 0)
        ):
            sql += self.render_tmpl('create_activity_stmt_level.sql')
            sql += self.render_tmpl('audit_table_stmt_level.sql')
        else:
            sql += self.render_tmpl('create_activity_row_level.sql')
            sql += self.render_tmpl('audit_table_row_level.sql')
        StatementExecutor(sql)(target, bind, **kwargs)

    def get_table_listeners(self):
        listeners = {'transaction': []}

        listeners['activity'] = [
            ('after_create', sa.schema.DDL(
                self.render_tmpl('jsonb_change_key_name.sql')
            )),
            ('after_create', self.create_audit_table),
            ('after_create', self.create_operators)
        ]
        if self.schema_name is not None:
            listeners['transaction'] = [
                ('before_create', sa.schema.DDL(
                    self.render_tmpl('create_schema.sql')
                )),
                ('after_drop', sa.schema.DDL(
                    self.render_tmpl('drop_schema.sql')
                )),
            ]
        return listeners

    def audit_table(self, table, exclude_columns=None):
        args = [table.name]
        if exclude_columns:
            for column in exclude_columns:
                if column not in table.c:
                    raise ImproperlyConfigured(
                        "Could not configure versioning. Table '{}'' does "
                        "not have a column named '{}'.".format(
                            table.name, column
                        )
                    )
            args.append(array(exclude_columns))

        if self.schema_name is None:
            func = sa.func.audit_table
        else:
            func = getattr(getattr(sa.func, self.schema_name), 'audit_table')
        query = sa.select([func(*args)])
        if query not in cached_statements:
            cached_statements[query] = StatementExecutor(query)
        listener = (table, 'after_create', cached_statements[query])
        if not sa.event.contains(*listener):
            sa.event.listen(*listener)

    def set_activity_values(self, session):
        dialect = session.bind.engine.dialect
        table = self.transaction_cls.__table__

        if not isinstance(dialect, PGDialect):
            warnings.warn(
                '"{0}" is not a PostgreSQL dialect. No versioning data will '
                'be saved.'.format(dialect.__class__),
                RuntimeWarning
            )
            return

        values = convert_callables(self.get_transaction_values())
        if values:
            values['native_transaction_id'] = sa.func.txid_current()
            values['issued_at'] = sa.text("now() AT TIME ZONE 'UTC'")
            stmt = (
                table
                .insert()
                .values(**values)
            )
            session.execute(stmt)

    def modified_columns(self, obj):
        columns = set()
        mapper = sa.inspect(obj.__class__)
        for key, attr in sa.inspect(obj).attrs.items():
            if key in mapper.synonyms.keys():
                continue
            prop = getattr(obj.__class__, key).property
            if attr.history.has_changes():
                columns |= set(
                    prop.columns
                    if isinstance(prop, sa.orm.ColumnProperty)
                    else
                    [local for local, remote in prop.local_remote_pairs]
                )
        return columns

    def is_modified(self, obj_or_session):
        if hasattr(obj_or_session, '__mapper__'):
            if not hasattr(obj_or_session, '__versioned__'):
                raise ClassNotVersioned(obj_or_session.__class__.__name__)
            excluded = obj_or_session.__versioned__.get('exclude', [])
            return bool(
                set([
                    column.name
                    for column in self.modified_columns(obj_or_session)
                ]) - set(excluded)
            )
        else:
            return any(
                self.is_modified(entity) or entity in obj_or_session.deleted
                for entity in obj_or_session
                if hasattr(entity, '__versioned__')
            )

    def receive_before_flush(self, session, flush_context, instances):
        if self.is_modified(session):
            self.set_activity_values(session)

    def instrument_versioned_classes(self, mapper, cls):
        """
        Collect versioned class and add it to pending_classes list.

        :mapper mapper: SQLAlchemy mapper object
        :cls cls: SQLAlchemy declarative class
        """
        if hasattr(cls, '__versioned__') and cls not in self.pending_classes:
            self.pending_classes.add(cls)

    def configure_versioned_classes(self):
        """
        Configures all versioned classes that were collected during
        instrumentation process.
        """
        for cls in self.pending_classes:
            self.audit_table(cls.__table__, cls.__versioned__.get('exclude'))
        assign_actor(self.base, self.transaction_cls, self.actor_cls)

    def attach_table_listeners(self):
        for values in self.table_listeners['transaction']:
            sa.event.listen(self.transaction_cls.__table__, *values)
        for values in self.table_listeners['activity']:
            sa.event.listen(self.activity_cls.__table__, *values)

    def remove_table_listeners(self):
        for values in self.table_listeners['transaction']:
            sa.event.remove(self.transaction_cls.__table__, *values)
        for values in self.table_listeners['activity']:
            sa.event.remove(self.activity_cls.__table__, *values)

    @property
    def actor_cls(self):
        if isinstance(self._actor_cls, str):
            if not self.base:
                raise ImproperlyConfigured(
                    'This manager does not have declarative base set up yet. '
                    'Call init method to set up this manager.'
                )
            registry = self.base._decl_class_registry
            try:
                return registry[self._actor_cls]
            except KeyError:
                raise ImproperlyConfigured(
                    'Could not build relationship between Activity'
                    ' and %s. %s was not found in declarative class '
                    'registry. Either configure VersioningManager to '
                    'use different actor class or disable this '
                    'relationship by setting it to None.' % (
                        self._actor_cls,
                        self._actor_cls
                    )
                )
        return self._actor_cls

    def attach_listeners(self):
        self.attach_table_listeners()
        for listener in self.listeners:
            sa.event.listen(*listener)

    def remove_listeners(self):
        self.remove_table_listeners()
        for listener in self.listeners:
            sa.event.remove(*listener)

    def activity_model_factory(self, base, transaction_cls):
        class Activity(activity_base(base, self.schema_name, transaction_cls)):
            __tablename__ = 'activity'

        return Activity

    def transaction_model_factory(self, base):
        class Transaction(transaction_base(base, self.schema_name)):
            __tablename__ = 'transaction'

        return Transaction

    def init(self, base):
        self.base = base
        self.transaction_cls = self.transaction_model_factory(base)
        self.activity_cls = self.activity_model_factory(
            base,
            self.transaction_cls
        )
        self.attach_listeners()


versioning_manager = VersioningManager()
