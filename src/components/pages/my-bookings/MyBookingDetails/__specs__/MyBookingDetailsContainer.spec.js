import { mapDispatchToProps } from '../MyBookingDetailsContainer'
import { bookingNormalizer } from '../../../../../utils/normalizers'

describe('src | components | pages | my-bookings | MyBookingsDetails | MyBookingDetailsContainer', () => {
  describe('requestGetData()', () => {
    it('should dispatch my booking detail', () => {
      // given
      const dispatch = jest.fn()
      const handleSuccess = jest.fn()
      const bookingId = 'BF'
      const ownProps = {
        match: {
          params: {
            bookingId: bookingId,
          },
        },
      }

      // when
      mapDispatchToProps(dispatch, ownProps).requestGetData(handleSuccess)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: `/bookings/${bookingId}`,
          handleSuccess,
          method: 'GET',
          normalizer: bookingNormalizer,
        },
        type: `REQUEST_DATA_GET_/BOOKINGS/${bookingId.toUpperCase()}`,
      })
    })
  })
})
