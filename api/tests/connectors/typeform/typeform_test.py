import datetime
from itertools import chain
from unittest import mock

import pytest
import requests_mock

from pcapi import settings
from pcapi.connectors import typeform

from tests.connectors.typeform import fixtures


pytestmark = [
    pytest.mark.settings(TYPEFORM_BACKEND="pcapi.connectors.typeform.TypeformBackend"),
]


class SearchFormTest:
    def test_search_forms(self):
        with requests_mock.Mocker() as mocker:
            mocker.get("https://api.eu.typeform.com/forms?search=concours", json=fixtures.RESPONSE_SEARCH_FORMS)
            forms = typeform.search_forms("concours")

        assert len(forms) == 3

        assert forms[0].form_id == "t4TyOteQ"
        assert forms[0].title == "BOOK CLUB - Jury concours - Fables 2024"

        assert forms[1].form_id == "Y97ETpXP"
        assert forms[1].title == "Concours - Gagne 2 places pour Le Lièvre et la Tortue 🐢"

        assert forms[2].form_id == "T9XBuGwX"
        assert forms[2].title == "Concours - Visite des coulisses La Cigale et la Fourmi"

    def test_search_forms_no_result(self):
        pass


class GetFormTest:
    def test_get_form(self):
        form_id = "aBCdEF12"
        with requests_mock.Mocker() as mocker:
            mocker.get(f"https://api.eu.typeform.com/forms/{form_id}", json=fixtures.RESPONSE_SINGLE_FORM)
            form = typeform.get_form(form_id)

        assert form.form_id == form_id
        assert form.title == "Jeu concours - Maître Corbeau"
        assert form.date_created == datetime.datetime(2024, 9, 2, 12, 51, 25, tzinfo=datetime.timezone.utc)

        fields = form.fields
        assert len(fields) == 7

        assert fields[0].field_id == "fC7aoAXHEfNR"
        assert fields[0].title == "Es-tu *bénéficiaire du pass Culture* ?"

        assert fields[1].field_id == "HXMURW9ecHCn"
        assert fields[1].title == "Es-tu disponible* le dimanche 22 septembre à 20h30* ?"

        assert fields[2].field_id == "ZjcVOgBgk94E"
        assert fields[2].title == "First name"

        assert fields[3].field_id == "dbgPcGvcsy5F"
        assert fields[3].title == "Last name"

        assert fields[4].field_id == "SzSN4dtjlJrO"
        assert fields[4].title == "*Où habites-tu ?*"

        assert fields[5].field_id == "nCUbEqicijfj"
        assert fields[5].title == "*Explique-nous pourquoi tu souhaites être sélectionné.e ! *"

        assert fields[6].field_id == "smRfvBKWjCfF"
        assert (
            fields[6].title
            == "*En participant à ce tirage, je m'engage, si je suis sélectionné.e, à honorer ma participation et à me présenter au jour et à l'horaire qui me seront communiqués.*"
        )

    def test_get_form_with_all_types(self):
        form_id = "AllTypes"
        with requests_mock.Mocker() as mocker:
            mocker.get(f"https://api.eu.typeform.com/forms/{form_id}", json=fixtures.RESPONSE_FORM_WITH_ALL_TYPES)
            form = typeform.get_form(form_id)

        assert form.form_id == form_id
        # Types are not returned here, but this test ensures that any future development will not break any type

    def test_get_form_not_found(self):
        form_id = "AaAaAa"
        with requests_mock.Mocker() as mocker:
            mocker.get(
                f"https://api.eu.typeform.com/forms/{form_id}",
                status_code=404,
                json=fixtures.RESPONSE_FORM_404_NOT_FOUND,
            )
            with pytest.raises(typeform.NotFoundException):
                typeform.get_form(form_id)


