import { mapStateToProps } from '../FinishableContainer'

describe('components | FinishableContainer', () => {
  describe('mapStateToProps', () => {
    describe('isNotBookable', () => {
      it('should return false when offer is not bookable and offer is already booked', () => {
        // given
        const state = {
          data: {
            bookings: [{ id: 'A1', stockId: 'B1' }],
            offers: [{ id: 'C1', isNotBookable: true }],
            stocks: [{ id: 'B1', offerId: 'C1' }]
          }
        }
        const ownProps = {
          isBooked: true,
          match: {
            params: {
              bookingId: 'A1'
            }
          }
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toStrictEqual({
          offerIsNoLongerBookable: false
        })
      })

      it('should return false when offer is bookable and offer is already booked', () => {
        // given
        const state = {
          data: {
            bookings: [{ id: 'A1', stockId: 'B1' }],
            offers: [{ id: 'C1', isNotBookable: false }],
            stocks: [{ id: 'B1', offerId: 'C1' }]
          }
        }
        const ownProps = {
          isBooked: true,
          match: {
            params: {
              bookingId: 'A1'
            }
          }
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toStrictEqual({
          offerIsNoLongerBookable: false
        })
      })

      it('should return true when offer is not bookable and offer is not booked', () => {
        // given
        const state = {
          data: {
            bookings: [{ id: 'A1', stockId: 'B1' }],
            offers: [{ id: 'C1', isNotBookable: true }],
            stocks: [{ id: 'B1', offerId: 'C1' }]
          }
        }
        const ownProps = {
          isBooked: false,
          match: {
            params: {
              bookingId: 'A1'
            }
          }
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toStrictEqual({
          offerIsNoLongerBookable: true
        })
      })

      it('should return false when offer is bookable and offer is not booked', () => {
        // given
        const state = {
          data: {
            bookings: [{ id: 'A1', stockId: 'B1' }],
            offers: [{ id: 'C1', isNotBookable: false }],
            stocks: [{ id: 'B1', offerId: 'C1' }]
          }
        }
        const ownProps = {
          isBooked: false,
          match: {
            params: {
              bookingId: 'A1'
            }
          }
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toStrictEqual({
          offerIsNoLongerBookable: false
        })
      })
    })
  })
})
