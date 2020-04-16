class User(object):
    def __init__(self,
                 identifier: int,
                 can_book_free_offers: bool
                 ):
        self.identifier = identifier
        self.can_book_free_offers = can_book_free_offers
