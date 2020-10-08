import re

import pytest

from pcapi.domain.identifier.identifier import Identifier, NonProperlyFormattedScrambledId, NonStricltyPositiveIdentifierException


class IdentifierTest:
    def should_be_a_positive_number(self):
        # When
        with pytest.raises(NonStricltyPositiveIdentifierException) as exception:
            Identifier(0)

        # Then
        assert str(exception.value) == 'Identifier should be a strictly positive number'

    def should_be_a_strictly_positive_number(self):
        # When
        with pytest.raises(NonStricltyPositiveIdentifierException) as exception:
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


class PersistedTest:
    def should_be_given_identifier(self):
        # Given
        expected_identifier = 42

        # When
        persisted_identifier = Identifier(expected_identifier).persisted

        # Then
        assert persisted_identifier == expected_identifier


class ScrambledTest:
    def should_scramble_identifier(self):
        # Given
        persisted_identifier = 42
        identifier = Identifier(persisted_identifier)

        # When
        scrambled_identifier = identifier.scrambled

        # Then
        assert scrambled_identifier != persisted_identifier

    def should_be_a_mix_of_uppercase_letters_and_digits(self):
        # When
        scrambled_identifier = Identifier(12452).scrambled

        # Then
        assert re.match('[A-Z0-9]*', scrambled_identifier)

    def should_be_unique_for_a_given_persisted_identifier(self):
        # When
        scrambled_identifier = Identifier(42).scrambled

        # Then
        assert scrambled_identifier != Identifier(43).scrambled

    def should_be_equal_to_original_identifier_when_initialized_from_scrambled_identifier(self):
        # Given
        identifier = Identifier(42)

        # When
        scrambled_identifier = identifier.scrambled

        # Then
        identifier_from_scrambled = Identifier.from_scrambled_id(scrambled_identifier)
        assert identifier == identifier_from_scrambled


class FromScrambledIdTest:
    def should_not_initialize_id_when_given_scrambled_id_is_none(self):
        # When
        identifier = Identifier.from_scrambled_id(None)

        # Then
        assert identifier is None

    def should_not_unscramble_unproperly_formatted_ids(self):
        # When
        with pytest.raises(NonProperlyFormattedScrambledId) as exception:
            Identifier.from_scrambled_id("#4%^&")

        # Then
        assert str(exception.value) == 'Scrambled identifier "#4%^&===" is not properly formatted'
