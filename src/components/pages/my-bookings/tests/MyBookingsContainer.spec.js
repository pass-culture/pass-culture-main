import { mapStateToProps, mapDispatchToProps } from '../MyBookingsContainer'

describe('src | components | pages | my-bookings | MyBookings', () => {
  describe('mapStateToProps()', () => {
    it('should return my bookings', () => {
      // given
      const state = {
        data: {
          bookings: [],
        },
      }

      // when
      const myBookings = mapStateToProps(state)

      // then
      expect(myBookings).toStrictEqual({
        myBookings: [],
        soonBookings: [],
      })
    })
  })

  describe('mapDispatchToProps()', () => {
    it('should dispatch my bookings', () => {
      // given
      const dispatch = jest.fn()
      const handleFail = jest.fn()
      const handleSuccess = jest.fn()

      // when
      mapDispatchToProps(dispatch).getMyBookings(handleFail, handleSuccess)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/bookings',
          handleFail: expect.any(Function),
          handleSuccess: expect.any(Function),
          method: 'GET',
          stateKey: 'bookings',
        },
        type: 'REQUEST_DATA_GET_BOOKINGS',
      })
    })
  })
})
