import { mapStateToProps } from '../FinishableContainer'

describe('components | FinishableContainer', () => {
  describe('mapStateToProps', () => {
    describe('not isBookable', () => {
      describe('when coming from /reservations', () => {
        it('should return false when offer is not bookable, is fully booked, offer is already booked', () => {
          // given
          const state = {
            data: {
              bookings: [{ id: 'A1', stockId: 'B1' }],
              offers: [{ id: 'C1', isBookable: false }],
              stocks: [{ id: 'B1', offerId: 'C1' }],
            },
          }
          const ownProps = {
            isBooked: true,
            match: {
              params: {
                bookingId: 'A1',
              },
            },
          }

          // when
          const props = mapStateToProps(state, ownProps)

          // then
          expect(props).toStrictEqual({
            offerCannotBeBooked: false,
          })
        })

        it('should return false when offer is bookable, not fully booked and offer is already booked', () => {
          // given
          const state = {
            data: {
              bookings: [{ id: 'A1', stockId: 'B1' }],
              offers: [{ id: 'C1', isBookable: true }],
              stocks: [{ id: 'B1', offerId: 'C1' }],
            },
          }
          const ownProps = {
            isBooked: true,
            match: {
              params: {
                bookingId: 'A1',
              },
            },
          }

          // when
          const props = mapStateToProps(state, ownProps)

          // then
          expect(props).toStrictEqual({
            offerCannotBeBooked: false,
          })
        })

        it('should return true when offer is not bookable, is fully booked and offer is not booked', () => {
          // given
          const state = {
            data: {
              bookings: [{ id: 'A1', stockId: 'B1' }],
              offers: [{ id: 'C1', isBookable: false }],
              stocks: [{ id: 'B1', offerId: 'C1' }],
            },
          }
          const ownProps = {
            isBooked: false,
            match: {
              params: {
                bookingId: 'A1',
              },
            },
          }

          // when
          const props = mapStateToProps(state, ownProps)

          // then
          expect(props).toStrictEqual({
            offerCannotBeBooked: true,
          })
        })

        it('should return false when offer is bookable, not fully booked and offer is not booked', () => {
          // given
          const state = {
            data: {
              bookings: [{ id: 'A1', stockId: 'B1' }],
              offers: [{ id: 'C1', isBookable: true }],
              stocks: [{ id: 'B1', offerId: 'C1' }],
            },
          }
          const ownProps = {
            isBooked: false,
            match: {
              params: {
                bookingId: 'A1',
              },
            },
          }

          // when
          const props = mapStateToProps(state, ownProps)

          // then
          expect(props).toStrictEqual({
            offerCannotBeBooked: false,
          })
        })
      })

      describe('when coming from other routes', () => {
        it('should return false when offer is not bookable, is fully booked and offer is already booked', () => {
          // given
          const state = {
            data: {
              offers: [{ id: 'A1', isBookable: false }],
            },
          }
          const ownProps = {
            isBooked: true,
            match: {
              params: {
                offerId: 'A1',
              },
            },
          }

          // when
          const props = mapStateToProps(state, ownProps)

          // then
          expect(props).toStrictEqual({
            offerCannotBeBooked: false,
          })
        })

        it('should return false when offer is bookable, not fully booked and offer is already booked', () => {
          // given
          const state = {
            data: {
              offers: [{ id: 'A1', isBookable: true }],
            },
          }
          const ownProps = {
            isBooked: true,
            match: {
              params: {
                offerId: 'A1',
              },
            },
          }

          // when
          const props = mapStateToProps(state, ownProps)

          // then
          expect(props).toStrictEqual({
            offerCannotBeBooked: false,
          })
        })

        it('should return true when offer is not bookable, is fully booked and offer is not booked', () => {
          // given
          const state = {
            data: {
              offers: [{ id: 'A1', isBookable: false }],
            },
          }
          const ownProps = {
            isBooked: false,
            match: {
              params: {
                offerId: 'A1',
              },
            },
          }

          // when
          const props = mapStateToProps(state, ownProps)

          // then
          expect(props).toStrictEqual({
            offerCannotBeBooked: true,
          })
        })

        it('should return false when offer is bookable, not fully booked and offer is not booked', () => {
          // given
          const state = {
            data: {
              offers: [{ id: 'A1', isBookable: true }],
            },
          }
          const ownProps = {
            isBooked: false,
            match: {
              params: {
                offerId: 'A1',
              },
            },
          }

          // when
          const props = mapStateToProps(state, ownProps)

          // then
          expect(props).toStrictEqual({
            offerCannotBeBooked: false,
          })
        })
      })
    })
  })
})
