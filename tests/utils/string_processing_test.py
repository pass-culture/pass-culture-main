from models import Deposit, MediationSQLEntity
from utils.string_processing import remove_single_letters_for_search, tokenize_for_search, get_model_plural_name


def test_remove_special_character():
    assert tokenize_for_search("Læetitia a mangé's'") == ['læetitia', 'a', 'mangé', 's', '']


def test_remove_special_character():
    assert tokenize_for_search("L'histoire sans fin") == ['l', 'histoire', 'sans', 'fin']


def test_tokenize_url():
    assert tokenize_for_search('http://www.t_est-toto.fr') == ['http', 'www', 't', 'est', 'toto', 'fr']


def test_tokenize_url():
    assert remove_single_letters_for_search(['http', 'www', 't', 'est', 'toto', 'fr']) == ['http', 'www', 'est', 'toto',
                                                                                           'fr']


class GetModelPluralNameTest:
    def test_should_return_model_plural(self):
        # Given
        model = Deposit()

        # When
        model_plural_name = get_model_plural_name(model)

        # Then
        assert model_plural_name == 'deposits'

    def test_should_return_model_plural_when_suffixed_by_sql_entity(self):
        # Given
        model = MediationSQLEntity()

        # When
        model_plural_name = get_model_plural_name(model)

        # Then
        assert model_plural_name == 'mediations'
