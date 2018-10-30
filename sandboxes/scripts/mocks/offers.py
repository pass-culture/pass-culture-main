""" offers """
from sandboxes.scripts.mocks.utils.generators import get_all_offer_mocks_by_type

offer_mocks = [
    {
        "eventName": "Rencontre avec Franck Lepage",
        "isActive": True,
        "venueName": "LE GRAND REX PARIS"
    },
    {
        "eventName": "Rencontre avec Franck Lepage",
        "isActive": True,
        "venueName": "LE GRAND REX PARIS"
    },
    {
        "eventName": "Concert de Gael Faye",
        "isActive": True,
        "venueName": "THEATRE DE L ODEON"
    },
    {
        "eventName": "PNL chante Marx",
        "isActive": True,
        "venueName": "THEATRE DE L ODEON"
    },
    {
        "thingName": "Ravage",
        "isActive": True,
        "venueName": "THEATRE DE L ODEON"
    }
] + get_all_offer_mocks_by_type()
