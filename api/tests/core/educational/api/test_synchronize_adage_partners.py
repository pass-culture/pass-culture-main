from unittest.mock import patch

import pytest

from pcapi.core.educational.api import adage
from pcapi.core.educational.schemas import AdageCulturalPartner
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.repository import get_emails_by_venue
from pcapi.models import db


BASE_DATA = {
    "regionId": None,
    "academieId": None,
    "statutId": None,
    "labelId": None,
    "typeId": 8,
    "communeId": "26324",
    "libelle": "Fête du livre jeunesse de St Paul les trois Châteaux",
    "adresse": "Place Charles Chausy",
    "siteWeb": "http://www.fetedulivrejeunesse.fr/",
    "latitude": 44.350457,
    "longitude": 4.765918,
    "dateModification": "2021-09-01T00:00:00",
    "statutLibelle": None,
    "labelLibelle": None,
    "typeIcone": "town",
    "typeLibelle": "Association ou fondation pour la promotion, le développement et la diffusion d\u0027oeuvres",
    "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
    "communeDepartement": "026",
    "academieLibelle": "GRENOBLE",
    "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
    "domaines": "Univers du livre, de la lecture et des écritures",
    "domaineIds": "11",
}


@pytest.mark.usefixtures("db_session")
class SynchronizeAdagePartnersTest:
    def test_synchronize_partners(self):
        # venue has no adageId, obtains one after synchronization
        adage_id_1 = 1
        venue_1 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
        partner_1 = AdageCulturalPartner(
            **BASE_DATA, id=adage_id_1, actif=1, synchroPass=1, venueId=venue_1.id, siret=venue_1.siret
        )

        # venue has no adageId, synchronization can add one but synchroPass is false
        adage_id_2 = 2
        venue_2 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
        partner_2 = AdageCulturalPartner(
            **BASE_DATA, id=adage_id_2, actif=1, synchroPass=0, venueId=venue_2.id, siret=venue_2.siret
        )

        # venue has no adageId, no corresponding adage partner
        venue_3 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)

        # venue has an adageId and is marked as inactive by the synchronization
        adage_id_4 = 4
        venue_4 = offerers_factories.VenueFactory(adageId=adage_id_4, managingOfferer__allowedOnAdage=True)
        partner_4 = AdageCulturalPartner(
            **BASE_DATA, id=adage_id_4, actif=0, synchroPass=1, venueId=venue_4.id, siret=venue_4.siret
        )

        # venue has an adageId and synchroPass is false
        adage_id_5 = 5
        venue_5 = offerers_factories.VenueFactory(adageId=adage_id_5, managingOfferer__allowedOnAdage=True)
        partner_5 = AdageCulturalPartner(
            **BASE_DATA, id=adage_id_5, actif=1, synchroPass=0, venueId=venue_5.id, siret=venue_5.siret
        )

        # venue has an adageId and is unchanged
        adage_id_6 = 6
        venue_6 = offerers_factories.VenueFactory(adageId=adage_id_6, managingOfferer__allowedOnAdage=True)
        partner_6 = AdageCulturalPartner(
            **BASE_DATA, id=adage_id_6, actif=1, synchroPass=1, venueId=venue_6.id, siret=venue_6.siret
        )

        # unknown venue id
        adage_id_7 = 7
        partner_7 = AdageCulturalPartner(
            **BASE_DATA, id=adage_id_7, actif=1, synchroPass=1, venueId=-1, siret="12345678901234"
        )

        # venue has an adageId, we receive a partner with same adageId but different venueId
        adage_id_8 = 8
        venue_8 = offerers_factories.VenueFactory(adageId=adage_id_8, managingOfferer__allowedOnAdage=True)
        partner_8 = AdageCulturalPartner(
            **BASE_DATA, id=adage_id_8, actif=1, synchroPass=1, venueId=-2, siret="12345678901235"
        )

        partners = [partner_1, partner_2, partner_4, partner_5, partner_6, partner_7, partner_8]
        with (
            patch("pcapi.core.educational.api.adage.send_eac_offerer_activation_email") as mock_activation_mail,
            patch("pcapi.core.educational.adage_backends.get_adage_offerer") as mock_get_adage_offerer,
        ):
            mock_get_adage_offerer.return_value = []
            adage.synchronize_adage_partners(partners, apply=True)
            db.session.commit()

        # venue has no adageId, obtains one after synchronization
        assert venue_1.adageId == str(adage_id_1)
        assert venue_1.adageInscriptionDate is not None
        [history] = venue_1.action_history
        assert history.extraData["modified_info"]["adageId"] == {"new_info": str(adage_id_1), "old_info": None}
        assert venue_1.managingOfferer.allowedOnAdage is True

        # venue has no adageId, synchronization can add one but synchroPass is false
        assert venue_2.adageId is None
        assert venue_2.adageInscriptionDate is None
        assert len(venue_2.action_history) == 0
        assert venue_2.managingOfferer.allowedOnAdage is False

        # venue has no adageId, no corresponding adage partner
        assert venue_3.adageId is None
        assert venue_3.adageInscriptionDate is None
        assert len(venue_3.action_history) == 0
        assert venue_3.managingOfferer.allowedOnAdage is False

        # venue has an adageId and is marked as inactive by the synchronization
        assert venue_4.adageId is None
        assert venue_4.adageInscriptionDate is None
        [history] = venue_4.action_history
        assert history.extraData["modified_info"]["adageId"] == {"new_info": None, "old_info": str(adage_id_4)}
        assert venue_4.managingOfferer.allowedOnAdage is False

        # venue has an adageId and synchroPass is false
        assert venue_5.adageId is None
        assert venue_5.adageInscriptionDate is None
        [history] = venue_5.action_history
        assert history.extraData["modified_info"]["adageId"] == {"new_info": None, "old_info": str(adage_id_5)}
        assert venue_5.managingOfferer.allowedOnAdage is False

        # venue has an adageId and is unchanged
        assert venue_6.adageId == str(adage_id_6)
        assert len(venue_6.action_history) == 0
        assert venue_6.managingOfferer.allowedOnAdage is True

        # check that the unknown adageId was not set in DB
        assert (
            db.session.query(offerers_models.Venue).filter(offerers_models.Venue.adageId == str(adage_id_7)).count()
            == 0
        )

        # venue has an adageId, we receive a partner with same adageId but different venueId
        assert venue_8.adageId == str(adage_id_8)
        assert len(venue_8.action_history) == 0
        assert venue_8.managingOfferer.allowedOnAdage is True

        # get_adage_offerer -> one call per inactive partner
        assert mock_get_adage_offerer.call_count == 3
        assert {call.kwargs["siren"] for call in mock_get_adage_offerer.call_args_list} == {
            venue_2.managingOfferer.siren,
            venue_4.managingOfferer.siren,
            venue_5.managingOfferer.siren,
        }

        # send_eac_offerer_activation_email -> one call for the activated venue
        [call] = mock_activation_mail.call_args_list
        called_venue = call.args[0].id
        called_emails = call.args[1]

        assert called_emails == list(get_emails_by_venue(venue_1))
        assert called_venue == venue_1.id

    def test_synchronize_partners_no_apply(self):
        # venue has no adageId, obtains one after synchronization
        adage_id_1 = 1
        venue_1 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
        partner_1 = AdageCulturalPartner(
            **BASE_DATA, id=adage_id_1, actif=1, synchroPass=1, venueId=venue_1.id, siret=venue_1.siret
        )

        partners = [partner_1]
        with (
            patch("pcapi.core.educational.api.adage.send_eac_offerer_activation_email") as mock_activation_mail,
            patch("pcapi.core.educational.adage_backends.get_adage_offerer") as mock_get_adage_offerer,
        ):
            mock_get_adage_offerer.return_value = []
            adage.synchronize_adage_partners(partners, apply=False)
            db.session.commit()

        mock_get_adage_offerer.assert_not_called()
        mock_activation_mail.assert_not_called()

    def test_synchronize_partners_offerers(self):
        # the partner has a siret that we do not know, but matches the offerer siren
        # -> the venue does not get an adageId but the offerer will be allowedOnAdage
        venue_1 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
        siret = f"{venue_1.managingOfferer.siren}99999"
        partner_1 = AdageCulturalPartner(**BASE_DATA, id=1, actif=1, synchroPass=0, venueId=None, siret=siret)

        # the offerer is allowedOnAdage, we receive an inactive partner that matches the siren
        # there is another active partner for this siren on adage side
        # -> the offerer remains allowedOnAdage
        venue_2 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=True)
        siret = f"{venue_2.managingOfferer.siren}99999"
        partner_2 = AdageCulturalPartner(**BASE_DATA, id=2, actif=0, synchroPass=0, venueId=None, siret=siret)

        # the offerer is allowedOnAdage, we receive an inactive partner that matches the siren
        # there is another venue with adageId related to the offerer
        # -> the offerer remains allowedOnAdage
        venue_3 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=True)
        other_venue_3 = offerers_factories.VenueFactory(managingOfferer=venue_3.managingOfferer, adageId="300")
        siret = f"{venue_3.managingOfferer.siren}99999"
        partner_3 = AdageCulturalPartner(**BASE_DATA, id=3, actif=0, synchroPass=0, venueId=None, siret=siret)

        # the offerer is allowedOnAdage, we receive an inactive partner that matches the siren
        # there is another soft-deleted venue with adageId related to the offerer
        # -> the offerer remains allowedOnAdage
        venue_4 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=True)
        other_venue_4 = offerers_factories.VenueFactory(managingOfferer=venue_4.managingOfferer, adageId="400")
        other_venue_4.isSoftDeleted = True
        deleted_venue_id = other_venue_4.id
        siret = f"{venue_4.managingOfferer.siren}99999"
        partner_4 = AdageCulturalPartner(**BASE_DATA, id=4, actif=0, synchroPass=0, venueId=None, siret=siret)

        # the offerer is allowedOnAdage, we receive an inactive partner that matches the siren
        # there is no venue with adageId, no other active partner on adage side
        # -> the offerer will be allowedOnAdage=False
        venue_5 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=True)
        siret = f"{venue_5.managingOfferer.siren}99999"
        partner_5 = AdageCulturalPartner(**BASE_DATA, id=5, actif=0, synchroPass=0, venueId=None, siret=siret)

        partners = [partner_1, partner_2, partner_3, partner_4, partner_5]

        def get_adage_offerer(siren: str) -> list[AdageCulturalPartner]:
            if siren == venue_2.managingOfferer.siren:
                siret = f"{siren}99998"
                return [AdageCulturalPartner(**BASE_DATA, id=100, actif=1, synchroPass=0, venueId=None, siret=siret)]

            return []

        with (
            patch("pcapi.core.educational.api.adage.send_eac_offerer_activation_email") as mock_activation_mail,
            patch("pcapi.core.educational.adage_backends.get_adage_offerer") as mock_get_adage_offerer,
        ):
            mock_get_adage_offerer.side_effect = get_adage_offerer
            adage.synchronize_adage_partners(partners, apply=True)
            db.session.commit()

        mock_activation_mail.assert_not_called()

        # get_adage_offerer is called when we receive an inactive partner that matches the siren
        # and there is no other venue with adageId
        assert mock_get_adage_offerer.call_count == 2
        assert {call.kwargs["siren"] for call in mock_get_adage_offerer.call_args_list} == {
            venue_2.managingOfferer.siren,
            venue_5.managingOfferer.siren,
        }

        # the partner has a siret that we do not know, but matches the offerer siren
        # -> the venue does not get an adageId but the offerer will be allowedOnAdage
        assert venue_1.adageId is None
        assert venue_1.adageInscriptionDate is None
        assert len(venue_1.action_history) == 0
        assert venue_1.managingOfferer.allowedOnAdage is True

        # the offerer is allowedOnAdage, we receive an inactive partner that matches the siren
        # there is another active partner for this siren on adage side
        # -> the offerer remains allowedOnAdage
        assert venue_2.adageId is None
        assert venue_2.adageInscriptionDate is None
        assert len(venue_2.action_history) == 0
        assert venue_2.managingOfferer.allowedOnAdage is True

        # the offerer is allowedOnAdage, we receive an inactive partner that matches the siren
        # there is another venue with adageId related to the offerer
        # -> the offerer remains allowedOnAdage
        assert venue_3.adageId is None
        assert venue_3.adageInscriptionDate is None
        assert len(venue_3.action_history) == 0
        assert other_venue_3.adageId == "300"
        assert venue_3.managingOfferer.allowedOnAdage is True

        # the offerer is allowedOnAdage, we receive an inactive partner that matches the siren
        # there is another soft-deleted venue with adageId related to the offerer
        # -> the offerer remains allowedOnAdage
        assert venue_4.adageId is None
        assert venue_4.adageInscriptionDate is None
        assert len(venue_4.action_history) == 0
        other_venue_4 = (
            db.session.query(offerers_models.Venue)
            .filter(offerers_models.Venue.id == deleted_venue_id)
            .execution_options(include_deleted=True)
            .one()
        )
        assert other_venue_4.adageId == "400"
        assert venue_4.managingOfferer.allowedOnAdage is True

        # the offerer is allowedOnAdage, we receive an inactive partner that matches the siren
        # there is no venue with adageId, no other active partner on adage side
        # -> the offerer will be allowedOnAdage=False
        assert venue_5.adageId is None
        assert venue_5.adageInscriptionDate is None
        assert len(venue_5.action_history) == 0
        assert venue_5.managingOfferer.allowedOnAdage is False
