"""This is a test file for our checker in `pcapi.utils.pylint`.

This file is NOT run by pytest, which is why it does not contain any
assertion.
"""

# ruff: noqa

import markupsafe
from markupsafe import Markup


def cases_ok(self):
    markupsafe.Markup("constant string")
    Markup("constant string")
    # proper use of `Markup.format()`
    markupsafe.Markup("{foo}").format(foo="uncontrolled string")
    Markup("{foo}").format(foo="uncontrolled string")
    # no argument, our checker should not crash
    markupsafe.Markup()
    Markup()


def cases_warning(self):
    variable = "uncontrolled string"
    # direct use of a variable
    markupsafe.Markup(variable)
    Markup(variable)
    # f-string
    markupsafe.Markup(f"{variable}")
    Markup(f"{variable}")
    # string.format()
    markupsafe.Markup("variable".format())
    Markup("variable".format())
    # percent formatting
    markupsafe.Markup("%s" % variable)
    Markup("%s" % variable)
    # function call
    markupsafe.Markup(get_variable())
    Markup(get_variable())
    # attribute access
    c = C()
    markupsafe.Markup(c.variable)
    Markup(c.variable)


def get_variable():
    return "uncontrolled string"


class C:
    variable = "uncontrolled string"
