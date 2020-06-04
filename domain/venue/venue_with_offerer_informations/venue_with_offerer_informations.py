class VenueWithOffererInformations(object):
    def __init__(self,
                 id: int,
                 is_virtual: bool,
                 name: str,
                 siret: str):
        self.id = id
        self.is_virtual = is_virtual
        self.name = name
        self.siret = siret
