from flask import Blueprint as BaseBlueprint


# This class is used as a wrapper around original Flask Blueprint class.
# We use it to remove the dot "." character because Blueprint's "name" property
# containing a dot is no longer supported  since version 2 of flask.
# (https://github.com/pallets/flask/blob/3897a518014931a82c77a353e1e9c2248529b856/src/flask/blueprints.py#L196)
class Blueprint(BaseBlueprint):
    def __init__(self, name: str, import_name: str, **kw):  # type: ignore [no-untyped-def]
        cleaned_name = name.replace(".", "_")
        super().__init__(name=cleaned_name, import_name=import_name, **kw)
