import { mapDispatchToProps, mergeProps } from '../DeskContainer'

describe('src | DeskContainer', () => {
  let dispatch

  beforeEach(() => {
    dispatch = jest.fn()
  })

  describe('getBookingFromCode', () => {
    it('should dispatch an action with the expected parameters', () => {
      // given
      const { getBookingFromCode } = mapDispatchToProps(dispatch)
      const handleSuccess = jest.fn()
      const handleFail = jest.fn()

      // when
      getBookingFromCode('ABCDEF', handleSuccess, handleFail)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/v2/bookings/token/ABCDEF',
          handleFail,
          handleSuccess,
          method: 'GET',
          stateKey: 'deskBookings',
        },
        type: 'REQUEST_DATA_GET_DESKBOOKINGS',
      })
    })
  })

  describe('validateBooking', () => {
    it('should dispatch an action with the expected parameters', () => {
      // given
      const { validateBooking } = mapDispatchToProps(dispatch)
      const handleSuccess = jest.fn()
      const handleFail = jest.fn()

      // when
      validateBooking('ABCDEF', handleSuccess, handleFail)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/v2/bookings/use/token/ABCDEF',
          handleFail,
          handleSuccess,
          method: 'PATCH',
          stateKey: 'deskBookings',
        },
        type: 'REQUEST_DATA_PATCH_DESKBOOKINGS',
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {}
      const dispatchProps = {
        getBookingFromCode: () => {},
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
        getBookingFromCode: expect.any(Function),
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
