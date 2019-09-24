from pandas import Index

from models import PcObject
from repository.okr_queries import get_all_experimentation_users_details
from tests.conftest import clean_database
from tests.test_utils import create_user


class GetAllExperimentationUsersDetailsTest:
    @clean_database
    def test_should_not_return_details_for_users_who_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)

        # When
        experimentation_users = get_all_experimentation_users_details()
        # Then
        assert experimentation_users.empty

    @clean_database
    def test_should_return_columns_in_given_order(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)

        # When
        experimentation_users = get_all_experimentation_users_details()
        # Then
        assert experimentation_users.columns.equals(Index(['Vague d\'expérimentation', 'Date d\'activation',
                                                           'Date de remplissage du typeform',
                                                           'Date de première connection',
                                                           'Date de première réservation',
                                                           'Date de deuxième réservation',
                                                           'Date de première réservation dans 3 catégories différentes',
                                                           'Date de dernière recommandation',
                                                           'Nombre de réservations totales',
                                                           'Nombre de réservations non annulées'],
                                                          dtype='object'))
