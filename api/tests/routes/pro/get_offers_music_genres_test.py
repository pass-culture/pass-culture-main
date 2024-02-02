import pytest

import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_get_all_music_types(client):
    # Given
    user = users_factories.UserFactory()
    # When
    response = client.with_session_auth(email=user.email).get("/offers/music-types/all")
    assert response.status_code == 200
    assert response.json == [
        {"gtlId": "01000000", "label": "MUSIQUE_CLASSIQUE"},
        {"gtlId": "02000000", "label": "JAZZ / BLUES"},
        {"gtlId": "03000000", "label": "BANDES ORIGINALES"},
        {"gtlId": "04000000", "label": "ELECTRO"},
        {"gtlId": "05000000", "label": "POP"},
        {"gtlId": "06000000", "label": "ROCK"},
        {"gtlId": "07000000", "label": "METAL"},
        {"gtlId": "08000000", "label": "ALTERNATIF"},
        {"gtlId": "09000000", "label": "VARIETES"},
        {"gtlId": "10000000", "label": "FUNK / SOUL / RNB / DISCO"},
        {"gtlId": "11000000", "label": "RAP/ HIP HOP"},
        {"gtlId": "12000000", "label": "REGGAE / RAGGA"},
        {"gtlId": "13000000", "label": "MUSIQUE DU MONDE"},
        {"gtlId": "14000000", "label": "COUNTRY / FOLK"},
        {"gtlId": "15000000", "label": "VIDEOS MUSICALES"},
        {"gtlId": "16000000", "label": "COMPILATIONS"},
        {"gtlId": "17000000", "label": "AMBIANCE"},
        {"gtlId": "18000000", "label": "ENFANTS"},
        {"gtlId": "19000000", "label": "AUTRES"},
    ]


@pytest.mark.usefixtures("db_session")
def test_get_event_music_types(client):
    # Given
    user = users_factories.UserFactory()
    # When
    response = client.with_session_auth(email=user.email).get("/offers/music-types/event")
    assert response.status_code == 200
    assert response.json == [
        {"gtlId": "01000000", "label": "MUSIQUE_CLASSIQUE"},
        {"gtlId": "02000000", "label": "JAZZ / BLUES"},
        {"gtlId": "04000000", "label": "ELECTRO"},
        {"gtlId": "05000000", "label": "POP"},
        {"gtlId": "06000000", "label": "ROCK"},
        {"gtlId": "07000000", "label": "METAL"},
        {"gtlId": "08000000", "label": "ALTERNATIF"},
        {"gtlId": "09000000", "label": "VARIETES"},
        {"gtlId": "10000000", "label": "FUNK / SOUL / RNB / DISCO"},
        {"gtlId": "11000000", "label": "RAP/ HIP HOP"},
        {"gtlId": "12000000", "label": "REGGAE / RAGGA"},
        {"gtlId": "13000000", "label": "MUSIQUE DU MONDE"},
        {"gtlId": "14000000", "label": "COUNTRY / FOLK"},
        {"gtlId": "17000000", "label": "AMBIANCE"},
        {"gtlId": "19000000", "label": "AUTRES"},
    ]


@pytest.mark.usefixtures("db_session")
def test_get_all_music_types_unauthentified_user(client):
    response = client.get("/offers/music-types/all")
    assert response.status_code == 401
    assert response.json == {"global": ["Authentification nécessaire"]}


@pytest.mark.usefixtures("db_session")
def test_get_event_music_types_unauthentified_user(client):
    response = client.get("/offers/music-types/event")
    assert response.status_code == 401
    assert response.json == {"global": ["Authentification nécessaire"]}
