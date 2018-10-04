""" users webapp """
from mock.scripts.chunks.users_light import user_mocks as light_user_mocks

user_mocks = light_user_mocks + [
    {
        "publicName": "Utilisateur test jeune",
        "firstName": "Utilisateur",
        "lastName": "Test Jeune",
        "email": "pctest.jeune.93@btmx.fr",
        "postalCode": "93100",
        "departementCode": "93",
        "password": "pctestjeune"
    },
]
