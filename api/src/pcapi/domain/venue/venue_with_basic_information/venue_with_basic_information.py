class VenueWithBasicInformation:
    def __init__(self, identifier: int, name: str, siret: str, publicName: str, bookingEmail: str | None):
        self.identifier = identifier
        self.name = name
        self.siret = siret
        self.publicName = publicName
        self.bookingEmail = bookingEmail
