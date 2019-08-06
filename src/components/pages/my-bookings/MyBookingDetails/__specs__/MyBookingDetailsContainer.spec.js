import { mapDispatchToProps, mapStateToProps } from '../MyBookingDetailsContainer'
import { bookingNormalizer } from '../../../../../utils/normalizers'

describe('src | components | pages | my-bookings | MyBookingsDetails | MyBookingDetailsContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return an object', () => {
      // given
      const bookingId = 'BF'
      const recommendationId = 'AE'
      const booking = {
        id: bookingId,
        recommendationId,
      }
      const recommendation = {
        id: recommendationId,
      }
      const state = {
        data: {
          bookings: [booking],
          recommendations: [recommendation],
        },
      }
      const ownProps = {
        booking,
        match: {
          params: {
            bookingId,
          },
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        hasReceivedData: true,
        needsToRequestGetData: true,
      })
    })
  })

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
