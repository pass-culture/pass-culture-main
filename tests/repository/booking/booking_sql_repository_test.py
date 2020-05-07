from domain.booking.booking import Booking
from domain.stock.stock import Stock
from domain.user.user import User
from models import ThingType
from models.booking_sql_entity import BookingSQLEntity
from repository import repository
from repository.booking import booking_domain_adapter
from repository.booking.booking_sql_repository import BookingSQLRepository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import (create_booking,
                                                   create_offerer, create_user,
                                                   create_venue, create_stock)
from tests.model_creators.specific_creators import (
    create_offer_with_thing_product, create_stock_from_offer)


class BookingSQLRepositoryTest:
    def setup_method(self):
        self.booking_sql_repository = BookingSQLRepository()

    @clean_database
    def test_returns_a_list_of_not_cancelled_bookings(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        book_offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.LIVRE_EDITION)
        book_stock = create_stock_from_offer(book_offer, price=0, quantity=200)
        booking_sql_entity1 = create_booking(user=user, is_cancelled=True, stock=book_stock, venue=venue_online)
        booking_sql_entity2 = create_booking(user=user, is_used=True, stock=book_stock, venue=venue_online)
        booking_sql_entity3 = create_booking(user=user, stock=book_stock, venue=venue_online)
        repository.save(booking_sql_entity1, booking_sql_entity2, booking_sql_entity3)

        booking1 = booking_domain_adapter.to_domain(booking_sql_entity1)

        # when
        bookings = self.booking_sql_repository.find_active_bookings_by_user_id(user.id)

        # then
        assert len(bookings) == 2
        assert booking1 not in bookings

    @clean_database
    def test_should_create_booking_when_booking_does_not_exist(self, app):
        # given
        user_sql_entity = create_user(idx=4)
        offerer = create_offerer()
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        offer = create_offer_with_thing_product(
            venue_online, thing_type=ThingType.LIVRE_EDITION, is_digital=True)
        stock_sql_entity = create_stock(offer=offer, quantity=200, price=0, idx=23)

        user = User(
            identifier=4,
            can_book_free_offers=True
        )
        stock = Stock(
            identifier=23,
            quantity=200,
            offer=offer,
            price=0
        )

        booking_to_save = Booking(user=user, stock=stock, amount=0, quantity=1)
        repository.save(offer, user_sql_entity, stock_sql_entity)

        # when
        self.booking_sql_repository.save(booking_to_save)

        # then
        booking = BookingSQLEntity.query.one()
        booking_saved = booking_domain_adapter.to_domain(booking)
        assert booking_saved.user.identifier == booking_to_save.user.identifier
        assert booking_saved.stock.identifier == booking_to_save.stock.identifier
        assert booking_saved.identifier is not None