class GetResponsesTest:
    def test_get_all_responses(self):
        form_id = "aBCdEF12"
        with requests_mock.Mocker() as mocker:
            mocker.get(f"https://api.eu.typeform.com/forms/{form_id}/responses", json=fixtures.RESPONSE_FORM_RESPONSES)
            responses = typeform.get_responses(form_id)

        # Responses without contact info are ignored (form not completed)
        assert len(responses) == 4

        response = responses[1]
        assert response.response_id == "zxmkrzc9uyxp6jsivn9zxmkrziwwcte2"
        assert response.date_submitted == datetime.datetime(2024, 9, 7, 16, 39, 53, tzinfo=datetime.timezone.utc)
        assert response.phone_number == "+33700000002"
        assert response.email == "second@example.com"
        assert len(response.answers) == 7
        assert response.answers[0].field_id == "fC7aoAXHEfNR"
        assert response.answers[0].text == "Oui"
        assert response.answers[1].field_id == "HXMURW9ecHCn"
        assert response.answers[1].text == "Oui"
        assert response.answers[2].field_id == "ZjcVOgBgk94E"
        assert response.answers[2].text == "Deuxième"
        assert response.answers[3].field_id == "dbgPcGvcsy5F"
        assert response.answers[3].text == "Second"
        assert response.answers[4].field_id == "SzSN4dtjlJrO"
        assert response.answers[4].text == "14130 Pont-l'Évêque"
        assert response.answers[5].field_id == "nCUbEqicijfj"
        assert response.answers[5].text == "Il est le Phénix des hôtes de ces bois."
        assert response.answers[6].field_id == "smRfvBKWjCfF"
        assert (
            response.answers[6].text
            == "J'ai lu et compris  les conditions. Je confirme ma participation au tirage au sort."
        )

        response = responses[3]
        assert response.response_id == "hsm1mxckfhbqtk50l9ahsm1mxa4ivy8o"
        assert response.date_submitted == datetime.datetime(2024, 9, 10, 11, 19, 42, tzinfo=datetime.timezone.utc)
        assert response.phone_number == "+33600000004"
        assert response.email == "fourth@example.com"
        assert len(response.answers) == 7
        assert response.answers[0].field_id == "fC7aoAXHEfNR"
        assert response.answers[0].text == "Oui"
        assert response.answers[1].field_id == "HXMURW9ecHCn"
        assert response.answers[1].text == "Oui"
        assert response.answers[2].field_id == "ZjcVOgBgk94E"
        assert response.answers[2].text == "Quatrième"
        assert response.answers[3].field_id == "dbgPcGvcsy5F"
        assert response.answers[3].text == "Fourth"
        assert response.answers[4].field_id == "SzSN4dtjlJrO"
        assert response.answers[4].text == "Beaufort 73270"
        assert response.answers[5].field_id == "nCUbEqicijfj"
        assert response.answers[5].text == "Tout flatteur vit aux dépens de celui qui l'écoute."
        assert response.answers[6].field_id == "smRfvBKWjCfF"
        assert (
            response.answers[6].text
            == "J'ai lu et compris  les conditions. Je confirme ma participation au tirage au sort."
        )

    def test_get_response_with_many_types(self):
        form_id = "AllTypes"
        with requests_mock.Mocker() as mocker:
            mocker.get(
                f"https://api.eu.typeform.com/forms/{form_id}/responses",
                json=fixtures.RESPONSE_FORM_RESPONSE_WITH_ALL_TYPES,
            )
            responses = typeform.get_responses(form_id)

        assert len(responses) == 1
        response = responses[0]

        assert response.phone_number == "+33123456789"
        assert response.email == "user@example.com"
        assert len(response.answers) == 15
        assert response.answers[0].text == "pass"
        assert response.answers[1].text == "pass Culture"
        assert response.answers[2].text == "choice 1"
        assert response.answers[3].text == "8"
        assert response.answers[4].text == "7"
        assert response.answers[5].text == "9"
        assert response.answers[6].text == "15/01/2025"
        assert response.answers[7].text == "Second choice"
        assert response.answers[8].text == "123"
        assert (
            response.answers[9].text
            == "https://api.eu.typeform.com/forms/AllTypes/responses/nj0g9wtuhxhkqdw11qnj0g9wnf3edhxu/fields/piy78v4evI30/files/file.jpg"
        )
        assert response.answers[10].text == "https://example.com"
        assert response.answers[11].text == "Oui"
        assert response.answers[12].text == "Oui"
        assert response.answers[13].text == "First choice"
        assert (
            response.answers[14].text
            == """choice D
choice C
choice B"""
        )

    def test_get_choices_response_without_labels(self):
        form_id = "AllTypes"
        with requests_mock.Mocker() as mocker:
            mocker.get(
                f"https://api.eu.typeform.com/forms/{form_id}/responses",
                json=fixtures.RESPONSE_FORM_RESPONSE_WITHOUT_LABELS,
            )
            responses = typeform.get_responses(form_id)

        assert len(responses) == 1
        response = responses[0]

        assert len(response.answers) == 1
        assert response.answers[0].text is None

    def test_get_responses_not_found(self):
        form_id = "AaAaAa"
        with requests_mock.Mocker() as mocker:
            mocker.get(
                f"https://api.eu.typeform.com/forms/{form_id}/responses",
                status_code=404,
                json=fixtures.RESPONSE_FORM_RESPONSES_404_NOT_FOUND,
            )
            with pytest.raises(typeform.NotFoundException):
                typeform.get_responses(form_id)


class GetResponsesGeneratorTest:
    def test_empty_answer(self):
        form_id = "123aze"
        with mock.patch("pcapi.connectors.typeform.get_responses", return_value=[]) as get_responses:
            for _ in typeform.get_responses_generator(lambda: None, form_id):
                assert False
            get_responses.assert_called_once_with(
                form_id=form_id,
                num_results=settings.TYPEFORM_IMPORT_CHUNK_SIZE,
                since=None,
                sort="submitted_at,asc",
            )

    @pytest.mark.settings(TYPEFORM_IMPORT_CHUNK_SIZE=5)
    def test_multiple_call(self):
        form_id = "123aze"
        times = [None, datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)]
        time_function = mock.MagicMock(side_effect=times)
        list_expected = [list(range(5)), list(range(10, 15)), [1, 2, 3]]
        cycles = 0

        with mock.patch("pcapi.connectors.typeform.get_responses", side_effect=list_expected) as get_responses:
            for r, e in zip(typeform.get_responses_generator(time_function, form_id), chain(*list_expected)):
                if cycles % 5 == 0:
                    get_responses.assert_called_with(
                        form_id=form_id,
                        num_results=settings.TYPEFORM_IMPORT_CHUNK_SIZE,
                        since=times[cycles // 5],
                        sort="submitted_at,asc",
                    )
                cycles += 1
                assert r == e

            assert get_responses.call_count == len(times)
            assert cycles == len(list(chain(*list_expected)))

    @pytest.mark.settings(TYPEFORM_IMPORT_CHUNK_SIZE=5)
    def test_inifinite_loop(self):
        form_id = "123aze"
        with mock.patch("pcapi.connectors.typeform.get_responses", return_value=list(range(5))) as get_responses:
            for r, e in zip(typeform.get_responses_generator(lambda: None, form_id), range(5)):
                assert r == e

            get_responses.assert_called_once_with(
                form_id=form_id,
                num_results=settings.TYPEFORM_IMPORT_CHUNK_SIZE,
                since=None,
                sort="submitted_at,asc",
            )
