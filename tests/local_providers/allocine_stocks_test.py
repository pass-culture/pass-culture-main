import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from local_providers import AllocineStocks
from local_providers.allocine_stocks import _parse_movie_duration, retrieve_movie_information, \
    retrieve_showtime_information, _format_poster_url, \
    _filter_only_digital_and_non_experience_showtimes, _find_showtime_by_showtime_uuid, \
    _get_showtimes_uuid_by_idAtProvider, _format_date_from_local_timezone_to_utc
from models import Offer, EventType, Product, Stock
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_venue_provider, \
    create_venue_provider_price_rule
from tests.model_creators.provider_creators import activate_provider
from tests.model_creators.specific_creators import create_product_with_event_type, create_offer_with_event_product
from utils.human_ids import humanize


class AllocineStocksTest:
    class InitTest:
        @patch('local_providers.allocine_stocks.get_movies_showtimes')
        @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
        @clean_database
        def test_should_call_allocine_api(self, mock_call_allocine_api, app):
            # Given
            theater_token = 'test'

            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Cinéma Allociné', siret='77567146400110')
            repository.save(venue)

            allocine_provider = get_provider_by_local_class('AllocineStocks')
            venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
            repository.save(venue_provider)

            # When
            AllocineStocks(venue_provider)

            # Then
            mock_call_allocine_api.assert_called_once_with('token', theater_token)

    class NextTest:
        @patch('local_providers.allocine_stocks.get_movies_showtimes')
        @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
        @freeze_time('2019-10-15 09:00:00')
        @clean_database
        def test_should_return_providable_infos_for_each_movie(self, mock_call_allocine_api, app):
            # Given
            theater_token = 'test'
            mock_call_allocine_api.return_value = iter([
                {
                    "node": {
                        "movie": {
                            "id": "TW92aWU6Mzc4MzI=",
                            "internalId": 37832,
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                                "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                            },
                            "data": {
                                "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                                "productionYear": 2001
                            },
                            "title": "Les Contes de la m\u00e8re poule",
                            "originalTitle": "Les Contes de la m\u00e8re poule",
                            "runtime": "PT0H46M0S",
                            "poster": {
                                "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                            },
                            "synopsis": "synopsis du film",
                            "releases": [
                                {
                                    "name": "Released",
                                    "releaseDate": {
                                        "date": "2001-10-03"
                                    },
                                    "data": {
                                        "visa_number": "2009993528"
                                    }
                                }
                            ],
                            "credits": {
                                "edges": [
                                    {
                                        "node": {
                                            "person": {
                                                "firstName": "Farkhondeh",
                                                "lastName": "Torabi"
                                            },
                                            "position": {
                                                "name": "DIRECTOR"
                                            }
                                        }
                                    }
                                ]
                            },
                            "cast": {
                                "backlink": {
                                    "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                    "label": "Casting complet du film sur AlloCin\u00e9"
                                },
                                "edges": []
                            },
                            "countries": [
                                {
                                    "name": "Iran",
                                    "alpha3": "IRN"
                                }
                            ],
                            "genres": [
                                "ANIMATION",
                                "FAMILY"
                            ],
                            "companies": []
                        },
                        "showtimes": [
                            {
                                "startsAt": "2019-10-29T10:30:00",
                                "diffusionVersion": "DUBBED",
                                "projection": [
                                    "DIGITAL"
                                ],
                                "experience": None
                            }
                        ]
                    }
                }
            ])

            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110',
                                 booking_email='toto@example.com')

            allocine_provider = get_provider_by_local_class('AllocineStocks')
            venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
            repository.save(venue, venue_provider)

            allocine_stocks_provider = AllocineStocks(venue_provider)

            # When
            allocine_providable_infos = next(allocine_stocks_provider)

            # Then
            assert len(allocine_providable_infos) == 3

            product_providable_info = allocine_providable_infos[0]
            offer_providable_info = allocine_providable_infos[1]
            stock_providable_info = allocine_providable_infos[2]

            assert product_providable_info.type == Product
            assert product_providable_info.id_at_providers == 'TW92aWU6Mzc4MzI='
            assert product_providable_info.date_modified_at_provider == datetime(year=2019, month=10, day=15, hour=9)

            assert offer_providable_info.type == Offer
            assert offer_providable_info.id_at_providers == 'TW92aWU6Mzc4MzI=%77567146400110-VF'
            assert offer_providable_info.date_modified_at_provider == datetime(year=2019, month=10, day=15, hour=9)

            assert stock_providable_info.type == Stock
            assert stock_providable_info.id_at_providers == 'TW92aWU6Mzc4MzI=%77567146400110#DUBBED/2019-10-29T10:30:00'
            assert stock_providable_info.date_modified_at_provider == datetime(year=2019, month=10, day=15, hour=9)


