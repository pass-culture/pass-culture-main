import { mapStateToProps, mapDispatchToProps } from '../MyBookingsListsContainer'

import { bookingNormalizer } from '../../../../../utils/normalizers'

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

  describe('requestGetBookings()', () => {
    it('should dispatch the requested bookings ', () => {
      // given
      const dispatch = jest.fn()
      const handleFail = jest.fn()
      const handleSuccess = jest.fn()

      // when
      mapDispatchToProps(dispatch).requestGetBookings(handleFail, handleSuccess)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/bookings',
          handleFail,
          handleSuccess,
          method: 'GET',
          normalizer: bookingNormalizer,
        },
        type: 'REQUEST_DATA_GET_/BOOKINGS',
      })
    })
  })
})
