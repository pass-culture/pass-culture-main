from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.scripts.add_or_update_bank_account.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_script_links_venue_with_bank_account_to_offerer_bank_account_on_venue_with_siret():
    """
    Test du cas où la venue sans siret, avec CB reçoit le CB de la venue avec siret de l'offerer. L'offerer a plusieurs venues avec CB qui ont toutes le même iban, sauf une
    """
    offerer = offerers_factories.OffererFactory()
    # venue 1 avec siret, avec CB, iban identique à l'iban du CB de la venue d'origine
    venue_with_good_BA = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
    bank_account = finance_factories.BankAccountFactory(
        offerer=offerer,
        status=finance_models.BankAccountApplicationStatus.ACCEPTED,
        isActive=True,
        iban="FR7610010000000000000009999",
    )
    venue_with_good_BA_link = offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_with_good_BA, bankAccount=bank_account
    )

    # venue d'origine sans siret, avec CB (iban identique au précédent)
    origin_venue = offerers_factories.VenueFactory(
        managingOfferer=offerer, siret=None, comment="Venue with bank account"
    )
    origin_bank_account = finance_factories.BankAccountFactory(
        offerer=offerer,
        status=finance_models.BankAccountApplicationStatus.ACCEPTED,
        isActive=True,
        iban="FR7610010000000000000009999",
    )
    origin_venue_bank_account_link = offerers_factories.VenueBankAccountLinkFactory(
        venue=origin_venue, bankAccount=origin_bank_account
    )

    # venue 3 avec siret, avec CB, iban différent
    venue_3 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900002")
    bank_account_3 = finance_factories.BankAccountFactory(
        offerer=offerer,
        status=finance_models.BankAccountApplicationStatus.ACCEPTED,
        isActive=True,
        iban="FR7610010000000000000000000",
    )
    offerers_factories.VenueBankAccountLinkFactory(venue=venue_3, bankAccount=bank_account_3)

    mock_csv_row = {"origin_venue_id": str(origin_venue.id)}

    with patch("pcapi.scripts.add_or_update_bank_account.main._read_csv_file", return_value=iter([mock_csv_row])):
        main(not_dry=True)

    db.session.refresh(venue_with_good_BA_link)
    assert venue_with_good_BA_link is not None
    assert venue_with_good_BA_link.venueId == venue_with_good_BA.id
    assert venue_with_good_BA_link.bankAccountId == bank_account.id

    # On vérifie que la venue sans SIRET est liée au bank account de la venue 1 avec siret
    db.session.refresh(origin_venue_bank_account_link)
    new_origin_venue_link = (
        db.session.query(offerers_models.VenueBankAccountLink)
        .filter(
            offerers_models.VenueBankAccountLink.venueId == origin_venue.id,
            offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
        )
        .one()
    )
    assert new_origin_venue_link != origin_venue_bank_account_link

    # On vérifie que la nouvelle liaison a un historique associé
    action_history_for_new_link = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            history_models.ActionHistory.venueId == origin_venue.id,
        )
        .one()
    )

    assert action_history_for_new_link.venueId == origin_venue.id
    assert action_history_for_new_link.bankAccountId == bank_account.id
    assert action_history_for_new_link.comment == "Compte bancaire du partenaire culturel mis à jour (PC-37159)"


def test_script_links_venue_without_bank_account_to_offerer_bank_account_on_venue_with_siret():
    """
    Test du cas où la venue sans siret, sans CB reçoit le CB de la venue avec siret de l'offerer. L'offerer a plusieurs venues avec CB, des PP différents. La venue d'origine doit recevoir le CB de la seule venue avec siret et le même PP.
    """
    offerer = offerers_factories.OffererFactory()
    # venue 1 avec siret, avec CB, PP identique à celui de la venue d'origine
    venue_with_good_BA = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
    bank_account = finance_factories.BankAccountFactory(
        offerer=offerer,
        status=finance_models.BankAccountApplicationStatus.ACCEPTED,
        isActive=True,
        iban="FR7610010000000000000009999",
    )
    venue_with_good_BA_link = offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_with_good_BA, bankAccount=bank_account
    )
    offerers_factories.VenuePricingPointLinkFactory(
        venue=venue_with_good_BA,
        pricingPoint=venue_with_good_BA,
        timespan=[datetime.utcnow() - timedelta(days=1), None],
    )

    # venue d'origine sans siret, sans CB, même PP que venue 1
    origin_venue = offerers_factories.VenueFactory(
        managingOfferer=offerer, siret=None, comment="Venue with bank account"
    )
    offerers_factories.VenuePricingPointLinkFactory(
        venue=origin_venue,
        pricingPoint=venue_with_good_BA,
        timespan=[datetime.utcnow() - timedelta(days=1), None],
    )

    # venue 3 avec siret, avec CB, PP différent
    venue_3 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900002")
    bank_account_3 = finance_factories.BankAccountFactory(
        offerer=offerer,
        status=finance_models.BankAccountApplicationStatus.ACCEPTED,
        isActive=True,
        iban="FR7610010000000000000000000",
    )
    offerers_factories.VenueBankAccountLinkFactory(venue=venue_3, bankAccount=bank_account_3)
    offerers_factories.VenuePricingPointLinkFactory(
        venue=venue_3,
        pricingPoint=venue_3,
        timespan=[datetime.utcnow() - timedelta(days=1), None],
    )

    mock_csv_row = {"origin_venue_id": str(origin_venue.id)}

    with patch("pcapi.scripts.add_or_update_bank_account.main._read_csv_file", return_value=iter([mock_csv_row])):
        main(not_dry=True)

    db.session.refresh(venue_with_good_BA_link)
    assert venue_with_good_BA_link is not None
    assert venue_with_good_BA_link.venueId == venue_with_good_BA.id
    assert venue_with_good_BA_link.bankAccountId == bank_account.id

    # On vérifie que la venue d'origine sans SIRET est liée au bank account de la venue 1 avec siret
    new_origin_venue_link = (
        db.session.query(offerers_models.VenueBankAccountLink).filter_by(venueId=origin_venue.id).one_or_none()
    )
    assert new_origin_venue_link.bankAccountId == bank_account.id

    # On vérifie que la nouvelle liaison a un historique associé
    action_history_for_new_link = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            history_models.ActionHistory.venueId == origin_venue.id,
        )
        .one_or_none()
    )

    assert action_history_for_new_link is not None
    assert action_history_for_new_link.venueId == origin_venue.id
    assert action_history_for_new_link.bankAccountId == bank_account.id
    assert action_history_for_new_link.comment == "Compte bancaire du partenaire culturel mis à jour (PC-37159)"
