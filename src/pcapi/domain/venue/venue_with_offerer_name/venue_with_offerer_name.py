class VenueWithOffererName:
    def __init__(
        self,
        identifier: int,
        is_virtual: bool,
        managing_offerer_identifier: int,
        name: str,
        offerer_name: str,
        public_name: str = None,
        booking_email: str = None,
    ):
        self.identifier = identifier
        self.is_virtual = is_virtual
        self.managing_offerer_identifier = managing_offerer_identifier
        self.name = name
        self.offerer_name = offerer_name
        self.public_name = public_name
        self.booking_email = booking_email
