import re

import pytest

from pcapi.domain.titelive import get_date_from_filename


class GetDateFromFilenameTest:
    def should_return_matching_pattern_in_filename(self):
        # Given
        filename = 'Resume191012.zip'
        date_regexp = re.compile('Resume(\d{6}).zip')

        # When
        extracted_date = get_date_from_filename(filename, date_regexp)

        # Then
        assert extracted_date == 191012

    def should_raises_error_if_no_match_in_filename(self):
        # Given
        filename = None
        date_regexp = re.compile('Resume(\d{6}).zip')

        # When / Then
        with pytest.raises(ValueError):
            get_date_from_filename(filename, date_regexp)
