from domain.booking import ClientError


class StockDoesntExist(ClientError):
    def __init__(self):
        super().__init__('stockId', 'stockId ne correspond à aucun stock')
