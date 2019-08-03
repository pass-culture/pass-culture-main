import { mapDispatchToProps, mapStateToProps } from '../MyBookingDetailsContainer'
import { bookingNormalizer } from '../../../../../utils/normalizers'

describe('src | components | pages | MyBookings | MyBookingDetailsContainer', () => {
  it('mapStateToProps', () => {
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
    const receivedProps = mapStateToProps(state, ownProps)

    // then
    const expectedProps = {
      hasReceivedData: true,
      needsToRequestGetData: true,
    }
    expect(receivedProps).toStrictEqual(expectedProps)
  })

  it('mapDispatchToProps', () => {
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
