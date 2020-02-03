from repository import booking_queries, repository


def manage_titelive_school_related_bookings_and_offers(file_path: str):
    print("[BOOKINGS TOKEN SCAN] START")
    bookings_token = _read_token_from_file(file_path)
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


def _read_token_from_file(file_path: str) -> [str]:
    with open(file_path, mode='r', newline='\n') as file:
        bookings_token = file.read().splitlines()
    return bookings_token
