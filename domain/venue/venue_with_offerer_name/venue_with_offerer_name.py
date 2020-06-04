class VenueWithOffererName(object):
    def __init__(self,
                 identifier: int,
                 is_virtual: bool,
                 name: str,
                 offerer_name: str):
        self.identifier = identifier
        self.is_virtual = is_virtual
        self.name = name
        self.offerer_name = offerer_name
