import copy
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers import AllocineStocks
from pcapi.model_creators.generic_creators import create_allocine_venue_provider
from pcapi.model_creators.generic_creators import create_allocine_venue_provider_price_rule
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_product_with_event_type
from pcapi.models import EventType
from pcapi.models import Offer
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.repository import repository
import pcapi.sandboxes
from pcapi.utils.human_ids import humanize
from src.pcapi.core.offers.factories import VenueFactory


MOVIE_INFO = {
    "id": "TW92aWU6Mzc4MzI=",
    "type": "FEATURE_FILM",
    "internalId": 37832,
    "backlink": {
        "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
    },
    "data": {"eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E", "productionYear": 2001},
    "title": "Les Contes de la m\u00e8re poule",
    "originalTitle": "Les Contes de la m\u00e8re poule",
    "runtime": "PT0H46M0S",
    "poster": {"url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"},
    "synopsis": "synopsis du film",
    "releases": [
        {
            "name": "Released",
            "releaseDate": {"date": "2001-10-03"},
            "data": {"visa_number": "2009993528"},
        }
    ],
    "credits": {
        "edges": [
            {
                "node": {
                    "person": {"firstName": "Farkhondeh", "lastName": "Torabi"},
                    "position": {"name": "DIRECTOR"},
                }
            }
        ]
    },
    "cast": {
        "backlink": {
            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
            "label": "Casting complet du film sur AlloCin\u00e9",
        },
        "edges": [
            {
                "node": {
                    "actor": {"firstName": "Chloë Grace", "lastName": "Moretz"},
                    "role": "Kayla",
                }
            },
            {"node": {"actor": None, "role": "Tom/Jerry"}},
            {
                "node": {
                    "actor": {"firstName": "Michael", "lastName": "Peña"},
                    "role": "Terence",
                }
            },
        ],
    },
    "countries": [{"name": "Iran", "alpha3": "IRN"}],
    "genres": ["ANIMATION", "FAMILY"],
    "companies": [
        {
            "activity": "Distribution",
            "company": {"name": "Warner Bros. France"},
        },
        {"activity": "Production", "company": {"name": "The Story Company"}},
    ],
}


class AllocineStocksTest:
    class InitTest:
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_call_allocine_api(self, mock_call_allocine_api, app):
            # Given
            theater_token = "test"

            offerer = create_offerer(siren="775671464")
            venue = create_venue(offerer, name="Cinéma Allociné", siret="77567146400110")
            repository.save(venue)

            allocine_provider = get_provider_by_local_class("AllocineStocks")
            allocine_venue_provider = create_allocine_venue_provider(
                venue, allocine_provider, venue_id_at_offer_provider=theater_token
            )

            repository.save(allocine_venue_provider)

            # When
            AllocineStocks(allocine_venue_provider)

            # Then
            mock_call_allocine_api.assert_called_once_with("token", theater_token)

    class NextTest:
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @freeze_time("2019-10-15 09:00:00")
        @pytest.mark.usefixtures("db_session")
        def test_should_return_providable_infos_for_each_movie(self, mock_call_allocine_api, app):
            # Given
            mock_call_allocine_api.return_value = iter(
                [
                    {
                        "node": {
                            "movie": MOVIE_INFO,
                            "showtimes": [
                                {
                                    "startsAt": "2019-10-29T10:30:00",
                                    "diffusionVersion": "DUBBED",
                                    "projection": ["DIGITAL"],
                                    "experience": None,
                                }
                            ],
                        }
                    }
                ]
            )

            offerer = create_offerer(siren="775671464")
            venue = create_venue(
                offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com"
            )

            allocine_provider = get_provider_by_local_class("AllocineStocks")
            allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
            repository.save(venue, allocine_venue_provider)

            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

            # When
            allocine_providable_infos = next(allocine_stocks_provider)

            # Then
            assert len(allocine_providable_infos) == 3

            product_providable_info = allocine_providable_infos[0]
            offer_providable_info = allocine_providable_infos[1]
            stock_providable_info = allocine_providable_infos[2]

            assert product_providable_info.type == Product
            assert product_providable_info.id_at_providers == "TW92aWU6Mzc4MzI="
            assert product_providable_info.new_id_at_provider == "TW92aWU6Mzc4MzI="
            assert product_providable_info.date_modified_at_provider == datetime(year=2019, month=10, day=15, hour=9)

            assert offer_providable_info.type == Offer
            assert offer_providable_info.id_at_providers == "TW92aWU6Mzc4MzI=%77567146400110-VF"
            assert offer_providable_info.new_id_at_provider == "TW92aWU6Mzc4MzI=%77567146400110-VF"
            assert offer_providable_info.date_modified_at_provider == datetime(year=2019, month=10, day=15, hour=9)

            assert stock_providable_info.type == Stock
            assert stock_providable_info.id_at_providers == "TW92aWU6Mzc4MzI=%77567146400110#DUBBED/2019-10-29T10:30:00"
            assert (
                stock_providable_info.new_id_at_provider == "TW92aWU6Mzc4MzI=%77567146400110#DUBBED/2019-10-29T10:30:00"
            )
            assert stock_providable_info.date_modified_at_provider == datetime(year=2019, month=10, day=15, hour=9)


