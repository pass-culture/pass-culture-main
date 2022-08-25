import copy
from datetime import datetime

import pytest

from pcapi.core.offerers.models import Venue
from pcapi.local_providers.allocine.allocine_stocks import _build_movie_uuid
from pcapi.local_providers.allocine.allocine_stocks import _filter_only_digital_and_non_experience_showtimes
from pcapi.local_providers.allocine.allocine_stocks import _find_showtime_by_showtime_uuid
from pcapi.local_providers.allocine.allocine_stocks import _format_poster_url
from pcapi.local_providers.allocine.allocine_stocks import _get_showtimes_uuid_by_idAtProvider
from pcapi.local_providers.allocine.allocine_stocks import _parse_movie_duration
from pcapi.local_providers.allocine.allocine_stocks import retrieve_movie_information
from pcapi.local_providers.allocine.allocine_stocks import retrieve_showtime_information


MOVIE_INFO = {
    "node": {
        "movie": {
            "id": "TW92aWU6MjY4Njgw",
            "internalId": 268680,
            "backlink": {
                "url": "http://www.allocine.fr/film/fichefilm_gen_cfilm=268680.html",
                "label": "Tous les détails du film sur AlloCiné",
            },
            "data": {"eidr": None, "productionYear": 2021},
            "title": "Tom et Jerry",
            "originalTitle": "Tom & Jerry",
            "type": "FEATURE_FILM",
            "runtime": "PT1H41M0S",
            "poster": {"url": "https://fr.web.img2.acsta.net/pictures/20/12/28/10/09/5991258.jpg"},
            "synopsis": "Lorsque Jerry s'installe dans le plus bel hôtel de New York la veille du mariage"
            " du siècle, Kayla, la wedding planneuse, n'a d'autre choix que d'embaucher Tom"
            " pour se débarrasser de l'intrus.",
            "releases": [
                {
                    "name": "Released",
                    "releaseDate": {"date": "2021-05-19"},
                    "data": {
                        "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [318469]"},
                        "visa_number": "154510",
                    },
                }
            ],
            "credits": {
                "edges": [
                    {
                        "node": {
                            "person": {"firstName": "Tim", "lastName": "Story"},
                            "position": {"name": "DIRECTOR"},
                        }
                    }
                ]
            },
            "cast": {
                "backlink": {
                    "url": "http://www.allocine.fr/film/fichefilm-268680/casting/",
                    "label": "Casting complet du film sur AlloCiné",
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
            "countries": [{"name": "USA", "alpha3": "USA"}],
            "genres": ["ANIMATION", "COMEDY", "FAMILY"],
            "companies": [
                {
                    "activity": "Distribution",
                    "company": {"name": "Warner Bros. France"},
                },
                {"activity": "Production", "company": {"name": "The Story Company"}},
            ],
        },
        "showtimes": [
            {
                "startsAt": "2021-07-09T17:00:00",
                "diffusionVersion": "DUBBED",
                "projection": ["DIGITAL"],
                "experience": None,
            },
            {
                "startsAt": "2021-07-10T17:00:00",
                "diffusionVersion": "DUBBED",
                "projection": ["DIGITAL"],
                "experience": None,
            },
            {
                "startsAt": "2021-07-11T18:00:00",
                "diffusionVersion": "DUBBED",
                "projection": ["DIGITAL"],
                "experience": None,
            },
            {
                "startsAt": "2021-07-12T17:00:00",
                "diffusionVersion": "DUBBED",
                "projection": ["DIGITAL"],
                "experience": None,
            },
        ],
    }
}


class ParseMovieDurationTest:
    def test_should_convert_duration_string_to_minutes(self):
        # Given
        movie_runtime = "PT1H50M15S"

        # When
        duration_in_minutes = _parse_movie_duration(movie_runtime)

        # Then
        assert duration_in_minutes == 110

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
        movie_information = MOVIE_INFO

        # When
        movie_parsed_information = retrieve_movie_information(movie_information["node"]["movie"])

        # Then
        assert movie_parsed_information == {
            "id": "TW92aWU6MjY4Njgw",
            "title": "Tom et Jerry",
            "internal_id": 268680,
            "genres": ["ANIMATION", "COMEDY", "FAMILY"],
            "type": "FEATURE_FILM",
            "cast": ["Chloë Grace Moretz", "Michael Peña"],
            "companies": [
                {"activity": "Distribution", "company": {"name": "Warner Bros. France"}},
                {"activity": "Production", "company": {"name": "The Story Company"}},
            ],
            "description": "Lorsque Jerry s'installe dans le plus bel hôtel de New York la veille du mariage du siècle, Kayla, la wedding planneuse, n'a d'autre choix que d'embaucher Tom pour se débarrasser de l'intrus.\nTous les détails du film sur AlloCiné: http://www.allocine.fr/film/fichefilm_gen_cfilm=268680.html",
            "duration": 101,
            "poster_url": "https://fr.web.img2.acsta.net/pictures/20/12/28/10/09/5991258.jpg",
            "stageDirector": "Tim Story",
            "visa": "154510",
            "releaseDate": "2021-05-19",
            "countries": ["USA"],
        }

    def test_should_not_add_operating_visa_and_stage_director_keys_when_nodes_are_missing(self):
        # Given
        movie_information = copy.deepcopy(MOVIE_INFO)
        del movie_information["node"]["movie"]["releases"][0]["data"]["visa_number"]
        movie_information["node"]["movie"]["credits"]["edges"] = []

        # When
        movie_parsed_information = retrieve_movie_information(movie_information["node"]["movie"])

        # Then
        assert "visa" not in movie_parsed_information
        assert "stageDirector" not in movie_parsed_information

    def test_should_raise_key_error_exception_when_missing_required_keys_in_movie_information(self):
        # Given
        movie_information = copy.deepcopy(MOVIE_INFO)
        del movie_information["node"]["movie"]["title"]

        # When
        with pytest.raises(KeyError):
            retrieve_movie_information(movie_information["node"]["movie"])

    def test_should_return_empty_value_when_missing_poster_information(self):
        # Given
        movie_information = copy.deepcopy(MOVIE_INFO)
        del movie_information["node"]["movie"]["poster"]["url"]

        # When
        movie_parsed_information = retrieve_movie_information(movie_information["node"]["movie"])

        # Then
        assert "poster_url" not in movie_parsed_information

    def test_should_create_product_and_new_offer_with_none_person_in_credits(self):
        # Given
        movie_information = copy.deepcopy(MOVIE_INFO)
        movie_information["node"]["movie"]["credits"]["edges"][0]["node"]["person"] = None

        # When
        movie_parsed_information = retrieve_movie_information(movie_information["node"]["movie"])

        # Then
        assert "stageDirector" not in movie_parsed_information


class RetrieveShowtimeInformationTest:
    def test_should_retrieve_showtime_information_from_allocine_json_response(self):
        # Given
        movie_showtime = {
            "startsAt": "2019-12-03T20:00:00",
            "diffusionVersion": "LOCAL",
            "projection": ["NON DIGITAL"],
            "experience": None,
        }

        # When
        parsed_movie_showtime = retrieve_showtime_information(movie_showtime)

        # Then
        assert parsed_movie_showtime == {
            "startsAt": datetime(2019, 12, 3, 20, 0),
            "diffusionVersion": "LOCAL",
            "projection": "NON DIGITAL",
            "experience": None,
        }

    def test_should_raise_key_error_exception_when_missing_keys_in_showtime_information(self):
        # Given
        movie_showtime = {"startsAt": "2019-12-03T20:00:00", "diffusionVersion": "LOCAL", "experience": None}

        # When
        with pytest.raises(KeyError):
            retrieve_showtime_information(movie_showtime)


class FormatPosterUrlTest:
    def test_should_return_url_in_correct_format(self):
        # Given
        url = r"https:\/\/fr.web.img4.acsta.net\/pictures\/19\/07\/23\/15\/55\/2940058.jpg"

        # When
        formatted_url = _format_poster_url(url)

        # Then
        assert formatted_url == "https://fr.web.img4.acsta.net/pictures/19/07/23/15/55/2940058.jpg"


class FilterOnlyDigitalAndNonExperiencedShowtimesTest:
    def test_should_filter_only_digital_and_non_experience_showtimes(self):
        # Given
        movie_information = [
            {
                "startsAt": "2019-12-03T10:00:00",
                "diffusionVersion": "LOCAL",
                "projection": ["DIGITAL"],
                "experience": None,
            },
            {
                "startsAt": "2019-12-03T18:00:00",
                "diffusionVersion": "ORIGINAL",
                "projection": ["NON DIGITAL"],
                "experience": "experience",
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
        ]

        # When
        filtered_movie_showtimes = _filter_only_digital_and_non_experience_showtimes(movie_information)

        # Then
        assert filtered_movie_showtimes == [
            {
                "startsAt": "2019-12-03T10:00:00",
                "diffusionVersion": "LOCAL",
                "projection": ["DIGITAL"],
                "experience": None,
            }
        ]


class GetShowtimeUUIDFromIdAtProviderTest:
    def test_should_return_the_right_uuid(self):
        # When
        showtime_uuid = _get_showtimes_uuid_by_idAtProvider("TW92aWU6Mzc4MzI=%77567146400110#LOCAL/2019-12-04T18:00:00")

        # Then
        assert showtime_uuid == "LOCAL/2019-12-04T18:00:00"


class FindShowtimesByShowtimeUUIDTest:
    def test_should_return_showtime_matching_the_given_beginning_datetime(self):
        # Given
        showtimes = [
            {
                "diffusionVersion": "LOCAL",
                "experience": None,
                "projection": ["DIGITAL"],
                "startsAt": "2019-12-03T10:00:00",
            },
            {
                "diffusionVersion": "LOCAL",
                "experience": None,
                "projection": ["DIGITAL"],
                "startsAt": "2019-12-04T18:00:00",
            },
        ]

        # When
        showtime = _find_showtime_by_showtime_uuid(showtimes, "LOCAL/2019-12-04T18:00:00")

        # Then
        assert showtime == {
            "diffusionVersion": "LOCAL",
            "experience": None,
            "projection": ["DIGITAL"],
            "startsAt": "2019-12-04T18:00:00",
        }

    def test_should_return_none_when_no_showtimes_found(self):
        # Given
        showtimes = [
            {
                "diffusionVersion": "LOCAL",
                "experience": None,
                "projection": ["DIGITAL"],
                "startsAt": "2019-12-04T18:00:00",
            },
            {
                "diffusionVersion": "LOCAL",
                "experience": None,
                "projection": ["DIGITAL"],
                "startsAt": "2019-12-04T18:00:00",
            },
        ]

        # When
        showtime = _find_showtime_by_showtime_uuid(showtimes, "DUBBED/2019-12-04T18:00:00")

        # Then
        assert showtime is None


class BuildMovieUuidTest:
    def test_should_construct_uuid_with_siret(self):
        # Given
        venue = Venue(name="Cinéma Allociné", siret="77567146400110")

        # When
        movie_uuid = _build_movie_uuid(movie_information=MOVIE_INFO["node"]["movie"], venue=venue)

        # Then
        assert movie_uuid == "TW92aWU6MjY4Njgw%77567146400110"

    def test_should_construct_uuid_with_venue_id_when_siret_is_none(self):
        # Given
        venue = Venue(name="Cinéma Allociné", id=333, siret=None)

        # When
        movie_uuid = _build_movie_uuid(movie_information=MOVIE_INFO["node"]["movie"], venue=venue)

        # Then
        assert movie_uuid == "TW92aWU6MjY4Njgw%333"

    def test_should_construct_uuid_with_venue_id_when_siret_is_empty(self):
        # Given
        venue = Venue(name="Cinéma Allociné", id=333, siret="")

        # When
        movie_uuid = _build_movie_uuid(movie_information=MOVIE_INFO["node"]["movie"], venue=venue)

        # Then
        assert movie_uuid == "TW92aWU6MjY4Njgw%333"
