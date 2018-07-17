from models.pc_object import PcObject


def with_app_context(app):
    with app.app_context():
        # IMPORT
        from utils.printer import get

        # ADAPT SQL ALCHEMY TO INSERT APP CONTEXT INSIDE QUERY
        def call_with_app_context(func):
            def func_with_app_context(*args, **kwargs):
                with app.app_context():
                    return func(*args, **kwargs)
            return func_with_app_context
        PcObject.check_and_save = call_with_app_context(PcObject.check_and_save)
        app.db.session.execute = call_with_app_context(app.db.session.execute)
        app.db.session.merge = call_with_app_context(app.db.session.merge)
        app.db.session.query = call_with_app_context(app.db.session.query)
        app.get = call_with_app_context(get)
        app.datascience.get_occasions = call_with_app_context(app.datascience.get_occasions)
        app.datascience.get_occasions_by_type = call_with_app_context(app.datascience.get_occasions_by_type)
        app.get_contact = call_with_app_context(app.get_contact)
        app.subscribe_newsletter = call_with_app_context(app.subscribe_newsletter)
        def model_with_app_context(model):
            if not hasattr(model, 'query'):
                return
            getter = model.__class__.__getattribute__
            if not type(getter).__name__ == 'wrapper_descriptor':
                return
            def getattribute_with_app_context(self, key):
                if key == 'query':
                    with app.app_context():
                        return getter(self, key)
                return getter(self, key)
            model.__class__.__getattribute__ = getattribute_with_app_context
        for model in values():
            model_with_app_context(model)