class UpdateObjectsTest:
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_one_product_and_one_local_version_offer_with_movie_info(
        self, mock_call_allocine_api, mock_api_poster
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "LOCAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            }
                        ],
                    }
                }
            ]
        )

        offerer = create_offerer(siren="775671464")
        venue = VenueFactory(
            managingOfferer=offerer,
            name="Cinema Allocine",
            siret="77567146400110",
            bookingEmail="toto@example.com",
            withdrawalDetails="Modalités",
        )

        allocine_provider = activate_provider("AllocineStocks")
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(venue, allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = Offer.query.one()
        created_product = Product.query.one()

        assert created_offer.bookingEmail == "toto@example.com"
        assert (
            created_offer.description == "synopsis du film\nTous les détails du film sur AlloCiné:"
            " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        )
        assert created_offer.durationMinutes == 46
        assert created_offer.extraData == {
            "visa": "2009993528",
            "stageDirector": "Farkhondeh Torabi",
            "theater": {"allocine_movie_id": 37832, "allocine_room_id": "PXXXXX"},
            "genres": ["ANIMATION", "FAMILY"],
            "type": "FEATURE_FILM",
            "companies": [
                {"activity": "Distribution", "company": {"name": "Warner Bros. France"}},
                {"activity": "Production", "company": {"name": "The Story Company"}},
            ],
            "releaseDate": "2001-10-03",
            "countries": ["Iran"],
            "cast": ["Chloë Grace Moretz", "Michael Peña"],
        }

        assert not created_offer.isDuo
        assert created_offer.name == "Les Contes de la mère poule - VF"
        assert created_offer.product == created_product
        assert created_offer.type == str(EventType.CINEMA)
        assert created_offer.withdrawalDetails == venue.withdrawalDetails

        assert (
            created_product.description == "synopsis du film\nTous les détails du film sur AlloCiné:"
            " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        )
        assert created_product.durationMinutes == 46
        assert created_product.extraData == {
            "visa": "2009993528",
            "stageDirector": "Farkhondeh Torabi",
            "genres": ["ANIMATION", "FAMILY"],
            "type": "FEATURE_FILM",
            "companies": [
                {"activity": "Distribution", "company": {"name": "Warner Bros. France"}},
                {"activity": "Production", "company": {"name": "The Story Company"}},
            ],
            "releaseDate": "2001-10-03",
            "countries": ["Iran"],
            "cast": ["Chloë Grace Moretz", "Michael Peña"],
        }

        assert created_product.name == "Les Contes de la mère poule"
        assert created_product.type == str(EventType.CINEMA)

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_one_product_and_one_original_version_offer_and_one_dubbed_version_offer_with_movie_info(
        self, mock_call_allocine_api, mock_api_poster
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "ORIGINAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "DUBBED",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-10-29T14:30:00",
                                "diffusionVersion": "ORIGINAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-10-29T14:30:00",
                                "diffusionVersion": "DUBBED",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                        ],
                    }
                }
            ]
        )

        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com")

        allocine_provider = get_provider_by_local_class("AllocineStocks")
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(venue, allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offers = Offer.query.all()
        created_products = Product.query.all()

        assert len(created_offers) == 2
        assert len(created_products) == 1

        original_version_offer = created_offers[0]
        assert original_version_offer.bookingEmail == "toto@example.com"
        assert (
            original_version_offer.description == "synopsis du film\nTous les détails du film sur AlloCiné:"
            " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        )
        assert original_version_offer.durationMinutes == 46
        assert original_version_offer.extraData["visa"] == "2009993528"
        assert original_version_offer.extraData["stageDirector"] == "Farkhondeh Torabi"
        assert not original_version_offer.isDuo
        assert original_version_offer.name == "Les Contes de la mère poule - VO"
        assert original_version_offer.product == created_products[0]
        assert original_version_offer.type == str(EventType.CINEMA)

        dubbed_version_offer = created_offers[1]
        assert dubbed_version_offer.bookingEmail == "toto@example.com"
        assert (
            dubbed_version_offer.description == "synopsis du film\nTous les détails du film sur AlloCiné:"
            " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        )
        assert dubbed_version_offer.durationMinutes == 46
        assert dubbed_version_offer.extraData["visa"] == "2009993528"
        assert dubbed_version_offer.extraData["stageDirector"] == "Farkhondeh Torabi"
        assert not dubbed_version_offer.isDuo
        assert dubbed_version_offer.name == "Les Contes de la mère poule - VF"
        assert dubbed_version_offer.product == created_products[0]
        assert dubbed_version_offer.type == str(EventType.CINEMA)

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_only_one_original_version_offer_when_only_original_showtimes_exist(
        self, mock_call_allocine_api, mock_api_poster
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "ORIGINAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-10-29T14:30:00",
                                "diffusionVersion": "ORIGINAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                        ],
                    }
                }
            ]
        )

        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com")

        allocine_provider = get_provider_by_local_class("AllocineStocks")
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)

        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(venue, allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offers = Offer.query.all()
        created_products = Product.query.all()

        assert len(created_offers) == 1
        assert len(created_products) == 1

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_update_existing_product_duration_and_update_matching_offers(
        self, mock_call_allocine_api, mock_api_poster
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "DUBBED",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "ORIGINAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                        ],
                    }
                }
            ]
        )

        product = create_product_with_event_type(
            event_name="Test event",
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI=",
        )

        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Cinéma Allociné", siret="77567146400110", booking_email="toto@example.com")

        offer_vo = create_offer_with_event_product(
            product=product,
            event_name="Test event",
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI=%77567146400110-VO",
            venue=venue,
        )
        offer_vf = create_offer_with_event_product(
            product=product,
            event_name="Test event",
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI=%77567146400110-VF",
            venue=venue,
        )

        allocine_provider = get_provider_by_local_class("AllocineStocks")
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(venue, product, offer_vo, offer_vf, allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        existing_offers = Offer.query.all()
        existing_product = Product.query.one()

        assert len(existing_offers) == 2
        assert existing_offers[0].durationMinutes == 46
        assert existing_offers[1].durationMinutes == 46
        assert existing_product.durationMinutes == 46

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_update_existing_product_duration_and_create_new_offer_when_no_offer_exists(
        self, mock_call_allocine_api, mock_api_poster
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "DUBBED",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            }
                        ],
                    }
                }
            ]
        )

        product = create_product_with_event_type(
            event_name="Test event",
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI=",
        )

        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com")

        allocine_provider = get_provider_by_local_class("AllocineStocks")
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(venue, product, allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = Offer.query.one()
        existing_product = Product.query.one()

        assert existing_product.durationMinutes == 46
        assert created_offer.type == str(EventType.CINEMA)
        assert created_offer.name == "Les Contes de la mère poule - VF"

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_product_and_new_offer_with_missing_visa_and_stage_director(
        self, mock_call_allocine_api, mock_api_poster
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "DUBBED",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            }
                        ],
                    }
                }
            ]
        )

        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com")

        allocine_provider = get_provider_by_local_class("AllocineStocks")
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider, internal_id="P12345")
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(venue, allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = Offer.query.one()
        created_product = Product.query.one()

        assert created_product.durationMinutes == 46
        assert created_product.extraData == {
            "visa": "2009993528",
            "stageDirector": "Farkhondeh Torabi",
            "genres": ["ANIMATION", "FAMILY"],
            "type": "FEATURE_FILM",
            "companies": [
                {"activity": "Distribution", "company": {"name": "Warner Bros. France"}},
                {"activity": "Production", "company": {"name": "The Story Company"}},
            ],
            "releaseDate": "2001-10-03",
            "countries": ["Iran"],
            "cast": ["Chloë Grace Moretz", "Michael Peña"],
        }
        assert created_offer.extraData == {
            "visa": "2009993528",
            "stageDirector": "Farkhondeh Torabi",
            "theater": {"allocine_movie_id": 37832, "allocine_room_id": "P12345"},
            "genres": ["ANIMATION", "FAMILY"],
            "type": "FEATURE_FILM",
            "companies": [
                {"activity": "Distribution", "company": {"name": "Warner Bros. France"}},
                {"activity": "Production", "company": {"name": "The Story Company"}},
            ],
            "releaseDate": "2001-10-03",
            "countries": ["Iran"],
            "cast": ["Chloë Grace Moretz", "Michael Peña"],
        }

        assert created_offer.type == str(EventType.CINEMA)
        assert created_offer.name == "Les Contes de la mère poule - VF"

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_not_create_product_and_offer_when_missing_required_information_in_api_response(
        self, mock_call_allocine_api, mock_api_poster
    ):
        # Given
        movie_information = copy.deepcopy(MOVIE_INFO)
        del movie_information["title"]

        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": movie_information,
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "DUBBED",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            }
                        ],
                    }
                }
            ]
        )

        offerer = create_offerer()
        venue = create_venue(offerer)

        allocine_provider = activate_provider("AllocineStocks")
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        allocine_venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(allocine_venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        assert Offer.query.count() == 0
        assert Product.query.count() == 0

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.local_providers.allocine.allocine_stocks.AllocineStocks.get_object_thumb")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_product_with_correct_thumb_and_increase_thumbCount_by_1(
        self, mock_get_object_thumb, mock_call_allocine_api, mock_api_poster
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "DUBBED",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            }
                        ],
                    }
                }
            ]
        )
        file_path = Path(pcapi.sandboxes.__path__[0]) / "providers" / "titelive_mocks" / "provider_thumb.jpeg"
        with open(file_path, "rb") as thumb_file:
            mock_get_object_thumb.return_value = thumb_file.read()

        product = create_product_with_event_type(
            event_name="Test event",
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI=",
            thumb_count=0,
        )

        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com")

        allocine_provider = get_provider_by_local_class("AllocineStocks")
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(venue, product, allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        existing_product = Product.query.one()

        assert existing_product.thumbUrl == f"http://localhost/storage/thumbs/products/{humanize(existing_product.id)}"
        assert existing_product.thumbCount == 1

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.local_providers.allocine.allocine_stocks.AllocineStocks.get_object_thumb")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_replace_product_thumb_when_product_has_already_one_thumb(
        self, mock_get_object_thumb, mock_call_allocine_api, mock_api_poster
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "DUBBED",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            }
                        ],
                    }
                }
            ]
        )
        file_path = Path(pcapi.sandboxes.__path__[0]) / "providers" / "titelive_mocks" / "provider_thumb.jpeg"
        with open(file_path, "rb") as thumb_file:
            mock_get_object_thumb.return_value = thumb_file.read()

        product = create_product_with_event_type(
            event_name="Test event",
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI=",
            thumb_count=1,
        )

        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com")

        allocine_provider = get_provider_by_local_class("AllocineStocks")
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(venue, product, allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        existing_product = Product.query.one()
        assert existing_product.thumbUrl == f"http://localhost/storage/thumbs/products/{humanize(existing_product.id)}"
        assert existing_product.thumbCount == 1

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_one_product_and_one_offer_and_associated_stocks(
        self, mock_api_poster, mock_call_allocine_api
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-12-03T10:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-12-03T18:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-12-03T20:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": ["DIGITAL"],
                                "experience": "experience",
                            },
                        ],
                    }
                }
            ]
        )

        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com")
        repository.save(venue)

        allocine_provider = get_provider_by_local_class("AllocineStocks")
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_product = Product.query.all()
        created_offer = Offer.query.all()
        created_stock = Stock.query.all()

        first_stock = created_stock[0]
        second_stock = created_stock[1]

        assert len(created_product) == 1
        assert len(created_offer) == 1
        assert len(created_stock) == 2

        vf_offer = Offer.query.filter(Offer.name.contains("VF")).one()

        assert vf_offer is not None
        assert vf_offer.name == "Les Contes de la mère poule - VF"

        assert first_stock.offerId == vf_offer.id
        assert first_stock.quantity is None
        assert first_stock.price == 10
        assert first_stock.beginningDatetime == datetime(2019, 12, 3, 9, 0)
        assert first_stock.bookingLimitDatetime == datetime(2019, 12, 3, 9, 0)

        assert second_stock.offerId == vf_offer.id
        assert second_stock.quantity is None
        assert second_stock.price == 10
        assert second_stock.beginningDatetime == datetime(2019, 12, 3, 17, 0)
        assert second_stock.bookingLimitDatetime == datetime(2019, 12, 3, 17, 0)

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_one_product_and_two_offers_and_associated_stocks(
        self, mock_poster_get_allocine, mock_call_allocine_api
    ):
        # Given
        mock_call_allocine_api.return_value = iter(
            [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-12-03T10:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-12-03T18:00:00",
                                "diffusionVersion": "ORIGINAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-12-03T20:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            },
                            {
                                "startsAt": "2019-12-03T20:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": ["DIGITAL"],
                                "experience": "experience",
                            },
                            {
                                "startsAt": "2019-12-03T20:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": ["NON DIGITAL"],
                                "experience": None,
                            },
                        ],
                    }
                }
            ]
        )

        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com")
        repository.save(venue)

        allocine_provider = get_provider_by_local_class("AllocineStocks")
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
        repository.save(allocine_venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_product = Product.query.all()
        created_offer = Offer.query.all()
        created_stock = Stock.query.all()

        vo_offer = created_offer[0]
        vf_offer = created_offer[1]

        first_stock = created_stock[0]
        second_stock = created_stock[1]
        third_stock = created_stock[2]

        assert len(created_product) == 1
        assert len(created_offer) == 2
        assert len(created_stock) == 3

        assert vo_offer.name == "Les Contes de la mère poule - VO"
        assert vf_offer.name == "Les Contes de la mère poule - VF"

        assert vo_offer.durationMinutes == 46

        assert first_stock.offerId == vf_offer.id
        assert first_stock.quantity is None
        assert first_stock.price == 10
        assert first_stock.beginningDatetime == datetime(2019, 12, 3, 9, 0)
        assert first_stock.bookingLimitDatetime == datetime(2019, 12, 3, 9, 0)

        assert second_stock.offerId == vo_offer.id
        assert second_stock.quantity is None
        assert second_stock.price == 10
        assert second_stock.beginningDatetime == datetime(2019, 12, 3, 17, 0)
        assert second_stock.bookingLimitDatetime == datetime(2019, 12, 3, 17, 0)

        assert third_stock.offerId == vf_offer.id
        assert third_stock.quantity is None
        assert third_stock.price == 10
        assert third_stock.beginningDatetime == datetime(2019, 12, 3, 19, 0)
        assert third_stock.bookingLimitDatetime == datetime(2019, 12, 3, 19, 0)

    class WhenAllocineStockAreSynchronizedTwiceTest:
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_update_stocks_based_on_stock_date(self, mock_poster_get_allocine, mock_call_allocine_api, app):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.side_effect = [
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                    {
                                        "startsAt": "2019-12-04T18:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                ],
                            }
                        }
                    ]
                ),
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-04T18:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    }
                                ],
                            }
                        }
                    ]
                ),
            ]

            offerer = create_offerer(siren="775671464")
            venue = create_venue(
                offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com"
            )
            repository.save(venue)

            allocine_provider = get_provider_by_local_class("AllocineStocks")
            allocine_provider.isActive = True
            allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
            venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
            repository.save(allocine_venue_provider, venue_provider_price_rule)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            created_stock = Stock.query.order_by(Stock.beginningDatetime).all()
            vf_offer = Offer.query.first()

            first_stock = created_stock[0]
            second_stock = created_stock[1]

            assert len(created_stock) == 2
            assert first_stock.offerId == vf_offer.id
            assert first_stock.beginningDatetime == datetime(2019, 12, 3, 9, 0)

            assert second_stock.offerId == vf_offer.id
            assert second_stock.beginningDatetime == datetime(2019, 12, 4, 17, 0)

        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_create_one_different_offer_and_stock_for_different_venues(
            self, mock_poster_get_allocine, mock_call_allocine_api
        ):
            # Given
            theater_token1 = "test1"
            theater_token2 = "test2"
            allocine_api_response = [
                {
                    "node": {
                        "movie": MOVIE_INFO,
                        "showtimes": [
                            {
                                "startsAt": "2019-12-03T10:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": ["DIGITAL"],
                                "experience": None,
                            }
                        ],
                    }
                }
            ]
            mock_call_allocine_api.side_effect = [iter(allocine_api_response), iter(allocine_api_response)]
            mock_poster_get_allocine.return_value = bytes()

            offerer = create_offerer(siren="775671464")
            venue1 = create_venue(
                offerer, name="Cinema Allocine 1", siret="77567146400110", booking_email="toto1@example.com"
            )
            venue2 = create_venue(
                offerer, name="Cinema Allocine 2", siret="98765432345677", booking_email="toto2@example.com"
            )
            repository.save(venue1, venue2)

            allocine_provider = get_provider_by_local_class("AllocineStocks")
            allocine_provider.isActive = True

            venue_provider1 = create_allocine_venue_provider(venue1, allocine_provider, internal_id="P12345")
            venue_provider1.venueIdAtOfferProvider = theater_token1
            venue_provider_price_rule1 = create_allocine_venue_provider_price_rule(venue_provider1)
            venue_provider2 = create_allocine_venue_provider(venue2, allocine_provider, internal_id="C12345")
            venue_provider2.venueIdAtOfferProvider = theater_token2
            venue_provider_price_rule2 = create_allocine_venue_provider_price_rule(venue_provider2)
            repository.save(venue_provider1, venue_provider2, venue_provider_price_rule1, venue_provider_price_rule2)

            allocine_stocks_provider1 = AllocineStocks(venue_provider1)
            allocine_stocks_provider1.updateObjects()

            allocine_stocks_provider2 = AllocineStocks(venue_provider2)
            # When
            allocine_stocks_provider2.updateObjects()

            # Then
            created_product = Product.query.all()
            created_offer = Offer.query.all()
            created_stock = Stock.query.all()

            assert mock_poster_get_allocine.call_count == 2
            assert len(created_product) == 1
            assert len(created_offer) == 2
            assert Offer.query.filter(Offer.venueId == venue1.id).count() == 1
            assert Offer.query.filter(Offer.venueId == venue2.id).count() == 1
            assert len(created_stock) == 2

        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_update_stocks_info_after_pro_user_modification(
            self, mock_poster_get_allocine, mock_call_allocine_api, app
        ):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.side_effect = [
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                    {
                                        "startsAt": "2019-12-04T18:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                ],
                            }
                        }
                    ]
                ),
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                    {
                                        "startsAt": "2019-12-04T18:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                ],
                            }
                        }
                    ]
                ),
            ]

            offerer = create_offerer(siren="775671464")
            venue = create_venue(
                offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com"
            )
            repository.save(venue)

            allocine_provider = activate_provider("AllocineStocks")
            allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
            venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
            repository.save(allocine_venue_provider, venue_provider_price_rule)

            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            created_stocks = Stock.query.order_by(Stock.beginningDatetime).all()

            first_stock = created_stocks[0]
            first_stock.fieldsUpdated = ["quantity", "price"]
            first_stock.quantity = 100
            first_stock.price = 20

            second_stock = created_stocks[1]
            second_stock.fieldsUpdated = ["bookingLimitDatetime"]
            second_stock.bookingLimitDatetime = datetime(2019, 12, 4, 15, 0)

            repository.save(first_stock, second_stock)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            assert len(created_stocks) == 2
            assert first_stock.quantity == 100
            assert first_stock.price == 20
            assert first_stock.bookingLimitDatetime == datetime(2019, 12, 3, 9, 0)

            assert second_stock.quantity is None
            assert second_stock.price == 10
            assert second_stock.bookingLimitDatetime == datetime(2019, 12, 4, 15, 0)

    class WhenOfferHasBeenManuallyUpdatedTest:
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_preserve_manual_modification(self, mock_poster_get_allocine, mock_call_allocine_api, app):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.side_effect = [
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                    {
                                        "startsAt": "2019-12-04T18:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                ],
                            }
                        }
                    ]
                ),
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                    {
                                        "startsAt": "2019-12-04T18:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                ],
                            }
                        }
                    ]
                ),
            ]

            offerer = create_offerer(siren="775671464")
            venue = create_venue(
                offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com"
            )
            repository.save(venue)

            allocine_provider = activate_provider("AllocineStocks")
            allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
            venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
            repository.save(allocine_venue_provider, venue_provider_price_rule)

            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            created_offer = Offer.query.one()
            created_offer.isDuo = True
            created_offer.fieldsUpdated = ["isDuo"]
            repository.save(created_offer)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            created_offer = Offer.query.one()
            assert created_offer.isDuo is True

    class WhenStockHasBeenManuallyDeletedTest:
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_preserve_deletion(self, mock_poster_get_allocine, mock_call_allocine_api, app):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.side_effect = [
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    }
                                ],
                            }
                        }
                    ]
                ),
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    }
                                ],
                            }
                        }
                    ]
                ),
            ]

            offerer = create_offerer(siren="775671464")
            venue = create_venue(offerer, name="Cinema Allocine", siret="77567146400110")
            repository.save(venue)

            allocine_provider = activate_provider("AllocineStocks")
            allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
            venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)
            repository.save(allocine_venue_provider, venue_provider_price_rule)

            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            created_stock = Stock.query.one()
            created_stock.isSoftDeleted = True

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            created_stock = Stock.query.one()
            assert created_stock.isSoftDeleted is True

    class WhenSettingDefaultValuesAtImportTest:
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_preserve_is_duo_default_value(self, mock_poster_get_allocine, mock_call_allocine_api, app):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.side_effect = [
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                    {
                                        "startsAt": "2019-12-04T18:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                ],
                            }
                        }
                    ]
                ),
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                    {
                                        "startsAt": "2019-12-04T18:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    },
                                ],
                            }
                        }
                    ]
                ),
            ]

            offerer = create_offerer(siren="775671464")
            venue = create_venue(
                offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com"
            )
            repository.save(venue)

            allocine_provider = activate_provider("AllocineStocks")
            allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider, is_duo=True)
            venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)

            repository.save(allocine_venue_provider, venue_provider_price_rule)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            created_offer = Offer.query.one()
            assert created_offer.isDuo

        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_preserve_quantity_default_value(self, mock_poster_get_allocine, mock_call_allocine_api, app):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.side_effect = [
                iter(
                    [
                        {
                            "node": {
                                "movie": MOVIE_INFO,
                                "showtimes": [
                                    {
                                        "startsAt": "2019-12-03T10:00:00",
                                        "diffusionVersion": "LOCAL",
                                        "projection": ["DIGITAL"],
                                        "experience": None,
                                    }
                                ],
                            }
                        }
                    ]
                )
            ]

            offerer = create_offerer(siren="775671464")
            venue = create_venue(
                offerer, name="Cinema Allocine", siret="77567146400110", booking_email="toto@example.com"
            )
            repository.save(venue)

            allocine_provider = activate_provider("AllocineStocks")
            allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider, quantity=50)
            venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider)

            repository.save(allocine_venue_provider, venue_provider_price_rule)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            stock = Stock.query.one()
            assert stock.quantity == 50


class GetObjectThumbTest:
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_get_movie_poster_if_poster_url_exist(self, mock_poster_get_allocine, mock_call_allocine_api, app):
        # Given
        mock_poster_get_allocine.return_value = "poster_thumb"
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = activate_provider("AllocineStocks")
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        repository.save(allocine_venue_provider)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
        allocine_stocks_provider.movie_information = dict()
        allocine_stocks_provider.movie_information["poster_url"] = "http://url.example.com"

        # When
        poster_thumb = allocine_stocks_provider.get_object_thumb()

        # Then
        mock_poster_get_allocine.assert_called_once_with("http://url.example.com")
        assert poster_thumb == "poster_thumb"

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movies_showtimes")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_return_empty_thumb_if_poster_does_not_exist(
        self, mock_poster_get_allocine, mock_call_allocine_api, app
    ):
        # Given
        mock_poster_get_allocine.return_value = "poster_thumb"
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = activate_provider("AllocineStocks")
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        repository.save(allocine_venue_provider)

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
        allocine_stocks_provider.movie_information = dict()

        # When
        poster_thumb = allocine_stocks_provider.get_object_thumb()

        # Then
        mock_poster_get_allocine.assert_not_called()
        assert poster_thumb == bytes()
