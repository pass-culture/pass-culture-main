import pathlib

import astroid

from pcapi.utils.pylint import MarkupSafeChecker


try:
    import pylint.testutils
except ImportError as exc:
    import os
    import sys

    # FIXME: DEBUG ONLY : Est-ce qu'on ne lance pas les tests d'un
    # répertoire où "pylint" n'est pas le package tiers (par exemple
    # depuis `src/pcapi/utils` qui contient un fichier "pylint.py"
    debug = []
    debug.append(f"cwd = {os.getcwd()}")
    debug.append(f"sys.path = {sys.path}")
    try:
        import pylint

        debug.append(f"pylint.__path__: {pylint.__path__}")  # nous donnera un peu d'infos sur le package pylint
    except ImportError as inner_exc:
        debug.append(f"impossible de 'import pylint' seulement: {inner_exc}")
    raise ValueError("\n".join(debug)) from exc

import tests


TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"


class MarkupSafeCheckerTest(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = MarkupSafeChecker

    def test_checker(self):
        code = (TEST_FILES_PATH / "pylint.py").read_text()
        node = astroid.parse(code)
        self.walk(node)
        messages = self.linter.release_messages()
        msg_ids = {m.msg_id for m in messages}
        assert msg_ids == {"markupsafe-uncontrolled-string"}
        lines = {m.line for m in messages}
        assert lines == {25, 26, 28, 29, 31, 32, 34, 35, 37, 38, 41, 42}
