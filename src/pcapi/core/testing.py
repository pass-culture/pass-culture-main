import factory.alchemy


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        # sqlalchemy_session = pcapi.models.db.session
        sqlalchemy_session = 'ignored'  # see hack in `_save()`
        sqlalchemy_session_persistence = 'commit'

    @classmethod
    def _save(cls, model_class, session, *args, **kwargs):
        # FIXME (dbaty, 2020-10-20): pytest-flask-sqlalchemy mocks
        # (replaces) `db.session` to remove the session and rollback
        # changes at the end of each test function (see `_session()`
        # fixture in pytest-flask-sqlalchemy). As such, the session
        # that is used in tests is not the session we defined in
        # `Meta.sqlalchemy_session` above. Because of this, data added
        # through a factory is not rollback'ed. To work around this,
        # here is a hack.
        # This issue is discussed here: https://github.com/jeancochrane/pytest-flask-sqlalchemy/issues/12
        from pcapi.models import db
        session = db.session
        # Factory Boy expects that a model instance can be built with this:
        #
        #    instance = Model(attr1='value1', attr2='value2')
        #
        # But PcObject's constructor does not do that, so we have to
        # call `setattr` manually here.
        #
        # FIXME: PcObject.__init__ should be changed. In fact, we
        # should not use PcObject.populate_from_dict to build model
        # instances from JSON input. Hopefully, this will be handled
        # by the future pydantic-based data validation system.
        obj = model_class()
        for attr, value in kwargs.items():
            setattr(obj, attr, value)
        # The rest of the method if the same as the original.
        session.add(obj)
        session_persistence = cls._meta.sqlalchemy_session_persistence
        if session_persistence == factory.alchemy.SESSION_PERSISTENCE_FLUSH:
            session.flush()
        elif session_persistence == factory.alchemy.SESSION_PERSISTENCE_COMMIT:
            session.commit()
        return obj
