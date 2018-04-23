def with_app_context(app):
    with app.app_context():
        # IMPORT
        import models
        import datascience
        import routes
        from utils.printer import get

        # ADAPT SQL ALCHEMY TO INSERT APP CONTEXT INSIDE QUERY
        def call_with_app_context(func):
            def func_with_app_context(*args, **kwargs):
                with app.app_context():
                    return func(*args, **kwargs)
            return func_with_app_context
        app.model.PcObject.check_and_save = call_with_app_context(app.model.PcObject.check_and_save)
        app.db.session.execute = call_with_app_context(app.db.session.execute)
        app.db.session.query = call_with_app_context(app.db.session.query)
        app.get = call_with_app_context(get)
        app.datascience.get_offers = call_with_app_context(app.datascience.get_offers)
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
        for model in app.model.values():
            model_with_app_context(model)
