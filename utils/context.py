def with_app_context(app):
    with app.app_context():
        import models
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
        for model in models.__dict__.values():
            model_with_app_context(model)
