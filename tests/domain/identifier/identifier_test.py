import pytest

from domain.identifier.identifier import Identifier


class IdentifierTest:
    def should_be_a_positive_number(self):
        # When
        with pytest.raises(Exception) as exception:
            Identifier(0)

        # Then
        assert str(exception.value) == 'Identifier should be a strictly positive number'

    def should_be_a_strictly_positive_number(self):
        # When
        with pytest.raises(Exception) as exception:
            Identifier(-1)

        # Then
        assert str(exception.value) == 'Identifier should be a strictly positive number'

    def should_not_be_equal_with_another_object(self):
        # When
        identifier = Identifier(42)

        # Then
        assert identifier != 42
        assert identifier != "42"
        assert identifier != {"identifier": 42}

    def should_not_be_equals_if_identifiers_are_differents(self):
        # When
        identifier = Identifier(42)

        # Then
        assert identifier != Identifier(84)

    def should_be_equals_if_identifier_is_equal(self):
        # Given
        identifier_value = 84

        # When
        equality = Identifier(identifier_value) == Identifier(identifier_value)

        # Then
        assert equality is True


class HumanizeTest:
    def should_return_identifier_as_string(self):
        # Given
        identifier = Identifier(42)

        # When
        humanized_identifier = identifier.humanize()

        # Then
        assert humanized_identifier == 'F9'
