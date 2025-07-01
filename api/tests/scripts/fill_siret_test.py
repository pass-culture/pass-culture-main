import copy

import pytest
import requests_mock

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.scripts.fill_siret_if_possible.main import main

from tests.connectors import api_entreprise_test_data


@pytest.mark.usefixtures("db_session")
def test_fill_siret_if_possible():
    SIRENS = (
        ("123456789", "12345678901257"),
        ("987654321", "98765432101569"),
        ("111111111", "11111111101569"),
    )
    # Offerer with 1 venue with SIRET and 1 without SIRET
    offerer_with_venues_with_and_without_siret = offerers_factories.OffererFactory(siren=SIRENS[0][0])
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer_with_venues_with_and_without_siret)
    offerers_factories.VenueFactory(siret=SIRENS[0][1], managingOfferer=offerer_with_venues_with_and_without_siret)
    offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer_with_venues_with_and_without_siret)

    # Offerer with 1 venue without SIRET
    offerer_with_1_venue_without_siret = offerers_factories.OffererFactory(siren=SIRENS[1][0])
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer_with_1_venue_without_siret)
    offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer_with_1_venue_without_siret)

    # Offerer with 3 venues without SIRET
    offerer_with_3_venues_without_siret = offerers_factories.OffererFactory(siren=SIRENS[2][0])
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer_with_3_venues_without_siret)
    offerers_factories.VenueWithoutSiretFactory.create_batch(3, managingOfferer=offerer_with_3_venues_without_siret)

    # Ensure the data are correct
    assert len(set(offerers_models.Offerer.query.with_entities(offerers_models.Offerer.siren))) == 3
    assert offerers_models.Venue.query.filter(offerers_models.Venue.siret.is_(None)).count() == 8
    assert offerers_models.Venue.query.filter(offerers_models.Venue.siret.is_not(None)).count() == 1

    # Mock the API and run the script
    with requests_mock.Mocker() as mock:
        for siren, siret in SIRENS:
            siret_data = copy.deepcopy(api_entreprise_test_data.RESPONSE_SIRET_COMPANY)
            siret_data["data"]["unite_legale"]["siret_siege_social"] = siret
            mock.get(
                f"https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/{siren}/siege_social",
                json=siret_data,
            )
            mock.get(
                f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/{siret}",
                json=api_entreprise_test_data.RESPONSE_SIRET_COMPANY,
            )
            mock.get(
                "https://api-adresse.data.gouv.fr/search",
                json={
                    "features": [
                        {
                            "properties": {
                                "id": "123456789",
                                "label": "12 BIS AVENUE DU LIVRE 58400 LA CHARITE-SUR-LOIRE",
                                "score": 1.0,
                                "postcode": "58400",
                                "citycode": "58059",
                                "city": "LA CHARITE-SUR-LOIRE",
                                "name": "12 BIS AVENUE DU LIVRE",
                            },
                            "geometry": {"type": "Point", "coordinates": [2.3522219, 48.856614]},
                        }
                    ]
                },
            )

        main(not_dry=True)

    # Each offerer should have its venues updated with SIRET
    assert offerers_models.Venue.query.filter(offerers_models.Venue.siret.is_not(None)).count() == 3
    # Ensure that the offerer with 1 venue has 1 venue with SIRET on the regular venue
    assert (
        offerers_models.Venue.query.filter(
            offerers_models.Venue.isVirtual == False,
            offerers_models.Venue.managingOfferer == offerer_with_1_venue_without_siret,
        ).count()
        == 1
    )
    # Ensure that the offerer with 3 venues has 1 venue with SIRET on the regular venue
    assert offerers_models.Venue.query.filter(
        offerers_models.Venue.isVirtual == False,
        offerers_models.Venue.managingOfferer == offerer_with_3_venues_without_siret,
    ).order_by(offerers_models.Venue.id).with_entities(offerers_models.Venue.siret).all() == [
        ("11111111101569",),
        (None,),
        (None,),
    ]
