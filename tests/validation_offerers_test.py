import pytest

from models import Offerer
from models.api_errors import ConflictError
from validation.offerers import check_offerer_is_validated


def test_check_offerer_is_validated_should_raise_conflict_error_when_offerer_not_validated():
    # Given
    offerer = Offerer()
    offerer.generate_validation_token()

    # When
    with pytest.raises(ConflictError):
        check_offerer_is_validated(offerer)


def test_check_offerer_is_validated_should_not_raise_conflict_error_when_offerer_validated():
    # Given
    offerer = Offerer()
    offerer.validationToken = None

    # When
    check_offerer_is_validated(offerer)
