class Venue(object):
    def __init__(self,
                 id: int = None,
                 name: str = None,
                 is_virtual: bool = False,
                 siret: str = None):
        self.id = id
        self.name = name
        self.is_virtual = is_virtual
        self.siret = siret
