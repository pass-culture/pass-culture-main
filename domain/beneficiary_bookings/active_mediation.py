from datetime import datetime


class ActiveMediation(object):
    def __init__(self,
                 identifier: int,
                 date_created: datetime,
                 offer_id: int
                 ):
        self.identifier = identifier
        self.date_created = date_created
        self.offer_id = offer_id
