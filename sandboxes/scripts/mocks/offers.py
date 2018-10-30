""" offers """
from sandboxes.scripts.mocks.utils.generators import get_all_offer_mocks_by_type
from uuid import UUID

offer_mocks = [
    {
        "eventName": "Rencontre avec Franck Lepage",
        "isActive": True,
        "key": UUID('d33ee240-dc59-11e8-a29f-0242ac130000'),
        "venueName": "LE GRAND REX PARIS"
    },
    {
        "eventName": "Rencontre avec Franck Lepage",
        "isActive": True,
        "key": UUID('d33ee240-dc59-11e8-a29f-0242ac130001'),
        "venueName": "LE GRAND REX PARIS"
    },
    {
        "eventName": "Concert de Gael Faye",
        "isActive": True,
        "key": UUID('d33ee240-dc59-11e8-a29f-0242ac130002'),
        "venueName": "THEATRE DE L ODEON"
    },
    {
        "eventName": "PNL chante Marx",
        "isActive": True,
        "key": UUID('d33ee240-dc59-11e8-a29f-0242ac130003'),
        "venueName": "THEATRE DE L ODEON"
    },
    {
        "thingName": "Ravage",
        "isActive": True,
        "key": UUID('d33ee240-dc59-11e8-a29f-0242ac130004'),
        "venueName": "THEATRE DE L ODEON"
    }
] + get_all_offer_mocks_by_type()
