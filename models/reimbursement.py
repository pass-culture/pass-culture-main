class Reimbursement:
    CSV_HEADER = [
        'ID de l\'utilisateur',
        'Solde théorique',
        'Solde réel'
    ]

    def as_csv_row(self):
        return [
            self.booking_user_email,
            self.offerer_name,
            self.offerer_siren,
            self.venue_name,
            self.venue_siret,
            self.offer_name,
            self.offer_type,
            str(self.booking_date),
            str(self.booking_amount),
            str(self.booking_used_date),
            self.payment_iban,
            self.transaction_message_id,
            str(self.transaction_end_to_end_id),
            str(self.reimbursement_rate),
            str(self.reimbursed_amount)
        ]
