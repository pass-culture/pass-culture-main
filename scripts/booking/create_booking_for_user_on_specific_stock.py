from infrastructure.container import book_an_offer
from use_cases.book_an_offer import BookAnOffer, BookingInformation


def create_booking_for_user_on_specific_stock(user_id: int, stock_id: int,
                                              book_an_offer_impl: BookAnOffer = book_an_offer) -> None:
    booking_information = BookingInformation(
        stock_id=stock_id,
        user_id=user_id,
        quantity=1,
    )

    book_an_offer_impl.execute(booking_information)
