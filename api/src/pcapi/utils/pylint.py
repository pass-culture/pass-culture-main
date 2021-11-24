import astroid.nodes
import pylint.checkers
import pylint.interfaces


MSG_USE_OF_UNCONTROLLED_STRING = "markupsafe-uncontrolled-string"

HELP = """\
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
            HELP,
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


def register(linter):
    linter.register_checker(MarkupSafeChecker(linter))
