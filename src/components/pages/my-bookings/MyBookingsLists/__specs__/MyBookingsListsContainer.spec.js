import { mapStateToProps } from '../MyBookingsListsContainer'

describe('src | components | pages | my-bookings | MyBookingsLists | MyBookingsListsContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return soon and other bookings', () => {
      // given
      const state = {
        data: {
          bookings: [],
          offers: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        otherBookings: [],
        soonBookings: [],
      })
    })
  })
})
