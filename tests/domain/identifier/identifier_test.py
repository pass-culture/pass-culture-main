from domain.identifier.identifier import Identifier


class IdentifierTest:
    def test_identifier_should_not_be_equal_with_another_object(self):
        # Given
        identifier = Identifier(42)
        other_object = 42

        # When
        equality = identifier == other_object

        # Then
        assert equality is False

    def test_identifiers_should_not_be_equals_if_identifiers_are_differents(self):
        # Given
        identifier_a = Identifier(42)
        identifier_b = Identifier(84)

        # When
        equality = identifier_a == identifier_b

        # Then
        assert equality is False

    def test_identifiers_should_be_equals_if_identifier_is_equal(self):
        # Given
        identifier_value = 84
        identifier_a = Identifier(identifier_value)
        identifier_b = Identifier(identifier_value)

        # When
        equality = identifier_a == identifier_b

        # Then
        assert equality is True

    def test_humanize_should_return_identifier_as_string(self):
        # Given
        identifier = Identifier(42)

        # When
        humanized_identifier = identifier.humanize()

        # Then
        assert humanized_identifier == 'F9'
