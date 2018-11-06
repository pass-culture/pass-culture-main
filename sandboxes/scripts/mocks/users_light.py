""" users light """
from utils.human_ids import humanize


USER_MOCKS = []

ADMIN_USER_MOCK = {
    "canBookFreeOffers": False,
    "departementCode": "93",
    "email": "pctest.admin.1@btmx.fr",
    "firstName": "PC Test",
    "id": humanize(1),
    "isAdmin": True,
    "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
    "lastName": "Admin 1",
    "password": "pctest.Admin.1",
    "postalCode": "93100",
    "publicName": "PC Test Admin 1",
}
USER_MOCKS += [ADMIN_USER_MOCK]

SCRATCH_USER_MOCKS = [
    {
        "departementCode": "93",
        "email": "pctest.jeune.93@btmx.fr",
        "firstName": "PC Test",
        "id": humanize(2),
        "lastName": "Jeune 93",
        "password": "pctest.Jeune.93",
        "postalCode": "93100",
        "publicName": "PC Test Jeune 93",
    },
    {
        "departementCode": "34",
        "email": "pctest.jeune.34@btmx.fr",
        "firstName": "PC Test",
        "id": humanize(3),
        "lastName": "Jeune 34",
        "password": "pctest.Jeune.34",
        "postalCode": "34080",
        "publicName": "PC Test Jeune 34",
    },
    {
        "departementCode": "93",
        "email": "pctest.pro.1@btmx.fr",
        "firstName": "PC Test",
        "id": humanize(4),
        "lastName": "Pro 1",
        "password": "pctest.Pro.1",
        "postalCode": "93100",
        "publicName": "PC Test Pro 1"
    },
    {
        "departementCode": "93",
        "firstName": "PC Test",
        "id": humanize(5),
        "lastName": "Pro 2",
        "email": "pctest.pro.2@btmx.fr",
        "password": "pctest.Pro.2",
        "postalCode": "93100",
        "publicName": "PC Test Pro 2",
    }
]
USER_MOCKS += SCRATCH_USER_MOCKS
