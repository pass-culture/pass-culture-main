import { mapStateToProps } from '../MyBookingsListsContainer'

describe('src | components | pages | my-bookings | MyBookingsLists | MyBookingsListsContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return soon, other and finished/used/cancelled bookings', () => {
      // given
      const state = {
        data: {
          bookings: [],
          offers: [],
          stocks: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        bookingsOfTheWeek: [],
        finishedAndUsedAndCancelledBookings: [],
        upComingBookings: [],
      })
    })
  })
})
