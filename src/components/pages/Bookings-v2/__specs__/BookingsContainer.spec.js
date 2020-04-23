import {mapStateToProps, mapDispatchToProps} from '../BookingsContainer'

describe('src | components | pages | Bookings-v2 | BookingsContainer', function () {
  describe('mapDispatchToProps', function () {
    let dispatch
    let props

    beforeEach(() => {
      dispatch = jest.fn()
      props = {}
    })

    it('should call api to load all bookings recap', function () {
      // Given
      const functions = mapDispatchToProps(dispatch)
      const handleSuccess = jest.fn()
      const handleFail = jest.fn()

      // When
      functions.requestGetAllBookingsRecap(handleSuccess, handleFail)

      // Then
      expect(dispatch.mock.calls[0][0]).toStrictEqual({
        config: {
          apiPath: '/bookings/pro',
          method: 'GET',
          handleSuccess: handleSuccess,
          handleFail: handleFail,
        },
        type: 'REQUEST_DATA_GET_/BOOKINGS/PRO',
      })
    })
  })

  describe('mapStateToProps', function () {
    it('should return an object with props', function () {
      // given
      const bookingsRecap = [
          {
            'stock': {
              'offer_name': 'Avez-vous déjà vu',
            },
            'beneficiary': {
              'lastname': 'Klepi',
              'firstname': 'Sonia',
              'email': 'sonia.klepi@example.com',
            },
            'booking_date': '2020-04-03T12:00:00Z',
            'booking_token': 'ZEHBGD',
          },
          {
            'stock': {
              'offer_name': 'Avez-vous déjà vu',
            },
            'beneficiary': {
              'lastname': 'Klepi',
              'firstname': 'Sonia',
              'email': 'sonia.klepi@example.com',
            },
            'booking_date': '2020-04-03T12:00:00Z',
            'booking_token': 'ZEHBGD',
          },
        ]

      const state = {
        data: {
          bookingsRecap: bookingsRecap
        },
      }

      // when
      const result = mapStateToProps(state)

      // then
      expect(result).toStrictEqual({bookingsRecap})
    })
  })
})
