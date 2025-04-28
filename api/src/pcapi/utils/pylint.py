import astroid.nodes
import pylint.checkers
import pylint.interfaces
import pylint.lint


WRONG_PYDANTIC_BASE_MODEL_IMPORT = "wrong-pydantic-base-model-import"


class BaseModelImportChecker(pylint.checkers.BaseChecker):
    name = "pydantic-import"
    priority = -1
    msgs = {
        "W4002": (
            "This BaseModel does accept NaN and infinite values which can lead to inconsistent behavior.\nYou should rather do `import BaseModel from pcapi.routes.serialization`.",
            WRONG_PYDANTIC_BASE_MODEL_IMPORT,
            "Accepting NaN and infinite values can lead to inconsistent behavior or security breaches.",
        ),
    }
    options = ()

    def visit_importfrom(self, node: astroid.nodes.ImportFrom) -> None:
        names = [name for name, _ in node.names]
        modname = node.modname
        if modname == "pydantic":
            for name in names:
                if name == "BaseModel":
                    self.add_message(WRONG_PYDANTIC_BASE_MODEL_IMPORT, node=node, line=node.lineno)
                    return


MSG_USE_OF_DATETIME_NOW = "datetime-now"
DATETIME_NOW_HELP = """\
Datetimes are stored in UTC. As such, `datetime.utcnow()` should be used
instead of `now()`, unless you are really sure that you want a local,
non-UTC datetime.
"""


class DatetimeNowChecker(pylint.checkers.BaseChecker):
    name = "datetime-now"
    priority = -1
    msgs = {
        "W4003": (
            "Likely wrong use of `datetime.now()` instead of `utcnow()`.",
            MSG_USE_OF_DATETIME_NOW,
            DATETIME_NOW_HELP,
        ),
    }
    options = ()

    def visit_attribute(self, node: astroid.nodes.Attribute) -> None:
        expr = node.expr
        expr_name = getattr(expr, "attrname", None) or getattr(expr, "name", None)
        if node.attrname == "now" and expr_name == "datetime":
            self.add_message(MSG_USE_OF_DATETIME_NOW, node=node, line=node.lineno)


MSG_REQUESTS_IMPORT = "wrong-requests-import"


class RequestsImportChecker(pylint.checkers.BaseChecker):
    name = "requests-import"
    priority = -1
    msgs = {
        "W4004": (
            "Likely wrong import of the original `requests` third-party package",
            MSG_REQUESTS_IMPORT,
            "There is a `pcapi.utils.requests` wrapper that should be used instead.",
        ),
    }
    options = ()

    def visit_import(self, node: astroid.nodes.Import) -> None:
        names = [name.split(".")[0] for name, _alias in node.names]
        if "requests" in names:
            self.add_message(MSG_REQUESTS_IMPORT, node=node, line=node.lineno)

    def visit_importfrom(self, node: astroid.nodes.ImportFrom) -> None:
        if node.modname.split(".")[0] == "requests":
            self.add_message(MSG_REQUESTS_IMPORT, node=node, line=node.lineno)


def register(linter: pylint.lint.PyLinter) -> None:
    linter.register_checker(BaseModelImportChecker(linter))
    linter.register_checker(DatetimeNowChecker(linter))
    linter.register_checker(RequestsImportChecker(linter))
