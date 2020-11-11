from unittest.mock import Mock

import pytest

from pcapi.model_creators.generic_creators import create_venue_type
from pcapi.use_cases.get_types_of_venues import get_types_of_venues


class UseCaseTest:
    class GetTypesOfVenuesTest:
        @pytest.mark.usefixtures("db_session")
        def test_return_the_list(self, app):
            # Given
            list_of_types = [create_venue_type("Theatre")]
            get_all_venue_types = Mock(return_value=list_of_types)

            # When
            result = get_types_of_venues(get_all_venue_types)

            # Then
            get_all_venue_types.assert_called_once()
            assert result == list_of_types
