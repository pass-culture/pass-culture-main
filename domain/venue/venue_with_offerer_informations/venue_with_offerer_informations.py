class VenueWithOffererInformations(object):
    def __init__(self,
                 id: int,
                 is_virtual: bool,
                 name: str,
                 offerer_name: str):
        self.id = id
        self.is_virtual = is_virtual
        self.name = name
        self.offerer_name = offerer_name
