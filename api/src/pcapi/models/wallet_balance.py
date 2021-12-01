class WalletBalance:
    CSV_HEADER = ["ID de l'utilisateur", "Solde théorique", "Solde réel"]

    @classmethod
    def as_csv_row(cls, row):
        return [row.user_id, row.current_balance, row.real_balance]
