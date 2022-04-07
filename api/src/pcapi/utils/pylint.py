import astroid.nodes
import pylint.checkers
import pylint.interfaces


MSG_USE_OF_UNCONTROLLED_STRING = "markupsafe-uncontrolled-string"

MARKUP_SAFE_HELP = """\
`markupsafe.Markup()` should not directly accept an uncontrolled string.
You should rather use `Markup("{variable}").format(variable=variable)`
to properly escape `variable`.
"""


class MarkupSafeChecker(pylint.checkers.BaseChecker):
    __implements__ = pylint.interfaces.IAstroidChecker

    name = "markupsafe"
    priority = -1
    msgs = {
        "W4001": (
            "Possible XSS caused by using a non-constant string as an argument of `markupsafe.Markup()`.",
            MSG_USE_OF_UNCONTROLLED_STRING,
            MARKUP_SAFE_HELP,
        ),
    }
    options = ()

    def visit_call(self, node: astroid.nodes.Call) -> None:
        children = node.get_children()
        first_child = next(children)
        # Access through `Markup` (name) or `markupsafe.Markup` (attrname)
        name = getattr(first_child, "name", None) or getattr(first_child, "attrname", None)
        if name != "Markup":
            return

        # If we're here, it's because we are calling `Markup()`. So
        # check the type of its argument, if any.
        try:
            second_child = next(children)
        except StopIteration:
            # No argument was passed. Odd, but fine.
            return

        if not isinstance(second_child, astroid.nodes.Const):
            self.add_message(MSG_USE_OF_UNCONTROLLED_STRING, node=node, line=node.lineno)
            return


WRONG_PYDANTIC_BASE_MODEL_IMPORT = "wrong-pydantic-base-model-import"

BASE_MODEL_IMPORT_HELP = """\
`You should not import BaseModel directly from pydantic.
You should rather do `import BaseModel from pcapi.routes.serialization`.
"""


class BaseModelImportChecker(pylint.checkers.BaseChecker):
    __implements__ = pylint.interfaces.IAstroidChecker

    name = "pydantic-import"
    priority = -1
    msgs = {
        "W4002": (
            "This BaseModel does accept NaN and infinite values which can lead to inconsistent behavior.",
            WRONG_PYDANTIC_BASE_MODEL_IMPORT,
            BASE_MODEL_IMPORT_HELP,
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


def register(linter):  # type: ignore [no-untyped-def]
    linter.register_checker(MarkupSafeChecker(linter))
    linter.register_checker(BaseModelImportChecker(linter))
