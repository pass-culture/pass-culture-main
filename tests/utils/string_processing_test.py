from models import Deposit, MediationSQLEntity
from utils.string_processing import get_matched_string_index, \
    format_decimal, \
    get_price_value, \
    remove_single_letters_for_search, \
    tokenize_for_search, pluralize, get_model_plural_name


def test_get_matched_string_index():
    assert get_matched_string_index(
        'karl marx',
        ['henri guillemin', 'groucho marx', 'kroutchev', 'emmanuel macron']
    ) == 1


def test_get_price_value():
    assert type(get_price_value('')) == int


def test_remove_special_character():
    assert tokenize_for_search("Læetitia a mangé's'") == ['læetitia', 'a', 'mangé', 's', '']


def test_remove_special_character():
    assert tokenize_for_search("L'histoire sans fin") == ['l', 'histoire', 'sans', 'fin']


def test_tokenize_url():
    assert tokenize_for_search('http://www.t_est-toto.fr') == ['http', 'www', 't', 'est', 'toto', 'fr']


def test_tokenize_url():
    assert remove_single_letters_for_search(['http', 'www', 't', 'est', 'toto', 'fr']) == ['http', 'www', 'est', 'toto',
                                                                                           'fr']


def test_format_decimal():
    assert format_decimal(1.22) == '1,22'


class PluralizeTest:
    def test_should_return_word_when_only_one_occurence(self):
        # Given
        number_of_occurence = 1
        word = 'stock'

        # When
        message = pluralize(number_of_occurence, word)

        # Then
        assert message == 'stock'

    def test_should_return_words_when_more_than_one_occurence(self):
        # Given
        number_of_occurence = 5
        word = 'stock'

        # When
        message = pluralize(number_of_occurence, word)

        # Then
        assert message == 'stocks'


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
