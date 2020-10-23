import { fetchFromApiWithCredentials } from 'utils/fetch'

import { mapDispatchToProps, mergeProps } from '../DeskContainer'

jest.mock('utils/fetch', () => ({
  fetchFromApiWithCredentials: jest.fn().mockImplementation(() => Promise.resolve()),
}))

describe('src | DeskContainer', () => {
  it('should retrive a booking with a token given', () => {
    // given
    const { getBooking } = mapDispatchToProps(jest.fn())

    // when
    getBooking('ABCDEF')

    // then
    expect(fetchFromApiWithCredentials).toHaveBeenCalledWith('/v2/bookings/token/ABCDEF')
  })

  it('should valid a booking with a token given', () => {
    // given
    const { validateBooking } = mapDispatchToProps(jest.fn())

    // when
    validateBooking('ABCDEF')

    // then
    expect(fetchFromApiWithCredentials).toHaveBeenCalledWith(
      '/v2/bookings/use/token/ABCDEF',
      'PATCH'
    )
  })

  describe('mergeProps', () => {
    it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {}
      const dispatchProps = {
        getBooking: () => {},
      }
      const ownProps = {
        match: {
          params: {},
        },
      }

      // when
      const mergedProps = mergeProps(stateProps, dispatchProps, ownProps)

      // then
      expect(mergedProps).toStrictEqual({
        getBooking: expect.any(Function),
        trackValidateBookingSuccess: expect.any(Function),
      })
    })

    it('should map a tracking event for validate a booking', () => {
      // given
      const stateProps = {
        offer: {
          id: 'B4',
        },
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackValidateBookingSuccess('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'validateBooking',
        name: 'RTgfd67',
      })
    })
  })
})
