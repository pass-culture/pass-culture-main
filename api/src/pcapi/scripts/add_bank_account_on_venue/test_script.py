from unittest.mock import patch

import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.scripts.add_bank_account_on_venue.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_script_links_venue_with_siret_to_offerer_bank_account():
    """
    Test du cas où la venue sans siret reçoit le CB de l'offerer.
    """
    offerer = offerers_factories.OffererFactory()
    venue_with_siret = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
    bank_account = finance_factories.BankAccountFactory(
        offerer=offerer, status=finance_models.BankAccountApplicationStatus.ACCEPTED, isActive=True
    )
    venue_without_siret = offerers_factories.VenueFactory(
        managingOfferer=offerer, siret=None, comment="Venue with bank account"
    )
    existing_venue_bank_account_link = offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_without_siret, bankAccount=bank_account
    )

    mock_csv_row = {"initial_venue_id": str(venue_without_siret.id)}

    with patch("pcapi.scripts.add_bank_account_on_venue.main._read_csv_file", return_value=iter([mock_csv_row])):
        main(not_dry=True, filename="test_file")

    venue_link = (
        db.session.query(offerers_models.VenueBankAccountLink).filter_by(venueId=venue_with_siret.id).one_or_none()
    )
    assert venue_link is not None
    assert venue_link.venueId == venue_with_siret.id
    assert venue_link.bankAccountId == bank_account.id

    # On vérifie que la venue sans SIRET est toujours liée au même bank account
    db.session.refresh(existing_venue_bank_account_link)
    venue_link = (
        db.session.query(offerers_models.VenueBankAccountLink).filter_by(venueId=venue_without_siret.id).one_or_none()
    )
    assert venue_link == existing_venue_bank_account_link

    # Vérifie que la nouvelle liaison a un historique associé
    action_history_for_new_link = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
            history_models.ActionHistory.venueId == venue_with_siret.id,
        )
        .one_or_none()
    )

    assert action_history_for_new_link is not None
    assert action_history_for_new_link.venueId == venue_with_siret.id
    assert action_history_for_new_link.bankAccountId == bank_account.id
    assert action_history_for_new_link.comment == "Compte bancaire du partenaire culturel mis à jour (PC-37091)"

    # Vérifie qu'on n'a pas créé d'historique pour la venue sans SIRET
    action_history_for_venue_without_siret = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
            history_models.ActionHistory.venueId == venue_without_siret.id,
        )
        .one_or_none()
    )

    assert action_history_for_venue_without_siret is None


def test_script_updates_existing_link_for_different_account():
    """
    Le script doit fermer l'ancienne liaison et en créer une nouvelle.
    """
    offerer = offerers_factories.OffererFactory()
    active_bank_account = finance_factories.BankAccountFactory(
        offerer=offerer, status=finance_models.BankAccountApplicationStatus.ACCEPTED, isActive=True
    )
    inactive_bank_account = finance_factories.BankAccountFactory(
        offerer=offerer, status=finance_models.BankAccountApplicationStatus.ACCEPTED, isActive=False
    )

    venue_without_siret = offerers_factories.VenueFactory(
        managingOfferer=offerer, siret=None, comment="Venue with bank account"
    )
    offerers_factories.VenueBankAccountLinkFactory(venue=venue_without_siret, bankAccount=active_bank_account)

    venue_with_siret = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
    # On lie ce venue à un autre compte bancaire initialement
    initial_link = offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_with_siret, bankAccount=inactive_bank_account
    )

    mock_csv_row = {"initial_venue_id": str(venue_without_siret.id)}

    with patch("pcapi.scripts.add_bank_account_on_venue.main._read_csv_file", return_value=iter([mock_csv_row])):
        main(not_dry=True, filename="test_file")

    # L'ancienne liaison devrait être fermée
    db.session.refresh(initial_link)
    assert initial_link.timespan.upper != None

    # Une nouvelle liaison devrait avoir été créée
    new_link = (
        db.session.query(offerers_models.VenueBankAccountLink)
        .filter(
            offerers_models.VenueBankAccountLink.venueId == venue_with_siret.id,
            offerers_models.VenueBankAccountLink.bankAccountId == active_bank_account.id,
        )
        .one_or_none()
    )
    assert new_link is not None

    # Vérifie l'historique pour le venue mis à jour
    action_history_for_updated_venue = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
            history_models.ActionHistory.venueId == venue_with_siret.id,
        )
        .all()
    )

    assert len(action_history_for_updated_venue) == 1
    assert action_history_for_updated_venue[0].bankAccountId == active_bank_account.id

    # Vérifie l'historique pour le venue sans SIRET
    action_history_for_siret_venue = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
            history_models.ActionHistory.venueId == venue_without_siret.id,
        )
        .one_or_none()
    )

    assert action_history_for_siret_venue is None


def test_script_does_nothing_if_link_is_already_correct():
    """
    Teste le cas où le venue est déjà lié au bon compte bancaire.
    Le script ne devrait rien modifier.
    """
    offerer = offerers_factories.OffererFactory()
    venue_with_siret = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
    bank_account = finance_factories.BankAccountFactory(
        offerer=offerer, status=finance_models.BankAccountApplicationStatus.ACCEPTED, isActive=True
    )

    venue_without_siret = offerers_factories.VenueFactory(
        managingOfferer=offerer, siret=None, comment="Venue with bank account"
    )
    offerers_factories.VenueBankAccountLinkFactory(venue=venue_without_siret, bankAccount=bank_account)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue_with_siret, bankAccount=bank_account)

    mock_csv_row = {"initial_venue_id": str(venue_without_siret.id)}

    with patch("pcapi.scripts.add_bank_account_on_venue.main._read_csv_file", return_value=iter([mock_csv_row])):
        main(not_dry=True, filename="test_file")

    # On s'assure qu'il n'y a toujours qu'une seule liaison pour ce venue
    links_count = (
        db.session.query(offerers_models.VenueBankAccountLink).filter_by(venueId=venue_without_siret.id).count()
    )
    assert links_count == 1

    # Aucun historique ne devrait avoir été ajouté pour le venue sans SIRET
    action_history_for_linked_venue = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
            history_models.ActionHistory.venueId == venue_without_siret.id,
        )
        .count()
    )

    assert action_history_for_linked_venue == 0

    # Aucun historique ne devrait avoir été ajouté pour le venue avec SIRET
    action_history_for_siret_venue = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
            history_models.ActionHistory.venueId == venue_with_siret.id,
        )
        .count()
    )

    assert action_history_for_siret_venue == 0
