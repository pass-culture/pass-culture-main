""" venue """

ninety_three_venue = {
    "address": "35 RUE DE PARIS",
    "bookingEmail": "fake@email.com",
    "city": "Bobigny",
    "departementCode": "93",
    "latitude": 48.89639,
    "longitude": 2.429692,
    "name": "NINETY THREE VENUE",
    "offererName": "NINETY THREE VENUE",
    "postalCode": "93000",
}

virtual_ninety_three_venue = {
    "isVirtual": True,
    "name": "Offre en ligne",
    "offererName": "NINETY THREE VENUE"
}

venue_mocks = [
    ninety_three_venue,
    virtual_ninety_three_venue,
    {
        "address": "1 BD POISSONNIERE",
        "bookingEmail": "fake@email.com",
        "city": "Paris",
        "departementCode": "75",
        "latitude": 48.870665,
        "longitude": 2.3478,
        "name": "LE GRAND REX PARIS",
        "offererName": "LE GRAND REX PARIS",
        "postalCode": "75002",
        "siret": "50763357600016"
    },
    {
        "isVirtual": True,
        "name": "Offre en ligne",
        "offererName": "LE GRAND REX PARIS"
    },
    {
        "address": "6 rue Grolee",
        "bookingEmail": "fake2@email.com",
        "city": "Lyon",
        "departementCode": "69",
        "latitude": 45.762606,
        "longitude": 4.836694,
        "name": "THEATRE DE L ODEON",
        "offererName": "THEATRE DE L ODEON",
        "postalCode": "69002",
        "siret": "75050570300025"
    },
    {
        "isVirtual": True,
        "name": "Offre en ligne",
        "offererName": "THEATRE DE L ODEON"
    },
    {
        "isVirtual": True,
        "name": "Offre en ligne",
        "offererName": "THEATRE DU SOLEIL"
    }
]
