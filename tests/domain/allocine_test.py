from unittest.mock import Mock

from domain.allocine import get_movie_showtime_list_from_allocine


class GetMovieShowtimeListFromAllocineTest:
    def setup_method(self):
        self.theater_id = '123456789'
        self.token = 'AZERTY123/@.,!é'
        self.mock_get_movie_showtime_list = Mock()

    def test_should_retrieve_result_from_api_connector_with_token_and_theater_id_parameter(self):
        # Given
        movies_list = [
            {"node": {
                "movie": {
                    "id": "TW92aWU6Mzc4MzI=",
                    "internalId": 37832,
                    "title": "Les Contes de la m\u00e8re poule"}}}
        ]
        self.mock_get_movie_showtime_list.return_value = {
            "movieShowtimeList": {
                "totalCount": 5,
                "edges": movies_list}}

        # When
        get_movie_showtime_list_from_allocine(self.token, self.theater_id,
                                              get_movie_showtime_list_api=self.mock_get_movie_showtime_list)
        # Then
        self.mock_get_movie_showtime_list.assert_called_once_with(self.token, self.theater_id)

    def test_should_extract_movies_from_api_result(self):
        # Given
        movies_list = [
            {"node": {
                "movie": {
                    "id": "TW92aWU6Mzc4MzI=",
                    "internalId": 37832,
                    "title": "Les Contes de la m\u00e8re poule"}}},
            {"node": {
                "movie": {
                    "id": "TW92aWU6NTA0MDk=",
                    "internalId": 50609,
                    "title": "Le Ch\u00e2teau ambulant"}}}

        ]
        self.mock_get_movie_showtime_list.return_value = {
            "movieShowtimeList": {
                "totalCount": 5,
                "edges": movies_list}}

        # When
        expected_result = get_movie_showtime_list_from_allocine(self.token, self.theater_id,
                                                                get_movie_showtime_list_api=self.mock_get_movie_showtime_list)
        # Then
        self.mock_get_movie_showtime_list.assert_called_once_with(self.token, self.theater_id)
        assert expected_result == movies_list
