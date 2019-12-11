from datetime import datetime

import pytest

from local_providers.allocine_stocks import _parse_movie_duration, retrieve_movie_information, \
    retrieve_showtime_information, _format_poster_url, _get_stock_number_from_id_at_providers, \
    _format_date_from_local_timezone_to_utc, _filter_only_digital_and_non_experience_showtimes


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


class GetStockNumberFromStockIdTest:
    def test_should_return_the_right_stock_number(self):
        # Given
        id_at_provider = 'TW92aWU6Mzc4MzI=-12'

        # When
        stock_number = _get_stock_number_from_id_at_providers(id_at_provider)

        # Then
        assert stock_number == 12


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
