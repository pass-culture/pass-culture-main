import pytest
from sqlalchemy import func

from models import OfferSQLEntity, VenueSQLEntity, ApiErrors
from repository import repository
import pytest
from tests.model_creators.generic_creators import create_offerer, create_venue
from utils.human_ids import humanize
from utils.rest import check_order_by, load_or_raise_error


class TestLoadOrRaiseErrorTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_object_if_found(self, app):
        # Given
        id = humanize(1)

        # When
        with pytest.raises(ApiErrors) as error:
            load_or_raise_error(VenueSQLEntity, id)

        assert error.value.errors['global'] == [
            'Aucun objet ne correspond à cet identifiant dans notre base de données']

    @pytest.mark.usefixtures("db_session")
    def test_raises_api_error_if_no_object(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        repository.save(venue)

        # When
        try:
            load_or_raise_error(VenueSQLEntity, humanize(venue.id))

        except:
            assert False


class TestCheckOrderByTest:
    def test_check_order_by_raises_no_exception_when_given_sqlalchemy_column(self, app):
        # When
        try:
            check_order_by(OfferSQLEntity.id)
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_sqlalchemy_column_list(self, app):
        # When
        try:
            check_order_by([OfferSQLEntity.id, OfferSQLEntity.venueId])
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_sqlalchemy_desc_expression(self, app):
        # When
        try:
            check_order_by(OfferSQLEntity.id.desc())
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_sqlalchemy_func_random_expression(self, app):
        # When
        try:
            check_order_by(func.random())
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_mixed_list(self, app):
        # When
        try:
            check_order_by([OfferSQLEntity.id, OfferSQLEntity.venueId.desc(), func.random(), 'id'])
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_colum_name_as_string(self, app):
        # When
        try:
            check_order_by('venueId')
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_colum_name_as_string_with_quotes(self, app):
        # When
        try:
            check_order_by('"venueId"')
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_colum_name_as_string_with_quotes_and_desc(self, app):
        # When
        try:
            check_order_by('"venueId" DESC')
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_colum_name_as_string_with_quotes_and_table_name(self, app):
        # When
        try:
            check_order_by('Offer."venueId" DESC')
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_colum_name_as_string_with_quotes_and_table_name_with_quotes(
            self, app):
        # When
        try:
            check_order_by('"Offer"."venueId" DESC')
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_comma_separated_list_in_string(self, app):
        # When
        try:
            check_order_by('"Offer"."venueId" DESC, id ASC')
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_no_exception_when_given_coalesce_expression_in_string(self, app):
        # When
        try:
            check_order_by('COALESCE("Offer"."venueId" , id) ASC')
        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_check_order_by_raises_an_exception_when_given_list_containing_invalid_part(self, app):
        # When
        with pytest.raises(ApiErrors) as e:
            check_order_by([OfferSQLEntity.id, func.random(), 'select * from toto'])

        # Then
        assert 'order_by' in e.value.errors

    def test_check_order_by_raises_an_exception_when_given_select_statement(self, app):
        # When
        with pytest.raises(ApiErrors) as e:
            check_order_by('select plop from offer')

        # Then
        assert 'order_by' in e.value.errors
