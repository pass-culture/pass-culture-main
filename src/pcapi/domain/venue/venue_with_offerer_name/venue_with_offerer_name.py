class VenueWithOffererName(object):
    def __init__(self,
                 identifier: int,
                 is_virtual: bool,
                 name: str,
                 offerer_name: str,
                 public_name: str = None):
        self.identifier = identifier
        self.is_virtual = is_virtual
        self.name = name
        self.offerer_name = offerer_name
        self.public_name = public_name
