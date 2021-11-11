import { mapStateToProps } from '../BookingCancellationContainer'

describe('src | components | layout | BookingCancellation | BookingCancellationContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const ownProps = {
        match: {
          params: {
            bookingId: 'bookingId',
            offerId: 'offerId',
          },
        },
      }

      const state = {
        currentUser: {
          deposit_expiration_date: '2019-01-01T09:00:00.000000Z',
        },
        data: {
          bookings: [
            {
              id: 'bookingId',
            },
          ],
          offers: [
            {
              id: 'offerId',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        booking: {
          id: 'bookingId',
        },
        isWalletValid: false,
        offer: {
          id: 'offerId',
        },
      })
    })
  })
})
