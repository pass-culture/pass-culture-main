import { mapDispatchToProps } from '../DeskContainer'

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
        validateBooking: expect.any(Function)
      })
    })

    describe('getBookingFromCode', () => {
      it('should dispatch an action with the expected parameters', () => {
        // given
        const functions = mapDispatchToProps(dispatch)
        const {getBookingFromCode} = functions

        // when
        getBookingFromCode(
          'ABCDEF',
          jest.fn(),
          jest.fn()
        )

        // then
        expect(dispatch).toHaveBeenCalledWith(
          {
            config:
              {
                apiPath: '/bookings/token/ABCDEF',
                handleFail: expect.any(Function),
                handleSuccess: expect.any(Function),
                method: 'GET',
                stateKey: 'deskBookings'
              },
            type: 'REQUEST_DATA_GET_DESKBOOKINGS'
          }
        )
      })
    })

    describe('validateBooking', () => {
      it('should dispatch an action with the expected parameters', () => {
        // given
        const functions = mapDispatchToProps(dispatch)
        const {validateBooking} = functions

        // when
        validateBooking(
          'ABCDEF',
          jest.fn(),
          jest.fn()
        )

        // then
        expect(dispatch).toHaveBeenCalledWith(
          {
            config:
              {
                apiPath: '/bookings/token/ABCDEF',
                handleFail: expect.any(Function),
                handleSuccess: expect.any(Function),
                method: 'PATCH',
              },
            type: 'REQUEST_DATA_PATCH_/BOOKINGS/TOKEN/ABCDEF'
          }
        )
      })
    })

  })
})
