import json
import logging
import sys
from io import StringIO

from utils import logger


class LoggerTest:
    def test_jsonlogger_should_log_with_log_level(self):
        # Given
        capturedOutput = StringIO()
        sys.stderr = capturedOutput
        logger.configure_json_logger()
        json_logger = logging.getLogger('json')

        # When
        json_logger.error("Request succeeded", extra={"response": "some response"})

        # Then
        captured_logs_dict = json.loads(capturedOutput.getvalue())
        assert captured_logs_dict["level"] == logging.getLevelName(logging.ERROR)

    def test_jsonlogger_should_log_with_iso_timestamp(self):
        # Given
        capturedOutput = StringIO()
        sys.stderr = capturedOutput
        logger.configure_json_logger()
        json_logger = logging.getLogger('json')

        # When
        json_logger.error("Request succeeded", extra={"response": "some response"})

        # Then
        captured_logs_dict = json.loads(capturedOutput.getvalue())
        assert captured_logs_dict["timestamp"] is not None

    def test_jsonlogger_should_log_keys_and_values_added_on_logging(self):
        # Given
        capturedOutput = StringIO()
        sys.stderr = capturedOutput
        logger.configure_json_logger()
        json_logger = logging.getLogger('json')

        # When
        json_logger.error("Request succeeded", extra={"response": "some response"})

        # Then
        captured_logs_dict = json.loads(capturedOutput.getvalue())
        assert captured_logs_dict["response"] == "some response"

    def test_jsonlogger_should_log_logged_message_in_message_key(self):
        # Given
        capturedOutput = StringIO()
        sys.stderr = capturedOutput
        logger.configure_json_logger()
        json_logger = logging.getLogger('json')

        # When
        json_logger.error("Request succeeded", extra={"response": "some response"})

        # Then
        captured_logs_dict = json.loads(capturedOutput.getvalue())
        assert captured_logs_dict["message"] == "Request succeeded"
