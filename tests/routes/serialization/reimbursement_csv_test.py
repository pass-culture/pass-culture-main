from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.repository.reimbursement_queries import find_all_offerer_payments
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerer_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv
from pcapi.scripts.payment.batch_steps import generate_new_payments


class FindReimbursementDetailsTest:
    @pytest.mark.usefixtures("db_session")
    def test_find_all_offerer_reimbursement_details(self, app):
        # Given
        user = users_factories.UserFactory(email="user+plus@email.fr")
        offerer1 = create_offerer(siren="123456789")
        user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
        venue1 = create_venue(offerer1)
        venue2 = create_venue(offerer1, siret="12345678912346")
        bank_information1 = create_bank_information(application_id=1, venue=venue1)
        bank_information2 = create_bank_information(application_id=2, venue=venue2)
        create_offer_with_thing_product(venue1, url="https://host/path/{token}?offerId={offerId}&email={email}")
        create_offer_with_thing_product(venue2)
        stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, price=10)
        stock2 = create_stock_with_thing_offer(offerer=offerer1, venue=venue2, price=11)
        booking1 = create_booking(user=user, stock=stock1, is_used=True, token="ABCDEF", venue=venue1)
        booking2 = create_booking(user=user, stock=stock1, token="ABCDEG", venue=venue1)
        booking3 = create_booking(user=user, stock=stock2, is_used=True, token="ABCDEH", venue=venue2)
        repository.save(booking1, booking2, booking3, user_offerer1, bank_information1, bank_information2)
        generate_new_payments()

        # When
        reimbursement_details = find_all_offerer_reimbursement_details(offerer1.id)

        # Then
        assert len(reimbursement_details) == 2


@freeze_time("2019-07-10")
class ReimbursementDetailsCSVTest:
    @pytest.mark.usefixtures("db_session")
    def test_generate_payment_details_csv_with_human_readable_header(self, app):
        # given
        reimbursement_details = []

        # when
        csv = generate_reimbursement_details_csv(reimbursement_details)

        # then
        assert (
            _get_header(csv, 0)
            == '"Année";"Virement";"Créditeur";"SIRET créditeur";"Adresse créditeur";"IBAN";"Raison sociale du lieu";"Nom de l\'offre";"Nom utilisateur";"Prénom utilisateur";"Contremarque";"Date de validation de la réservation";"Montant remboursé";"Statut du remboursement"'
        )

    @freeze_time("2019-07-05 12:00:00")
    @pytest.mark.usefixtures("db_session")
    def test_generate_payment_details_csv_with_right_values(self, app):
        # given
        stock = offers_factories.StockFactory(price=10, offer__name='Mon titre ; un peu "spécial"')
        venue = stock.offer.venue
        user_offerer = offers_factories.UserOffererFactory(offerer=venue.managingOfferer)
        bank_informations = offers_factories.BankInformationFactory(venue=venue)
        bookings_factories.BookingFactory(stock=stock, isUsed=True, token="0E2722")
        bookings_factories.BookingFactory(stock=stock, token="LDVNNW")

        generate_new_payments()

        reimbursement_details = find_all_offerer_reimbursement_details(user_offerer.offererId)

        # when
        csv = generate_reimbursement_details_csv(reimbursement_details)

        # then
        assert _count_non_empty_lines(csv) == 2
        assert (
            _get_header(csv, 1)
            == f'"2019";"Juillet : remboursement 1ère quinzaine";"{venue.name}";"{venue.siret}";"1 boulevard Poissonnière";"{bank_informations.iban}";"{venue.name}";"Mon titre ; un peu ""spécial""";"Doux";"Jeanne";"0E2722";"";10.00;"Remboursement en cours"'
        )


class AsCsvRowTest:
    @pytest.mark.usefixtures("db_session")
    def test_generate_payment_csv_raw_contains_human_readable_status_with_details_when_error(self, app):
        # given
        user = users_factories.UserFactory(email="user+plus@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=10)
        booking = create_booking(user=user, stock=stock, is_used=True, token="ABCDEF", venue=venue)
        payment = create_payment(
            booking,
            offerer,
            transaction_label="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            status=TransactionStatus.ERROR,
            amount=50,
            detail="Iban non fourni",
        )
        repository.save(payment)

        payments_info = find_all_offerer_payments(offerer.id)

        # when
        raw_csv = ReimbursementDetails(payments_info[0]).as_csv_row()

        # then
        assert raw_csv[13] == "Remboursement en cours : Iban non fourni"


def _get_header(csv, line):
    return csv.split("\r\n")[line]


def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != "", csv.split("\r\n"))))
