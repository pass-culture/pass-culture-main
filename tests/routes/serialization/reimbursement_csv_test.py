from freezegun import freeze_time

from models.feature import FeatureToggle
from models.payment_status import TransactionStatus
from repository import repository
from repository.reimbursement_queries import find_all_offerer_payments
from routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv, \
    ReimbursementDetails, \
    find_all_offerer_reimbursement_details
from scripts.payment.batch_steps import generate_new_payments
import pytest
from model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_deposit, \
    create_user_offerer, create_bank_information, create_payment
from model_creators.specific_creators import create_stock_with_thing_offer, create_offer_with_thing_product
from tests.test_utils import deactivate_feature


class FindReimbursementDetailsTest:
    @pytest.mark.usefixtures("db_session")
    def test_find_all_offerer_reimbursement_details(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        deposit = create_deposit(user, amount=500, source='public')
        offerer1 = create_offerer(siren='123456789')
        user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
        venue1 = create_venue(offerer1)
        venue2 = create_venue(offerer1, siret='12345678912346')
        bank_information1 = create_bank_information(application_id=1, venue=venue1)
        bank_information2 = create_bank_information(application_id=2, venue=venue2)
        create_offer_with_thing_product(venue1, url='https://host/path/{token}?offerId={offerId}&email={email}')
        create_offer_with_thing_product(venue2)
        stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, price=10)
        stock2 = create_stock_with_thing_offer(offerer=offerer1, venue=venue2, price=11)
        booking1 = create_booking(user=user, stock=stock1, is_used=True, token='ABCDEF', venue=venue1)
        booking2 = create_booking(user=user, stock=stock1, token='ABCDEG', venue=venue1)
        booking3 = create_booking(user=user, stock=stock2, is_used=True, token='ABCDEH', venue=venue2)
        repository.save(deposit, booking1, booking2, booking3,
                        user_offerer1, bank_information1, bank_information2)
        generate_new_payments()

        # When
        reimbursement_details = find_all_offerer_reimbursement_details(offerer1.id)

        # Then
        assert len(reimbursement_details) == 2


@freeze_time('2019-07-10')
class ReimbursementDetailsCSVTest:
    @pytest.mark.usefixtures("db_session")
    def test_generate_payment_details_csv_with_human_readable_header(self, app):
        # given
        reimbursement_details = []

        # when
        csv = generate_reimbursement_details_csv(reimbursement_details)

        # then
        assert _get_header(csv,
                           0) == "Année;Virement;Créditeur;SIRET créditeur;Adresse créditeur;IBAN;Raison sociale du lieu;Nom de l'offre;Nom utilisateur;Prénom utilisateur;Contremarque;Date de validation de la réservation;Montant remboursé;Statut du remboursement"

    @freeze_time('2019-07-05 12:00:00')
    @pytest.mark.usefixtures("db_session")
    def test_generate_payment_details_csv_with_right_values(self, app):
        # given
        deactivate_feature(FeatureToggle.DEGRESSIVE_REIMBURSEMENT_RATE)
        user = create_user(first_name='John', last_name='Doe')
        deposit = create_deposit(user, amount=500, source='public')
        offerer1 = create_offerer(siren='123456789', address='123 rue de Paris')
        user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
        venue1 = create_venue(offerer1)
        bank_information1 = create_bank_information(venue=venue1)
        stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, price=10)
        booking1 = create_booking(user=user, stock=stock1, is_used=True, token='ABCDEF', venue=venue1)
        booking2 = create_booking(user=user, stock=stock1, token='ABCDEG', venue=venue1)

        repository.save(deposit, booking1, booking2, user_offerer1, bank_information1)

        generate_new_payments()

        reimbursement_details = find_all_offerer_reimbursement_details(offerer1.id)

        # when
        csv = generate_reimbursement_details_csv(reimbursement_details)

        # then
        assert _count_non_empty_lines(csv) == 2
        assert _get_header(csv,
                           1) == "2019;Juillet : remboursement 1ère quinzaine;La petite librairie;12345678912345;123 rue de Paris;FR7630006000011234567890189;La petite librairie;Test Book;Doe;John;ABCDEF;;10.00;Remboursement initié"


class AsCsvRowTest:
    @pytest.mark.usefixtures("db_session")
    def test_generate_payment_csv_raw_contains_human_readable_status_with_details_when_error(self, app):
        # given
        user = create_user(email='user+plus@example.com')
        deposit = create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=10)
        booking = create_booking(user=user, stock=stock, is_used=True, token='ABCDEF', venue=venue)
        payment = create_payment(booking, offerer,
                                 transaction_label='pass Culture Pro - remboursement 1ère quinzaine 07-2019',
                                 status=TransactionStatus.ERROR,
                                 amount=50,
                                 detail='Iban non fourni')
        repository.save(deposit, payment)

        payments_info = find_all_offerer_payments(offerer.id)

        # when
        raw_csv = ReimbursementDetails(payments_info[0]).as_csv_row()

        # then
        assert raw_csv[13] == 'Erreur d\'envoi du remboursement : Iban non fourni'


def _get_header(csv, line):
    return csv.split('\r\n')[line]


def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != '', csv.split('\r\n'))))
