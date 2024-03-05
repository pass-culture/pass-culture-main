import pathlib

import astroid
import pylint.testutils

import pcapi.utils.pylint as pcapi_pylint

import tests


TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"


class CheckerTestCaseBase(pylint.testutils.CheckerTestCase):
    def test_checker(self):
        code = (TEST_FILES_PATH / self.test_filename).read_text()
        node = astroid.parse(code)
        self.walk(node)
        messages = self.linter.release_messages()
        lines = {m.line for m in messages if m.msg_id == self.message_id}
        assert lines == self.expected_error_lines


class MarkupSafeCheckerTest(CheckerTestCaseBase):
    CHECKER_CLASS = pcapi_pylint.MarkupSafeChecker
    message_id = pcapi_pylint.MSG_USE_OF_UNCONTROLLED_STRING
    test_filename = "pylint_markupsafe.py"
    expected_error_lines = {25, 26, 28, 29, 31, 32, 34, 35, 37, 38, 41, 42}


class DatetimeNowCheckerTest(CheckerTestCaseBase):
    CHECKER_CLASS = pcapi_pylint.DatetimeNowChecker
    message_id = pcapi_pylint.MSG_USE_OF_DATETIME_NOW
    test_filename = "pylint_datetime.py"
    expected_error_lines = {11, 14, 15, 16, 17, 23, 26, 27, 28, 29}


class RequestsImportCheckerTest(CheckerTestCaseBase):
    CHECKER_CLASS = pcapi_pylint.RequestsImportChecker
    message_id = pcapi_pylint.MSG_REQUESTS_IMPORT
    test_filename = "pylint_requests.py"
    expected_error_lines = {7, 8, 9, 10}
