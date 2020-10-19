class OffersStatusFilters(object):
    def __init__(self, exclude_active: bool = False, exclude_inactive: bool = False):
        self.exclude_active = exclude_active
        self.exclude_inactive = exclude_inactive
