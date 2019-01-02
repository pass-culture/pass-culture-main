from models import PaymentTransaction


def find_transaction_checksum(message_id: str) -> str:
    transaction = PaymentTransaction.query.filter_by(messageId=message_id).first()
    return transaction.checksum if transaction else None
