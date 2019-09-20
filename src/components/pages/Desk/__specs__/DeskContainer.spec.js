import { mapDispatchToProps, mergeProps } from '../DeskContainer'

describe('src | components | pages | Desk | DeskContainer ', () => {
  let dispatch

  beforeEach(() => {
    dispatch = jest.fn()
  })

  describe('mapDispatchToProps', () => {
    it('should return an object of functions', () => {
      // when
      const result = mapDispatchToProps(dispatch)

      // then
      expect(result).toStrictEqual({
        getBookingFromCode: expect.any(Function),
        validateBooking: expect.any(Function),
      })
    })

    describe('getBookingFromCode', () => {
      it('should dispatch an action with the expected parameters', () => {
        // given
        const functions = mapDispatchToProps(dispatch)
        const { getBookingFromCode } = functions

        // when
        getBookingFromCode('ABCDEF', jest.fn(), jest.fn())

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/bookings/token/ABCDEF',
            handleFail: expect.any(Function),
            handleSuccess: expect.any(Function),
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
        const functions = mapDispatchToProps(dispatch)
        const { validateBooking } = functions

        // when
        validateBooking('ABCDEF', jest.fn(), jest.fn())

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/bookings/token/ABCDEF',
            handleFail: expect.any(Function),
            handleSuccess: expect.any(Function),
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
})
