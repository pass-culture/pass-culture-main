from decimal import Decimal

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import Expense
from pcapi.core.users.models import ExpenseDomain
from pcapi.models import EventType
from pcapi.models import ThingType


@pytest.mark.usefixtures("db_session")
class ExpensesTest:
    class DomainBookingTemporaryTest:
        def test_should_return_expenses(self):
            booking = BookingFactory(
                amount=50,
                stock__offer__type=str(ThingType.LIVRE_EDITION),
                stock__offer__url="url",
            )
            user = booking.user

            # when
            expenses = user.expenses

            # then
            assert expenses == [
                Expense(domain=ExpenseDomain.ALL, current=Decimal(50), limit=Decimal(500)),
                Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(50), limit=Decimal(200)),
                Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0), limit=Decimal(200)),
            ]

    class ThingsTest:
        class AudiovisuelTest:
            def test_online_offer_increase_digital_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.AUDIOVISUEL),
                    stock__offer__url="http://on.line",
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(50.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

            def test_offline_offer_increase_physical_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.AUDIOVISUEL),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(50.0), limit=Decimal(200)),
                ]

        class JeuxVideoTest:
            def test_online_offer_increase_digital_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.JEUX_VIDEO),
                    stock__offer__url="http://on.line",
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(50.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class MusiqueTest:
            def test_online_offer_increase_digital_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.MUSIQUE),
                    stock__offer__url="http://on.line",
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(50.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

            def test_offline_offer_increase_physical_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.MUSIQUE),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(50.0), limit=Decimal(200)),
                ]

        class OeuvreArtTest:
            def test_offline_offer_increase_physical_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.OEUVRE_ART),
                )

                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(50.0), limit=Decimal(200)),
                ]

        class PresseAboTest:
            def test_online_offer_increase_digital_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.PRESSE_ABO),
                    stock__offer__url="http://on.line",
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(50.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class LivreEditionTest:
            def test_online_offer_increase_digital_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.LIVRE_EDITION),
                    stock__offer__url="http://on.line",
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(50.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

            def test_offline_offer_increase_physical_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.LIVRE_EDITION),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(50.0), limit=Decimal(200)),
                ]

        class JeuxTest:
            def test_offline_offer_increase_physical_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.JEUX),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(50.0), limit=Decimal(200)),
                ]

        class PratiqueArtistiqueAboTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=100,
                    stock__offer__type=str(ThingType.PRATIQUE_ARTISTIQUE_ABO),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(100.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class MusiqueAboTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.MUSIQUE_ABO),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class MuseesPatrimoineAboTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.MUSEES_PATRIMOINE_ABO),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class CinemaAboTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.CINEMA_ABO),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class CinemaCardTest:
            def test_online_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.CINEMA_CARD),
                    stock__offer__url="http://on.line",
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class InstrumentTest:
            def test_offline_offer_increase_physical_expense(self):
                # Given
                booking = BookingFactory(
                    amount=60,
                    stock__offer__type=str(ThingType.INSTRUMENT),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(60.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(60.0), limit=Decimal(200)),
                ]

        class JeuxVideoAboTest:
            def test_online_offer_is_capped(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.JEUX_VIDEO_ABO),
                    stock__offer__url="http://on.line",
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(50.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class SpectacleVivantAboTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.SPECTACLE_VIVANT_ABO),
                    stock__offer__url=None,
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class LivreAudioTest:
            def test_online_offer_increase_digital_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(ThingType.LIVRE_AUDIO),
                    stock__offer__url="http://on.line",
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(50.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

    class EventsTest:
        class CinemaTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(EventType.CINEMA),
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class ConferenceDebatDedicaceTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(EventType.CONFERENCE_DEBAT_DEDICACE),
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class JeuxTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(EventType.JEUX),
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class MusiqueTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(EventType.MUSIQUE),
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class MuseesPatrimoineTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(EventType.MUSEES_PATRIMOINE),
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class PratiqueArtistiqueTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(EventType.PRATIQUE_ARTISTIQUE),
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

        class SpectacleVivantTest:
            def test_offline_offer_increase_total_expense(self):
                # Given
                booking = BookingFactory(
                    amount=50,
                    stock__offer__type=str(EventType.SPECTACLE_VIVANT),
                )
                user = booking.user

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(50.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]

    class ComputationTest:
        class MaxTest:
            def test_returns_max_500_and_actual_210(self):
                # Given
                beneficiary = UserFactory()
                BookingFactory(
                    user=beneficiary,
                    amount=90,
                )
                BookingFactory(user=beneficiary, amount=60, quantity=2)
                BookingFactory(user=beneficiary, amount=20, isCancelled=True)

                # when
                expenses = beneficiary.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(210.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(210.0), limit=Decimal(200)),
                ]

            def test_returns_max_500_and_actual_0(self):
                # Given
                user = UserFactory()

                # when
                expenses = user.expenses

                # Then
                assert expenses == [
                    Expense(domain=ExpenseDomain.ALL, current=Decimal(0.0), limit=Decimal(500)),
                    Expense(domain=ExpenseDomain.DIGITAL, current=Decimal(0.0), limit=Decimal(200)),
                    Expense(domain=ExpenseDomain.PHYSICAL, current=Decimal(0.0), limit=Decimal(200)),
                ]
