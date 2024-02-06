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
        {"gtl_id": "01000000", "label": "MUSIQUE_CLASSIQUE"},
        {"gtl_id": "02000000", "label": "JAZZ / BLUES"},
        {"gtl_id": "03000000", "label": "BANDES ORIGINALES"},
        {"gtl_id": "04000000", "label": "ELECTRO"},
        {"gtl_id": "05000000", "label": "POP"},
        {"gtl_id": "06000000", "label": "ROCK"},
        {"gtl_id": "07000000", "label": "METAL"},
        {"gtl_id": "08000000", "label": "ALTERNATIF"},
        {"gtl_id": "09000000", "label": "VARIETES"},
        {"gtl_id": "10000000", "label": "FUNK / SOUL / RNB / DISCO"},
        {"gtl_id": "11000000", "label": "RAP/ HIP HOP"},
        {"gtl_id": "12000000", "label": "REGGAE / RAGGA"},
        {"gtl_id": "13000000", "label": "MUSIQUE DU MONDE"},
        {"gtl_id": "14000000", "label": "COUNTRY / FOLK"},
        {"gtl_id": "15000000", "label": "VIDEOS MUSICALES"},
        {"gtl_id": "16000000", "label": "COMPILATIONS"},
        {"gtl_id": "17000000", "label": "AMBIANCE"},
        {"gtl_id": "18000000", "label": "ENFANTS"},
        {"gtl_id": "19000000", "label": "AUTRES"},
    ]


@pytest.mark.usefixtures("db_session")
def test_get_event_music_types(client):
    # Given
    user = users_factories.UserFactory()
    # When
    response = client.with_session_auth(email=user.email).get("/offers/music-types/event")
    assert response.status_code == 200
    assert response.json == [
        {"gtl_id": "01000000", "label": "MUSIQUE_CLASSIQUE"},
        {"gtl_id": "02000000", "label": "JAZZ / BLUES"},
        {"gtl_id": "04000000", "label": "ELECTRO"},
        {"gtl_id": "05000000", "label": "POP"},
        {"gtl_id": "06000000", "label": "ROCK"},
        {"gtl_id": "07000000", "label": "METAL"},
        {"gtl_id": "08000000", "label": "ALTERNATIF"},
        {"gtl_id": "09000000", "label": "VARIETES"},
        {"gtl_id": "10000000", "label": "FUNK / SOUL / RNB / DISCO"},
        {"gtl_id": "11000000", "label": "RAP/ HIP HOP"},
        {"gtl_id": "12000000", "label": "REGGAE / RAGGA"},
        {"gtl_id": "13000000", "label": "MUSIQUE DU MONDE"},
        {"gtl_id": "14000000", "label": "COUNTRY / FOLK"},
        {"gtl_id": "17000000", "label": "AMBIANCE"},
        {"gtl_id": "19000000", "label": "AUTRES"},
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
