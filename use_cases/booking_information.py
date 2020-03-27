class BookingInformation(object):
    def __init__(self, stock_id: int, user_id: int, quantity: int, recommendation_id: int = None):
        self.stock_id = stock_id
        self.user_id = user_id
        self.quantity = quantity
        self.recommendation_id = recommendation_id
