from itertools import chain
from datetime import datetime

from tests.conftest import clean_database

from models import Offerer, Payment, PcObject
from scripts.payment.batch_steps import generate_new_payments
from tests.test_utils import create_bank_information, create_stock_with_thing_offer, \
    create_deposit, create_venue, create_offerer, \
    create_user, create_booking, create_user_offerer
from repository.reimbursement_queries import find_all_offerer_reimbursement_details
from domain.reimbursement import generate_reimbursement_details_csv

class ReimbursmentDetailsCSVTest:
    @clean_database
    def test_generate_payment_details_csv_with_human_readable_header_and_reimbursements_lines(self, app):
        # given
        user = create_user(email='user+plus@email.fr')
        deposit = create_deposit(user, datetime.utcnow(), amount=500, source='public')
        offerer1 = create_offerer()
        offerer2 = create_offerer(siren='123456788')
        user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
        user_offerer2 = create_user_offerer(user, offerer2, validation_token=None)
        venue1 = create_venue(offerer1)
        venue2 = create_venue(offerer1, siret='12345678912346')
        venue3 = create_venue(offerer2, siret='12345678912347')
        bank_information1 = create_bank_information(id_at_providers='79387501900056', venue=venue1)
        bank_information2 = create_bank_information(id_at_providers='79387501900057', venue=venue2)
        stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, price=10)
        stock2 = create_stock_with_thing_offer(offerer=offerer1, venue=venue2, price=11)
        stock3 = create_stock_with_thing_offer(offerer=offerer2, venue=venue3, price=12)
        stock4 = create_stock_with_thing_offer(offerer=offerer2, venue=venue3, price=13)
        booking1 = create_booking(user, stock1, venue=venue1, token='ABCDEF', is_used=True)
        booking2 = create_booking(user, stock1, venue=venue1, token='ABCDEG')
        booking3 = create_booking(user, stock2, venue=venue2, token='ABCDEH', is_used=True)
        booking4 = create_booking(user, stock3, venue=venue3, token='ABCDEI', is_used=True)
        booking5 = create_booking(user, stock4, venue=venue3, token='ABCDEJ', is_used=True)
        booking6 = create_booking(user, stock4, venue=venue3, token='ABCDEK', is_used=True)
        PcObject.save(deposit, booking1, booking2, booking3,
                      booking4, booking5, booking6, user_offerer1,
                      user_offerer2, bank_information1, bank_information2)

        generate_new_payments()

        offerers = Offerer.query.all()

        reimbursement_details = chain(*[
            find_all_offerer_reimbursement_details(offerer.id)
            for offerer in offerers
        ])

        # when
        csv = generate_reimbursement_details_csv(reimbursement_details)

        # then
        assert _count_non_empty_lines(csv) == 6
        assert _get_header(csv) == "Année;Virement;Créditeur;SIRET créditeur;Adresse créditeur;IBAN;Raison sociale du lieu;Nom de l'offre;Nom utilisateur;Prénom utilisateur;Contremarque;Date de validation de la réservation;Montant remboursé;Statut du remboursement"


def _get_header(csv):
    return csv.split('\r\n')[0]

def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != '', csv.split('\r\n'))))