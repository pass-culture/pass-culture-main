from repository import booking_queries, repository


def update_offer_and_booking_status(booking_tokens_file_path: str):
    print("[BOOKINGS TOKEN SCAN] START")
    bookings_token = _read_booking_tokens_from_file(booking_tokens_file_path)
    print(f"[BOOKINGS TOKEN SCAN] Getting {len(bookings_token)} bookings token to check")
    progress = 0

    for booking_token in bookings_token:
        booking = booking_queries.find_by(booking_token)

        if not booking.isUsed:
            booking.isCancelled = True
            print(f"[BOOKINGS TOKEN SCAN] Cancelling booking: {booking_token}")

        offer = booking.stock.resolvedOffer
        offer.isActive = False
        repository.save(offer, booking)

        progress += 1
        step = progress / len(bookings_token) * 100
        if (progress % 1000) == 0:
            print(f"[ISBN SCAN] Progress: {str(step)}")
    print("[BOOKINGS TOKEN SCAN] END")


def _read_booking_tokens_from_file(file_path: str) -> [str]:
    with open(file_path, mode='r', newline='\n') as file:
        return file.read().splitlines()
