from decimal import Decimal


class WalletBalance:
    CSV_HEADER = ["ID de l'utilisateur", "Solde théorique", "Solde réel"]

    def __init__(self, user_id: int, current_wallet_balance: Decimal, real_wallet_balance: Decimal):
        self.user_id = user_id
        self.current_balance = current_wallet_balance
        self.real_balance = real_wallet_balance

    def as_csv_row(self):
        return [self.user_id, self.current_balance, self.real_balance]
