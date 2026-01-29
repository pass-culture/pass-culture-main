import datetime
import re
from unittest import mock

import pytest
from flask import url_for

from pcapi.connectors import api_adresse
from pcapi.connectors import api_geo
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.highlights import factories as highlights_factories
from pcapi.core.highlights import models as highlights_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.utils import date as date_utils


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class AutocompleteTestBase:
    def _test_autocomplete(
        self,
        authenticated_client,
        search_query: str,
        expected_texts: list[str],
        expected_num_queries: int = 0,
    ):
        # session + data requested
        if not expected_num_queries:
            expected_num_queries = 2 if search_query.isnumeric() or len(search_query) >= 2 else 1

        with assert_num_queries(expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))
            assert response.status_code == 200

        items = response.json["items"]
        for item in items:
            assert isinstance(item["id"], int)
            assert isinstance(item["text"], str)
        assert {re.sub(r"^\d+ - ", "", item["text"]) for item in items} == expected_texts

    def test_autocomplete_as_anonymous(self, client):
        response = client.get(url_for(self.endpoint, q="123"))
        assert response.status_code == 401


class AutocompleteOffererTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_offerers"

    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("1", {"La scène (100200000)"}),
            ("12", {"Le Cinéma (123456789)", "La Librairie (123444556)"}),
            ("1234", {"Le Cinéma (123456789)", "La Librairie (123444556)"}),
            ("12345", {"Le Cinéma (123456789)"}),
            ("123444556", {"La Librairie (123444556)"}),
            ("789", set()),
            ("100200301", set()),
            ("ciné", {"Le Cinéma (123456789)", "Cinéma concurrent (561234789)"}),
            ("cinema", {"Le Cinéma (123456789)", "Cinéma concurrent (561234789)"}),
            ("ciné théâtre", set()),
            ("666666", set()),
            ("666666001", {"Le Théâtre (100200300)"}),
            ("12344", {"Cinéma concurrent (561234789)", "La Librairie (123444556)"}),
        ],
    )
    def test_autocomplete_offerers(self, authenticated_client, search_query, expected_texts):
        offerers_factories.OffererFactory(id=1, siren="100200000", name="La scène")
        offerers_factories.OffererFactory(id=666666001, siren="100200300", name="Le Théâtre")
        offerers_factories.OffererFactory(id=666666002, siren="123456789", name="Le Cinéma")
        offerers_factories.OffererFactory(id=666666003, siren="123444556", name="La Librairie")
        offerers_factories.OffererFactory(id=12344, siren="561234789", name="Cinéma concurrent")

        self._test_autocomplete(authenticated_client, search_query, expected_texts)


class AutocompleteInstitutionTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_institutions"

    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("1", set()),
            ("2", set()),
            ("12", {"Lycée public magique Georges Pompidou - Fougères (1470009E)"}),
            ("789", set()),
            (
                "Georges",
                {
                    "Lycée public magique Georges Pompidou - Fougères (1470009E)",
                    "Collège Georges de la Tour - Metz (1270009E)",
                },
            ),
            ("Pompidou", {"Lycée public magique Georges Pompidou - Fougères (1470009E)"}),
            ("magique Pompidou Fou", {"Lycée public magique Georges Pompidou - Fougères (1470009E)"}),
            ("Georges Clémenceau", set()),
            ("1270009E", {"Collège Georges de la Tour - Metz (1270009E)"}),
        ],
    )
    def test_autocomplete_institutions(self, authenticated_client, search_query, expected_texts):
        educational_factories.EducationalInstitutionFactory(
            id=12,
            name="Georges Pompidou",
            institutionId="1470009E",
            institutionType="Lycée public magique",
            city="Fougères",
        )
        educational_factories.EducationalInstitutionFactory(
            id=2000, name="Georges de la Tour", institutionId="1270009E", institutionType="Collège", city="Metz"
        )

        self._test_autocomplete(authenticated_client, search_query, expected_texts)


class AutocompleteVenueTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_venues"

    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("1", {"La scène (10020030000000)"}),
            ("12", {"Le Cinéma (12345678900018)", "La Librairie (12344455600012)", "La Médiathèque (12345678900011)"}),
            (
                "1234",
                {"Le Cinéma (12345678900018)", "La Librairie (12344455600012)", "La Médiathèque (12345678900011)"},
            ),
            ("12345", {"Le Cinéma (12345678900018)", "La Médiathèque (12345678900011)"}),
            ("123456789", {"Le Cinéma (12345678900018)", "La Médiathèque (12345678900011)"}),
            ("12345678900011", {"La Médiathèque (12345678900011)"}),
            ("789", set()),
            ("100200301", set()),
            ("ciné", {"Le Cinéma (12345678900018)", "Cinéma concurrent (56123478900023)"}),
            ("cinema", {"Le Cinéma (12345678900018)", "Cinéma concurrent (56123478900023)"}),
            ("ciné théâtre", set()),
            ("666666", set()),
            ("666666001", {"Le Théâtre (10020030000021)"}),
            ("12344", {"Cinéma concurrent (56123478900023)", "La Librairie (12344455600012)"}),
        ],
    )
    def test_autocomplete_venues(self, authenticated_client, search_query, expected_texts):
        offerers_factories.VenueFactory(id=1, siret="10020030000000", name="La scène")
        offerers_factories.VenueFactory(id=666666001, siret="10020030000021", name="Le Théâtre")
        offerers_factories.VenueFactory(id=666666002, siret="12345678900018", name="Le Cinéma")
        offerers_factories.VenueFactory(id=666666003, siret="12344455600012", name="La Librairie")
        offerers_factories.VenueFactory(id=666666004, siret="12345678900011", name="La Médiathèque")
        offerers_factories.VenueFactory(id=12344, siret="56123478900023", name="Cinéma concurrent")

        self._test_autocomplete(authenticated_client, search_query, expected_texts)


class AutocompletePricingPointTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_pricing_points"

    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("123", {"Cinéma fabuleux (56123478900023)"}),
            ("Cinéma", {"Cinéma fabuleux (56123478900023)"}),
            ("1234", set()),
            ("magique", set()),
            ("12345", set()),
        ],
    )
    def test_autocomplete_venues(self, authenticated_client, search_query, expected_texts):
        offerers_factories.VenueWithoutSiretFactory(id=12345, name="Cinéma magique")
        offerers_factories.VenueFactory(id=123, siret="56123478900023", name="Cinéma fabuleux")

        self._test_autocomplete(authenticated_client, search_query, expected_texts)


class AutocompleteCriteriaTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_criteria"

    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("o", set()),
            ("offre", {"Bonne offre d'appel", "Offre du moment"}),
            ("va", {"Mauvaise accroche (22/02/2023-…)", "Lecture pour les vacances (01/07/2023-31/08/2023)"}),
            ("Cinema", {"Playlist cinéma (…-28/02/2023)"}),
            ("playlist lecture", set()),
            ("10534", {"Un bon id"}),
        ],
    )
    def test_autocomplete_criteria(self, authenticated_client, search_query, expected_texts):
        criteria_factories.CriterionFactory(name="Bonne offre d'appel")
        criteria_factories.CriterionFactory(name="Mauvaise accroche", startDateTime=datetime.datetime(2023, 2, 22, 12))
        criteria_factories.CriterionFactory(name="Offre du moment")
        criteria_factories.CriterionFactory(
            name="Lecture pour les vacances",
            startDateTime=datetime.datetime(2023, 7, 1, 8),
            endDateTime=datetime.datetime(2023, 8, 31, 21, 59),
        )
        criteria_factories.CriterionFactory(name="Playlist cinéma", endDateTime=datetime.datetime(2023, 2, 28, 22, 59))
        criteria_factories.CriterionFactory(id=10534, name="Un bon id")

        self._test_autocomplete(authenticated_client, search_query, expected_texts)

    def test_autocomplete_with_square_numeric_character(self, authenticated_client):
        criteria_factories.CriterionFactory(name="3²+4²=5²")
        self._test_autocomplete(authenticated_client, "3²", {"3²+4²=5²"})


class AutocompleteBoUserTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_bo_users"

    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("1", set()),
            ("L", set()),
            ("Le", {"Léa Hugo", "Léo Admin", "Hercule Poirot"}),  # Hercule Poirot is the authenticated admin user
            ("Léa", {"Léa Hugo"}),
            ("Hugo", {"Léa Hugo", "Hugo Admin"}),
            ("Hugo A", {"Hugo Admin"}),
            ("Pro", set()),
            ("1234", set()),
            ("12345", {"Louise Admin"}),
        ],
    )
    def test_autocomplete_bo_users(self, authenticated_client, search_query, expected_texts):
        users_factories.AdminFactory(firstName="Léa", lastName="Hugo")
        users_factories.AdminFactory(firstName="Léo", lastName="Admin")
        users_factories.AdminFactory(firstName="Hugo", lastName="Admin")
        users_factories.AdminFactory(id=12345, firstName="Louise", lastName="Admin")
        users_factories.UserFactory(id=1234, firstName="Léo", lastName="Hugo")
        users_factories.ProFactory(firstName="Léa", lastName="Pro")

        self._test_autocomplete(authenticated_client, search_query, expected_texts)


class AutocompleteProvidersTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_providers"

    @pytest.mark.parametrize(
        "search_query, expected_texts, expected_queries",
        [
            ("", set(), 1),
            (
                "a",
                {
                    "A good id",
                },
                2,
            ),
            (
                "bon",
                {
                    "Bon providér",
                },
                2,
            ),
            ("12", {"Bon providér"}, 2),
            ("nothing", set(), 2),
            ("912", {"A good id"}, 2),
        ],
    )
    def test_autocomplete_providers(self, authenticated_client, search_query, expected_texts, expected_queries):
        db.session.query(providers_models.Provider).delete()
        providers_factories.ProviderFactory(id=12, name="Bon providér")
        providers_factories.ProviderFactory(id=5, name="provider with number 12")
        providers_factories.ProviderFactory(id=912, name="A good id")

        self._test_autocomplete(
            authenticated_client, search_query, expected_texts, expected_num_queries=expected_queries
        )


class AutocompleteHighlightsTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_highlights"

    @pytest.mark.parametrize(
        "search_query, expected_texts, expected_queries",
        [
            ("", set(), 1),
            (
                "co",
                {
                    f"Temps costaud - {datetime.datetime.strftime((date_utils.get_naive_utc_now() + datetime.timedelta(days=11)).date(), '%d/%m/%Y')}"
                    f" → {datetime.datetime.strftime((date_utils.get_naive_utc_now() + datetime.timedelta(days=12)).date(), '%d/%m/%Y')}",
                },
                2,
            ),
            (
                "fort",
                {
                    f"Temps Fôrt - {datetime.datetime.strftime((date_utils.get_naive_utc_now() + datetime.timedelta(days=11)).date(), '%d/%m/%Y')}"
                    f" → {datetime.datetime.strftime((date_utils.get_naive_utc_now() + datetime.timedelta(days=12)).date(), '%d/%m/%Y')}",
                },
                2,
            ),
            (
                "1",
                {
                    f"Temps costaud - {datetime.datetime.strftime((date_utils.get_naive_utc_now() + datetime.timedelta(days=11)).date(), '%d/%m/%Y')}"
                    f" → {datetime.datetime.strftime((date_utils.get_naive_utc_now() + datetime.timedelta(days=12)).date(), '%d/%m/%Y')}"
                },
                2,
            ),
            ("nothing", set(), 2),
        ],
    )
    def test_autocomplete_highlights(self, authenticated_client, search_query, expected_texts, expected_queries):
        db.session.query(highlights_models.Highlight).delete()
        highlights_factories.HighlightFactory(id=1, name="Temps costaud")
        highlights_factories.HighlightFactory(id=5, name="Temps Fôrt")

        self._test_autocomplete(
            authenticated_client, search_query, expected_texts, expected_num_queries=expected_queries
        )


class AutocompleteAddressesTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_addresses"

    @pytest.mark.parametrize(
        "search_query, search_address_response, expected_texts",
        [
            ("", [], set()),
            (
                "2 rue de la culture là bas",
                [
                    api_adresse.AddressInfo(
                        id="01234_56789_00002",
                        label="unused",
                        postcode="unused",
                        citycode="unused",
                        latitude=0.0,
                        longitude=0.0,
                        score=0.5,
                        city="unused",
                        street="unused",
                    )
                ],
                {"2 rue de la Culture 01002 Là-Bas"},
            ),
            (
                "2 rue de la culture là",
                [
                    api_adresse.AddressInfo(
                        id="01234_56789_00002",
                        label="unused",
                        postcode="unused",
                        citycode="unused",
                        latitude=0.0,
                        longitude=0.0,
                        score=0.5,
                        city="unused",
                        street="unused",
                    ),
                    api_adresse.AddressInfo(
                        id="01234_56789_00003",
                        label="unused",
                        postcode="unused",
                        citycode="unused",
                        latitude=0.0,
                        longitude=0.0,
                        score=0.5,
                        city="unused",
                        street="unused",
                    ),
                ],
                {"2 rue de la Culture 01002 Là-Bas", "2 rue de la Culture 01003 Là-Haut"},
            ),
            (
                "4 rue de la Culture Ailleurs",
                [
                    api_adresse.AddressInfo(
                        id="01234_56789_00004",
                        label="unused",
                        postcode="unused",
                        citycode="unused",
                        latitude=0.0,
                        longitude=0.0,
                        score=0.5,
                        city="unused",
                        street="unused",
                    )
                ],
                set(),
            ),
        ],
    )
    def test_autocomplete_addresses(self, authenticated_client, search_query, search_address_response, expected_texts):
        geography_factories.AddressFactory(
            banId="01234_56789_00001", street="1 rue de la Culture", postalCode="01001", inseeCode="01201", city="Ici"
        )
        geography_factories.AddressFactory(
            banId="01234_56789_00002",
            street="2 rue de la Culture",
            postalCode="01002",
            inseeCode="01202",
            city="Là-Bas",
        )
        geography_factories.AddressFactory(
            banId="01234_56789_00003",
            street="2 rue de la Culture",
            postalCode="01003",
            inseeCode="01203",
            city="Là-Haut",
        )
        geography_factories.AddressFactory(
            banId=None, street="4 rue de la Culture", postalCode="01004", inseeCode="01204", city="Ailleurs"
        )

        with mock.patch("pcapi.connectors.api_adresse.search_address", return_value=search_address_response):
            self._test_autocomplete(authenticated_client, search_query, expected_texts)


class AutocompleteOffererTagTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_offerer_tags"

    @pytest.mark.parametrize(
        "search_query, expected_texts",
        [
            ("", set()),
            ("com", {"premiercom", "no-labelcom"}),
            ("no-", {"no-labelcom"}),
            ("prem", {"premiercom"}),
            ("fir", {"premiercom"}),
        ],
    )
    def test_autocomplete_offerers(self, authenticated_client, search_query, expected_texts):
        offerers_factories.OffererTagFactory(name="first", label="premiercom")
        offerers_factories.OffererTagFactory(name="no-labelcom")

        self._test_autocomplete(authenticated_client, search_query, expected_texts)


class AutocompleteCitiesTest(AutocompleteTestBase):
    endpoint = "backoffice_web.autocomplete_cities"
    expected_num_queries = 1  # only authenticated user

    @pytest.mark.parametrize(
        "search_query, search_city_response, expected_texts",
        [
            ("", [], set()),
            (" ", [], set()),
            (
                "Toulo",
                [
                    api_geo.GeoCity(insee_code="31555", name="Toulouse"),
                    api_geo.GeoCity(insee_code="83137", name="Toulon"),
                ],
                {"Toulouse (31)", "Toulon (83)"},
            ),
        ],
    )
    def test_autocomplete_cities(self, authenticated_client, search_query, search_city_response, expected_texts):
        with mock.patch("pcapi.connectors.api_geo.search_city", return_value=search_city_response):
            self._test_autocomplete(
                authenticated_client, search_query, expected_texts, expected_num_queries=self.expected_num_queries
            )