class UpdateObjectsTest:
    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_create_one_product_and_one_local_version_offer_with_movie_info(self,
                                                                                   mock_call_allocine_api,
                                                                                   mock_api_poster,
                                                                                   mock_redis,
                                                                                   app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Les Contes de la m\u00e8re poule",
                        "originalTitle": "Les Contes de la m\u00e8re poule",
                        "runtime": "PT0H46M0S",
                        "poster": {
                            "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": {
                                    "visa_number": "2009993528"
                                }
                            }
                        ],
                        "credits": {
                            "edges": [
                                {
                                    "node": {
                                        "person": {
                                            "firstName": "Farkhondeh",
                                            "lastName": "Torabi"
                                        },
                                        "position": {
                                            "name": "DIRECTOR"
                                        }
                                    }
                                }
                            ]
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "LOCAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        }
                    ]
                }
            }])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110', booking_email='toto@example.com')

        allocine_provider = activate_provider('AllocineStocks')
        venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue, venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = Offer.query.one()
        created_product = Product.query.one()

        assert created_offer.bookingEmail == 'toto@example.com'
        assert created_offer.description == "synopsis du film\nTous les détails du film sur AlloCiné:" \
                                            " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        assert created_offer.durationMinutes == 46
        assert created_offer.extraData["visa"] == "2009993528"
        assert created_offer.extraData["stageDirector"] == "Farkhondeh Torabi"
        assert not created_offer.isDuo
        assert created_offer.name == "Les Contes de la mère poule - VF"
        assert created_offer.product == created_product
        assert created_offer.type == str(EventType.CINEMA)

        assert created_product.description == "synopsis du film\nTous les détails du film sur AlloCiné:" \
                                              " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        assert created_product.durationMinutes == 46
        assert created_product.extraData["visa"] == "2009993528"
        assert created_product.extraData["stageDirector"] == "Farkhondeh Torabi"
        assert created_product.name == "Les Contes de la mère poule"
        assert created_product.type == str(EventType.CINEMA)
        mock_redis.assert_called_once()

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_create_one_product_and_one_original_version_offer_and_one_dubbed_version_offer_with_movie_info(
            self, mock_call_allocine_api, mock_api_poster, mock_redis, app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Les Contes de la m\u00e8re poule",
                        "originalTitle": "Les Contes de la m\u00e8re poule",
                        "runtime": "PT0H46M0S",
                        "poster": {
                            "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": {
                                    "visa_number": "2009993528"
                                }
                            }
                        ],
                        "credits": {
                            "edges": [
                                {
                                    "node": {
                                        "person": {
                                            "firstName": "Farkhondeh",
                                            "lastName": "Torabi"
                                        },
                                        "position": {
                                            "name": "DIRECTOR"
                                        }
                                    }
                                }
                            ]
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "ORIGINAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        },
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "DUBBED",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        },
                        {
                            "startsAt": "2019-10-29T14:30:00",
                            "diffusionVersion": "ORIGINAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        },
                        {
                            "startsAt": "2019-10-29T14:30:00",
                            "diffusionVersion": "DUBBED",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        }
                    ]
                }
            }])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110',
                             booking_email='toto@example.com')

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider,
                                               venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue, venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offers = Offer.query.all()
        created_products = Product.query.all()

        assert len(created_offers) == 2
        assert len(created_products) == 1

        original_version_offer = created_offers[0]
        assert original_version_offer.bookingEmail == 'toto@example.com'
        assert original_version_offer.description == "synopsis du film\nTous les détails du film sur AlloCiné:" \
                                                     " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        assert original_version_offer.durationMinutes == 46
        assert original_version_offer.extraData["visa"] == "2009993528"
        assert original_version_offer.extraData["stageDirector"] == "Farkhondeh Torabi"
        assert not original_version_offer.isDuo
        assert original_version_offer.name == "Les Contes de la mère poule - VO"
        assert original_version_offer.product == created_products[0]
        assert original_version_offer.type == str(EventType.CINEMA)

        dubbed_version_offer = created_offers[1]
        assert dubbed_version_offer.bookingEmail == 'toto@example.com'
        assert dubbed_version_offer.description == "synopsis du film\nTous les détails du film sur AlloCiné:" \
                                                   " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        assert dubbed_version_offer.durationMinutes == 46
        assert dubbed_version_offer.extraData["visa"] == "2009993528"
        assert dubbed_version_offer.extraData["stageDirector"] == "Farkhondeh Torabi"
        assert not dubbed_version_offer.isDuo
        assert dubbed_version_offer.name == "Les Contes de la mère poule - VF"
        assert dubbed_version_offer.product == created_products[0]
        assert dubbed_version_offer.type == str(EventType.CINEMA)

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_create_only_one_original_version_offer_when_only_original_showtimes_exist(self,
                                                                                              mock_call_allocine_api,
                                                                                              mock_api_poster,
                                                                                              mock_redis,
                                                                                              app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Les Contes de la m\u00e8re poule",
                        "originalTitle": "Les Contes de la m\u00e8re poule",
                        "runtime": "PT0H46M0S",
                        "poster": {
                            "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": {
                                    "visa_number": "2009993528"
                                }
                            }
                        ],
                        "credits": {
                            "edges": [
                                {
                                    "node": {
                                        "person": {
                                            "firstName": "Farkhondeh",
                                            "lastName": "Torabi"
                                        },
                                        "position": {
                                            "name": "DIRECTOR"
                                        }
                                    }
                                }
                            ]
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "ORIGINAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        }, {
                            "startsAt": "2019-10-29T14:30:00",
                            "diffusionVersion": "ORIGINAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        }
                    ]
                }
            }])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110',
                             booking_email='toto@example.com')

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider,
                                               venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue, venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offers = Offer.query.all()
        created_products = Product.query.all()

        assert len(created_offers) == 1
        assert len(created_products) == 1

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_update_existing_product_duration_and_update_matching_offers(self,
                                                                                mock_call_allocine_api,
                                                                                mock_api_poster,
                                                                                mock_redis,
                                                                                app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Les Contes de la m\u00e8re poule",
                        "originalTitle": "Les Contes de la m\u00e8re poule",
                        "runtime": "PT1H50M0S",
                        "poster": {
                            "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": {
                                    "visa_number": "2009993528"
                                }
                            }
                        ],
                        "credits": {
                            "edges": [
                                {
                                    "node": {
                                        "person": {
                                            "firstName": "Farkhondeh",
                                            "lastName": "Torabi"
                                        },
                                        "position": {
                                            "name": "DIRECTOR"
                                        }
                                    }
                                }
                            ]
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "DUBBED",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        },
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "ORIGINAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        }
                    ]
                }
            }])

        product = create_product_with_event_type(
            event_name='Test event',
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI="
        )

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinéma Allociné', siret='77567146400110', booking_email='toto@example.com')

        offer_vo = create_offer_with_event_product(product=product, event_name='Test event',
                                                   event_type=EventType.CINEMA,
                                                   duration_minutes=60,
                                                   id_at_providers="TW92aWU6Mzc4MzI=%77567146400110-VO", venue=venue)
        offer_vf = create_offer_with_event_product(product=product, event_name='Test event',
                                                   event_type=EventType.CINEMA,
                                                   duration_minutes=60,
                                                   id_at_providers="TW92aWU6Mzc4MzI=%77567146400110-VF", venue=venue)

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue, product, offer_vo, offer_vf, venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        existing_offers = Offer.query.all()
        existing_product = Product.query.one()

        assert len(existing_offers) == 2
        assert existing_offers[0].durationMinutes == 110
        assert existing_offers[1].durationMinutes == 110
        assert existing_product.durationMinutes == 110

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_update_existing_product_duration_and_create_new_offer_when_no_offer_exists(self,
                                                                                               mock_call_allocine_api,
                                                                                               mock_api_poster,
                                                                                               mock_redis,
                                                                                               app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Les Contes de la m\u00e8re poule",
                        "originalTitle": "Les Contes de la m\u00e8re poule",
                        "runtime": "PT1H50M0S",
                        "poster": {
                            "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": {
                                    "visa_number": "2009993528"
                                }
                            }
                        ],
                        "credits": {
                            "edges": [
                                {
                                    "node": {
                                        "person": {
                                            "firstName": "Farkhondeh",
                                            "lastName": "Torabi"
                                        },
                                        "position": {
                                            "name": "DIRECTOR"
                                        }
                                    }
                                }
                            ]
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "DUBBED",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        }
                    ]
                }
            }])

        product = create_product_with_event_type(
            event_name='Test event',
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI="
        )

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110', booking_email='toto@example.com')

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue, product, venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = Offer.query.one()
        existing_product = Product.query.one()

        assert existing_product.durationMinutes == 110
        assert created_offer.type == str(EventType.CINEMA)
        assert created_offer.name == 'Les Contes de la mère poule - VF'

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_create_product_and_new_offer_with_missing_visa_and_stage_director(self,
                                                                                      mock_call_allocine_api,
                                                                                      mock_api_poster,
                                                                                      mock_redis,
                                                                                      app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Les Contes de la m\u00e8re poule",
                        "originalTitle": "Les Contes de la m\u00e8re poule",
                        "runtime": "PT1H50M0S",
                        "poster": {
                            "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": []
                            }
                        ],
                        "credits": {
                            "edges": []
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "DUBBED",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        }
                    ]
                }
            }])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110', booking_email='toto@example.com')

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue, venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = Offer.query.one()
        created_product = Product.query.one()

        assert created_product.durationMinutes == 110
        assert created_product.extraData == {}
        assert created_offer.extraData == {}
        assert created_offer.type == str(EventType.CINEMA)
        assert created_offer.name == 'Les Contes de la mère poule - VF'

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch('local_providers.allocine_stocks.AllocineStocks.get_object_thumb')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_create_product_with_correct_thumb_and_increase_thumbCount_by_1(self,
                                                                                   mock_get_object_thumb,
                                                                                   mock_call_allocine_api,
                                                                                   mock_api_poster,
                                                                                   mock_redis,
                                                                                   app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Zombieland: Double Tap",
                        "originalTitle": "Zombieland: Double Tap",
                        "runtime": "PT1H50M0S",
                        "poster": {
                            "url": r"https:\/\/fr.web.img5.acsta.net\/pictures\/19\/08\/14\/10\/54\/4737391.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": []
                            }
                        ],
                        "credits": {
                            "edges": []
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "DUBBED",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        }
                    ]
                }
            }])
        file_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                    / '..' / '..' / 'sandboxes' / 'providers' / 'titelive_mocks' / 'provider_thumb.jpeg'
        mock_get_object_thumb.return_value = open(file_path, "rb").read()

        product = create_product_with_event_type(
            event_name='Test event',
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI=",
            thumb_count=0
        )

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110', booking_email='toto@example.com')

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue, product, venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        existing_product = Product.query.one()

        assert existing_product.thumbUrl == f"http://localhost/storage/thumbs/products/{humanize(existing_product.id)}"
        assert existing_product.thumbCount == 1

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch('local_providers.allocine_stocks.AllocineStocks.get_object_thumb')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_replace_product_thumb_when_product_has_already_one_thumb(self,
                                                                             mock_get_object_thumb,
                                                                             mock_call_allocine_api,
                                                                             mock_api_poster,
                                                                             mock_redis,
                                                                             app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Zombieland: Double Tap",
                        "originalTitle": "Zombieland: Double Tap",
                        "runtime": "PT1H50M0S",
                        "poster": {
                            "url": r"https:\/\/fr.web.img5.acsta.net\/pictures\/19\/08\/14\/10\/54\/4737391.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": {
                                    "visa_number": "2009993528"
                                }
                            }
                        ],
                        "credits": {
                            "edges": [
                                {
                                    "node": {
                                        "person": {
                                            "firstName": "Farkhondeh",
                                            "lastName": "Torabi"
                                        },
                                        "position": {
                                            "name": "DIRECTOR"
                                        }
                                    }
                                }
                            ]
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-10-29T10:30:00",
                            "diffusionVersion": "DUBBED",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        }
                    ]
                }
            }])
        file_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                    / '..' / '..' / 'sandboxes' / 'providers' / 'titelive_mocks' / 'provider_thumb.jpeg'
        mock_get_object_thumb.return_value = open(file_path, "rb").read()

        product = create_product_with_event_type(
            event_name='Test event',
            event_type=EventType.CINEMA,
            duration_minutes=60,
            id_at_providers="TW92aWU6Mzc4MzI=",
            thumb_count=1
        )

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110', booking_email='toto@example.com')

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue, product, venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        existing_product = Product.query.one()
        assert existing_product.thumbUrl == f"http://localhost/storage/thumbs/products/{humanize(existing_product.id)}"
        assert existing_product.thumbCount == 1

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_create_one_product_and_one_offer_and_associated_stocks(self,
                                                                           mock_api_poster,
                                                                           mock_call_allocine_api,
                                                                           mock_redis,
                                                                           app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Les Contes de la m\u00e8re poule",
                        "originalTitle": "Les Contes de la m\u00e8re poule",
                        "runtime": None,
                        "poster": {
                            "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": {
                                    "visa_number": "2009993528"
                                }
                            }
                        ],
                        "credits": {
                            "edges": [
                                {
                                    "node": {
                                        "person": {
                                            "firstName": "Farkhondeh",
                                            "lastName": "Torabi"
                                        },
                                        "position": {
                                            "name": "DIRECTOR"
                                        }
                                    }
                                }
                            ]
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-12-03T10:00:00",
                            "diffusionVersion": "LOCAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        },
                        {
                            "startsAt": "2019-12-03T18:00:00",
                            "diffusionVersion": "LOCAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        },
                        {
                            "startsAt": "2019-12-03T20:00:00",
                            "diffusionVersion": "LOCAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": 'experience'
                        }
                    ]
                }
            }])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110', booking_email='toto@example.com')
        repository.save(venue)

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_product = Product.query.all()
        created_offer = Offer.query.all()
        created_stock = Stock.query.all()

        vf_offer = created_offer[0]

        first_stock = created_stock[0]
        second_stock = created_stock[1]

        assert len(created_product) == 1
        assert len(created_offer) == 1
        assert len(created_stock) == 2

        assert vf_offer.name == 'Les Contes de la mère poule - VF'

        assert first_stock.offerId == vf_offer.id
        assert first_stock.available is None
        assert first_stock.price == 10
        assert first_stock.beginningDatetime == datetime(2019, 12, 3, 9, 0)
        assert first_stock.endDatetime == datetime(2019, 12, 3, 9, 0, 1)
        assert first_stock.bookingLimitDatetime == datetime(2019, 12, 3, 9, 0)

        assert second_stock.offerId == vf_offer.id
        assert second_stock.available is None
        assert second_stock.price == 10
        assert second_stock.beginningDatetime == datetime(2019, 12, 3, 17, 0)
        assert second_stock.endDatetime == datetime(2019, 12, 3, 17, 0, 1)
        assert second_stock.bookingLimitDatetime == datetime(2019, 12, 3, 17, 0)

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_create_one_product_and_two_offers_and_associated_stocks(self,
                                                                            mock_poster_get_allocine,
                                                                            mock_call_allocine_api,
                                                                            mock_redis,
                                                                            app):
        # Given
        theater_token = 'test'
        mock_call_allocine_api.return_value = iter([
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                        },
                        "data": {
                            "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                            "productionYear": 2001
                        },
                        "title": "Les Contes de la m\u00e8re poule",
                        "originalTitle": "Les Contes de la m\u00e8re poule",
                        "runtime": "PT1H50M0S",
                        "poster": {
                            "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                        },
                        "synopsis": "synopsis du film",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {
                                    "date": "2001-10-03"
                                },
                                "data": {
                                    "visa_number": "2009993528"
                                }
                            }
                        ],
                        "credits": {
                            "edges": [
                                {
                                    "node": {
                                        "person": {
                                            "firstName": "Farkhondeh",
                                            "lastName": "Torabi"
                                        },
                                        "position": {
                                            "name": "DIRECTOR"
                                        }
                                    }
                                }
                            ]
                        },
                        "cast": {
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                "label": "Casting complet du film sur AlloCin\u00e9"
                            },
                            "edges": []
                        },
                        "countries": [
                            {
                                "name": "Iran",
                                "alpha3": "IRN"
                            }
                        ],
                        "genres": [
                            "ANIMATION",
                            "FAMILY"
                        ],
                        "companies": []
                    },
                    "showtimes": [
                        {
                            "startsAt": "2019-12-03T10:00:00",
                            "diffusionVersion": "LOCAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        },
                        {
                            "startsAt": "2019-12-03T18:00:00",
                            "diffusionVersion": "ORIGINAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        },
                        {
                            "startsAt": "2019-12-03T20:00:00",
                            "diffusionVersion": "LOCAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": None
                        },
                        {
                            "startsAt": "2019-12-03T20:00:00",
                            "diffusionVersion": "LOCAL",
                            "projection": [
                                "DIGITAL"
                            ],
                            "experience": 'experience'
                        },
                        {
                            "startsAt": "2019-12-03T20:00:00",
                            "diffusionVersion": "LOCAL",
                            "projection": [
                                "NON DIGITAL"
                            ],
                            "experience": None
                        }
                    ]
                }
            }])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110', booking_email='toto@example.com')
        repository.save(venue)

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
        repository.save(venue_provider, venue_provider_price_rule)

        allocine_stocks_provider = AllocineStocks(venue_provider)

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

        assert vo_offer.name == 'Les Contes de la mère poule - VO'
        assert vf_offer.name == 'Les Contes de la mère poule - VF'

        assert vo_offer.durationMinutes == 110

        assert first_stock.offerId == vf_offer.id
        assert first_stock.available is None
        assert first_stock.price == 10
        assert first_stock.beginningDatetime == datetime(2019, 12, 3, 9, 0)
        assert first_stock.endDatetime == datetime(2019, 12, 3, 10, 50)
        assert first_stock.bookingLimitDatetime == datetime(2019, 12, 3, 9, 0)

        assert second_stock.offerId == vo_offer.id
        assert second_stock.available is None
        assert second_stock.price == 10
        assert second_stock.beginningDatetime == datetime(2019, 12, 3, 17, 0)
        assert second_stock.endDatetime == datetime(2019, 12, 3, 18, 50)
        assert second_stock.bookingLimitDatetime == datetime(2019, 12, 3, 17, 0)

        assert third_stock.offerId == vf_offer.id
        assert third_stock.available is None
        assert third_stock.price == 10
        assert third_stock.beginningDatetime == datetime(2019, 12, 3, 19, 0)
        assert third_stock.endDatetime == datetime(2019, 12, 3, 20, 50)
        assert third_stock.bookingLimitDatetime == datetime(2019, 12, 3, 19, 0)

    class WhenAllocineStockAreSynchronizedTwice:
        @patch('local_providers.allocine_stocks.get_movies_showtimes')
        @patch('local_providers.allocine_stocks.get_movie_poster')
        @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
        @clean_database
        def test_should_update_stocks_based_on_stock_date(self,
                                                          mock_poster_get_allocine,
                                                          mock_call_allocine_api,
                                                          app):
            # Given
            theater_token = 'test'
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.side_effect = [iter([
                {
                    "node": {
                        "movie": {
                            "id": "TW92aWU6Mzc4MzI=",
                            "internalId": 37832,
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                                "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                            },
                            "data": {
                                "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                                "productionYear": 2001
                            },
                            "title": "Les Contes de la m\u00e8re poule",
                            "originalTitle": "Les Contes de la m\u00e8re poule",
                            "runtime": "PT1H50M0S",
                            "poster": {
                                "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                            },
                            "synopsis": "synopsis du film",
                            "releases": [
                                {
                                    "name": "Released",
                                    "releaseDate": {
                                        "date": "2001-10-03"
                                    },
                                    "data": {
                                        "visa_number": "2009993528"
                                    }
                                }
                            ],
                            "credits": {
                                "edges": [
                                    {
                                        "node": {
                                            "person": {
                                                "firstName": "Farkhondeh",
                                                "lastName": "Torabi"
                                            },
                                            "position": {
                                                "name": "DIRECTOR"
                                            }
                                        }
                                    }
                                ]
                            },
                            "cast": {
                                "backlink": {
                                    "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                    "label": "Casting complet du film sur AlloCin\u00e9"
                                },
                                "edges": []
                            },
                            "countries": [
                                {
                                    "name": "Iran",
                                    "alpha3": "IRN"
                                }
                            ],
                            "genres": [
                                "ANIMATION",
                                "FAMILY"
                            ],
                            "companies": []
                        },
                        "showtimes": [
                            {
                                "startsAt": "2019-12-03T10:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": [
                                    "DIGITAL"
                                ],
                                "experience": None
                            },
                            {
                                "startsAt": "2019-12-04T18:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": [
                                    "DIGITAL"
                                ],
                                "experience": None
                            }
                        ]
                    }
                }]),
                iter([{
                    "node": {
                        "movie": {
                            "id": "TW92aWU6Mzc4MzI=",
                            "internalId": 37832,
                            "backlink": {
                                "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                                "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                            },
                            "data": {
                                "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                                "productionYear": 2001
                            },
                            "title": "Les Contes de la m\u00e8re poule",
                            "originalTitle": "Les Contes de la m\u00e8re poule",
                            "runtime": "PT1H50M0S",
                            "poster": {
                                "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                            },
                            "synopsis": "synopsis du film",
                            "releases": [
                                {
                                    "name": "Released",
                                    "releaseDate": {
                                        "date": "2001-10-03"
                                    },
                                    "data": {
                                        "visa_number": "2009993528"
                                    }
                                }
                            ],
                            "credits": {
                                "edges": [
                                    {
                                        "node": {
                                            "person": {
                                                "firstName": "Farkhondeh",
                                                "lastName": "Torabi"
                                            },
                                            "position": {
                                                "name": "DIRECTOR"
                                            }
                                        }
                                    }
                                ]
                            },
                            "cast": {
                                "backlink": {
                                    "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                                    "label": "Casting complet du film sur AlloCin\u00e9"
                                },
                                "edges": []
                            },
                            "countries": [
                                {
                                    "name": "Iran",
                                    "alpha3": "IRN"
                                }
                            ],
                            "genres": [
                                "ANIMATION",
                                "FAMILY"
                            ],
                            "companies": []
                        },
                        "showtimes": [
                            {
                                "startsAt": "2019-12-04T18:00:00",
                                "diffusionVersion": "LOCAL",
                                "projection": [
                                    "DIGITAL"
                                ],
                                "experience": None
                            }
                        ]
                    }
                }])
            ]

            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Cinema Allocine', siret='77567146400110',
                                 booking_email='toto@example.com')
            repository.save(venue)

            allocine_provider = get_provider_by_local_class('AllocineStocks')
            allocine_provider.isActive = True
            venue_provider = create_venue_provider(venue, allocine_provider, venue_id_at_offer_provider=theater_token)
            venue_provider_price_rule = create_venue_provider_price_rule(venue_provider)
            repository.save(venue_provider, venue_provider_price_rule)

            # When
            allocine_stocks_provider = AllocineStocks(venue_provider)
            allocine_stocks_provider.updateObjects()

            allocine_stocks_provider = AllocineStocks(venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            created_stock = Stock.query.all()
            vf_offer = Offer.query.first()

            first_stock = created_stock[0]
            second_stock = created_stock[1]

            assert len(created_stock) == 2
            assert first_stock.offerId == vf_offer.id
            assert first_stock.beginningDatetime == datetime(2019, 12, 3, 9, 0)

            assert second_stock.offerId == vf_offer.id
            assert second_stock.beginningDatetime == datetime(2019, 12, 4, 17, 0)

    @patch('local_providers.local_provider.send_venue_provider_data_to_redis')
    @patch('local_providers.allocine_stocks.get_movies_showtimes')
    @patch('local_providers.allocine_stocks.get_movie_poster')
    @patch.dict('os.environ', {'ALLOCINE_API_KEY': 'token'})
    @clean_database
    def test_should_create_one_different_offer_and_stock_for_different_venues(self,
                                                                              mock_poster_get_allocine,
                                                                              mock_call_allocine_api,
                                                                              mock_redis,
                                                                              app):
        # Given
        theater_token1 = 'test1'
        theater_token2 = 'test2'
        allocine_api_response = [{
            "node": {
                "movie": {
                    "id": "TW92aWU6Mzc4MzI=",
                    "internalId": 37832,
                    "backlink": {
                        "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                    },
                    "data": {
                        "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                        "productionYear": 2001
                    },
                    "title": "Les Contes de la m\u00e8re poule",
                    "originalTitle": "Les Contes de la m\u00e8re poule",
                    "runtime": "PT1H50M0S",
                    "poster": {
                        "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                    },
                    "synopsis": "synopsis du film",
                    "releases": [{
                        "name": "Released",
                        "releaseDate": {
                            "date": "2001-10-03"
                        },
                        "data": {
                            "visa_number": "2009993528"
                        }
                    }],
                    "credits": {
                        "edges": [{
                            "node": {
                                "person": {
                                    "firstName": "Farkhondeh",
                                    "lastName": "Torabi"
                                },
                                "position": {
                                    "name": "DIRECTOR"
                                }
                            }}
                        ]},
                    "cast": {
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                            "label": "Casting complet du film sur AlloCin\u00e9"
                        },
                        "edges": []
                    },
                    "countries": [{
                        "name": "Iran",
                        "alpha3": "IRN"
                    }],
                    "genres": [
                        "ANIMATION",
                        "FAMILY"
                    ],
                    "companies": []
                },
                "showtimes": [{
                    "startsAt": "2019-12-03T10:00:00",
                    "diffusionVersion": "LOCAL",
                    "projection": ["DIGITAL"],
                    "experience": None
                }]}
        }]
        mock_call_allocine_api.side_effect = [iter(allocine_api_response),
                                              iter(allocine_api_response)]
        mock_poster_get_allocine.return_value = bytes()

        offerer = create_offerer(siren='775671464')
        venue1 = create_venue(offerer, name='Cinema Allocine 1',
                              siret='77567146400110',
                              booking_email='toto1@example.com')
        venue2 = create_venue(offerer, name='Cinema Allocine 2',
                              siret='98765432345677',
                              booking_email='toto2@example.com')
        repository.save(venue1, venue2)

        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider1 = create_venue_provider(venue1, allocine_provider, venue_id_at_offer_provider=theater_token1)
        venue_provider_price_rule1 = create_venue_provider_price_rule(venue_provider1)
        venue_provider2 = create_venue_provider(venue2, allocine_provider, venue_id_at_offer_provider=theater_token2)
        venue_provider_price_rule2 = create_venue_provider_price_rule(venue_provider2)
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
        assert created_offer[0].venueId == venue1.id
        assert created_offer[1].venueId == venue2.id
        assert len(created_stock) == 2


class ParseMovieDurationTest:
    def test_should_convert_duration_string_to_minutes(self):
        # Given
        movie_runtime = "PT1H50M0S"

        # When
        duration_in_minutes = _parse_movie_duration(movie_runtime)

        # Then
        assert duration_in_minutes == 110

    def test_should_only_parse_hours_and_minutes(self):
        # Given
        movie_runtime = "PT11H0M15S"

        # When
        duration_in_minutes = _parse_movie_duration(movie_runtime)

        # Then
        assert duration_in_minutes == 660

    def test_should_return_None_when_null_value_given(self):
        # Given
        movie_runtime = None

        # When
        duration_in_minutes = _parse_movie_duration(movie_runtime)

        # Then
        assert not duration_in_minutes


class RetrieveMovieInformationTest:
    def test_should_retrieve_information_from_wanted_json_nodes(self):
        # Given
        movie_information = {
            "node": {
                "movie": {
                    "id": "TW92aWU6Mzc4MzI=",
                    "internalId": 37832,
                    "backlink": {
                        "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                    },
                    "data": {
                        "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                        "productionYear": 2001
                    },
                    "title": "Les Contes de la m\u00e8re poule",
                    "originalTitle": "Les Contes de la m\u00e8re poule",
                    "runtime": "PT1H50M0S",
                    "poster": {
                        "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                    },
                    "synopsis": "synopsis du film",
                    "releases": [
                        {
                            "name": "Released",
                            "releaseDate": {
                                "date": "2001-10-03"
                            },
                            "data": {
                                "visa_number": "2009993528"
                            }
                        }
                    ],
                    "credits": {
                        "edges": [
                            {
                                "node": {
                                    "person": {
                                        "firstName": "Farkhondeh",
                                        "lastName": "Torabi"
                                    },
                                    "position": {
                                        "name": "DIRECTOR"
                                    }
                                }
                            }
                        ]
                    },
                    "cast": {
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                            "label": "Casting complet du film sur AlloCin\u00e9"
                        },
                        "edges": []
                    },
                    "countries": [
                        {
                            "name": "Iran",
                            "alpha3": "IRN"
                        }
                    ],
                    "genres": [
                        "ANIMATION",
                        "FAMILY"
                    ],
                    "companies": []
                },
                "showtimes": [
                    {
                        "startsAt": "2019-10-29T10:30:00",
                        "diffusionVersion": "DUBBED",
                        "projection": [
                            "DIGITAL"
                        ],
                        "experience": None
                    }
                ]
            }
        }

        # When
        movie_parsed_information = retrieve_movie_information(movie_information['node']['movie'])

        # Then
        assert movie_parsed_information['title'] == "Les Contes de la mère poule"
        assert movie_parsed_information[
                   'description'] == "synopsis du film\nTous les détails du film sur AlloCiné:" \
                                     " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        assert movie_parsed_information["visa"] == "2009993528"
        assert movie_parsed_information["stageDirector"] == "Farkhondeh Torabi"
        assert movie_parsed_information['duration'] == 110
        assert movie_parsed_information[
                   'poster_url'] == "https://fr.web.img6.acsta.net/medias/nmedia/00/02/32/64/69215979_af.jpg"

    def test_should_not_add_operating_visa_and_stageDirector_keys_when_nodes_are_missing(self):
        # Given
        movie_information = {
            "node": {
                "movie": {
                    "id": "TW92aWU6Mzc4MzI=",
                    "internalId": 37832,
                    "backlink": {
                        "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                    },
                    "data": {
                        "eidr": r"10.5240\/EF0C-7FB2-7D20-46D1-5C8D-E",
                        "productionYear": 2001
                    },
                    "title": "Les Contes de la m\u00e8re poule",
                    "originalTitle": "Les Contes de la m\u00e8re poule",
                    "runtime": "PT1H50M0S",
                    "poster": {
                        "url": r"https:\/\/fr.web.img6.acsta.net\/medias\/nmedia\/00\/02\/32\/64\/69215979_af.jpg"
                    },
                    "synopsis": "synopsis du film",
                    "releases": [
                        {
                            "name": "Released",
                            "releaseDate": {
                                "date": "2019-11-20"
                            },
                            "data": []
                        }
                    ],
                    "credits": {
                        "edges": []
                    },
                    "cast": {
                        "backlink": {
                            "url": r"http:\/\/www.allocine.fr\/film\/fichefilm-255951\/casting\/",
                            "label": "Casting complet du film sur AlloCin\u00e9"
                        },
                        "edges": []
                    },
                    "countries": [
                        {
                            "name": "Iran",
                            "alpha3": "IRN"
                        }
                    ],
                    "genres": [
                        "ANIMATION",
                        "FAMILY"
                    ],
                    "companies": []
                },
                "showtimes": [
                    {
                        "startsAt": "2019-10-29T10:30:00",
                        "diffusionVersion": "DUBBED",
                        "projection": [
                            "DIGITAL"
                        ],
                        "experience": None
                    }
                ]
            }
        }

        # When
        movie_parsed_information = retrieve_movie_information(movie_information['node']['movie'])

        # Then
        assert movie_parsed_information['title'] == "Les Contes de la mère poule"
        assert movie_parsed_information[
                   'description'] == "synopsis du film\nTous les détails du film sur AlloCiné:" \
                                     " http://www.allocine.fr/film/fichefilm_gen_cfilm=37832.html"
        assert "visa" not in movie_parsed_information
        assert "stageDirector" not in movie_parsed_information
        assert movie_parsed_information['duration'] == 110

    def test_should_raise_key_error_exception_when_missing_keys_in_movie_information(self):
        # Given
        movie_information = {
            'node': {
                'movie': {
                    "id": "TW92aWU6Mzc4MzI=",
                    "backlink": {
                        "url": r"http:\/\/www.allocine.fr\/film\/fichefilm_gen_cfilm=37832.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9"
                    },
                    "title": "Les Contes de la m\u00e8re poule",
                }
            }
        }

        # When
        with pytest.raises(KeyError):
            retrieve_movie_information(movie_information['node']['movie'])


class RetrieveShowtimeInformationTest:
    def test_should_retrieve_showtime_information_from_allocine_json_response(self):
        # Given
        movie_showtime = {"startsAt": "2019-12-03T20:00:00",
                          "diffusionVersion": "LOCAL",
                          "projection": ["NON DIGITAL"],
                          "experience": None}

        # When
        parsed_movie_showtime = retrieve_showtime_information(movie_showtime)

        # Then
        assert parsed_movie_showtime == {"startsAt": datetime(2019, 12, 3, 20, 0),
                                         "diffusionVersion": "LOCAL",
                                         "projection": "NON DIGITAL",
                                         "experience": None}

    def test_should_raise_key_error_exception_when_missing_keys_in_showtime_information(self):
        # Given
        movie_showtime = {"startsAt": "2019-12-03T20:00:00", "diffusionVersion": "LOCAL", "experience": None}

        # When
        with pytest.raises(KeyError):
            retrieve_showtime_information(movie_showtime)


class FormatPosterUrlTest:
    def test_should_return_url_in_correct_format(self):
        # Given
        url = "https:\/\/fr.web.img4.acsta.net\/pictures\/19\/07\/23\/15\/55\/2940058.jpg"

        # When
        formatted_url = _format_poster_url(url)

        # Then
        assert formatted_url == "https://fr.web.img4.acsta.net/pictures/19/07/23/15/55/2940058.jpg"


class FormatNaiveDateToUtcTest:
    def test_should_convert_date_to_utc_timezone(self):
        # Given
        local_date = datetime(2019, 12, 3, 20, 0)
        local_tz = 'America/Cayenne'

        # When
        date_in_utc = _format_date_from_local_timezone_to_utc(local_date, local_tz)

        # Then
        assert date_in_utc.hour == 23
        assert date_in_utc.tzname() == 'UTC'


class FilterOnlyDigitalAndNonExperiencedShowtimesTest:
    def test_should_filter_only_digital_and_non_experience_showtimes(self):
        # Given
        movie_information = [
            {"startsAt": "2019-12-03T10:00:00",
             "diffusionVersion": "LOCAL",
             "projection": ["DIGITAL"],
             "experience": None},
            {"startsAt": "2019-12-03T18:00:00",
             "diffusionVersion": "ORIGINAL",
             "projection": ["NON DIGITAL"],
             "experience": 'experience'},
            {"startsAt": "2019-12-03T20:00:00",
             "diffusionVersion": "LOCAL",
             "projection": ["DIGITAL"],
             "experience": 'experience'},
            {"startsAt": "2019-12-03T20:00:00",
             "diffusionVersion": "LOCAL",
             "projection": ["NON DIGITAL"],
             "experience": None}
        ]

        # When
        filtered_movie_showtimes = _filter_only_digital_and_non_experience_showtimes(movie_information)

        # Then
        assert filtered_movie_showtimes == [
            {"startsAt": "2019-12-03T10:00:00",
             "diffusionVersion": "LOCAL",
             "projection": ["DIGITAL"],
             "experience": None}
        ]


class FindShowtimesByShowtimeUUIDTest:
    def test_should_filter_on_begining_date(self):
        # Given
        showtimes = [
            {
                'diffusionVersion': 'LOCAL',
                'experience': None,
                'projection': ['DIGITAL'],
                'startsAt': '2019-12-03T10:00:00'
            },
            {
                'diffusionVersion': 'LOCAL',
                'experience': None,
                'projection': ['DIGITAL'],
                'startsAt': '2019-12-04T18:00:00'
            }
        ]

        # When
        showtime = _find_showtime_by_showtime_uuid(showtimes, 'LOCAL/2019-12-04T18:00:00')

        # Then
        assert showtime == {
            'diffusionVersion': 'LOCAL',
            'experience': None,
            'projection': ['DIGITAL'],
            'startsAt': '2019-12-04T18:00:00'
        }

    def test_should_return_none_when_no_showtimes_found(self):
        # Given
        showtimes = [
            {
                'diffusionVersion': 'LOCAL',
                'experience': None,
                'projection': ['DIGITAL'],
                'startsAt': '2019-12-04T18:00:00'
            },
            {
                'diffusionVersion': 'LOCAL',
                'experience': None,
                'projection': ['DIGITAL'],
                'startsAt': '2019-12-04T18:00:00'
            }
        ]

        # When
        showtime = _find_showtime_by_showtime_uuid(showtimes, 'DUBBED/2019-12-04T18:00:00')

        # Then
        assert showtime is None


class GetShowtimeUUIDFromIdAtProviderTest:
    def test_should_return_the_right_uuid(self):
        # When
        showtime_uuid = _get_showtimes_uuid_by_idAtProvider('TW92aWU6Mzc4MzI=%77567146400110#LOCAL/2019-12-04T18:00:00')

        # Then
        assert showtime_uuid == 'LOCAL/2019-12-04T18:00:00'
