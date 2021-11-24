import pathlib

import astroid
import pylint.testutils

from pcapi.utils.pylint import MarkupSafeChecker

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
