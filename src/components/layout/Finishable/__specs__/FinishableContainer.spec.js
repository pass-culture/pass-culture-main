import { mapStateToProps } from '../FinishableContainer'
import getIsBooked from '../../../../utils/getIsBooked'

jest.mock('../../../../utils/getIsBooked')

describe('components | FinishableContainer', () => {
  describe('mapStateToProps', () => {
    describe('when offer is a tuto', () => {
      it('should be bookable', () => {
        // given
        const state = {
          data: {
            bookings: [{}],
            offers: [{}],
            stocks: [{}],
          },
        }
        const ownProps = {
          match: {
            params: {},
          },
        }
        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCanBeBooked).toBe(true)
      })
    })

    describe('when coming from /reservations', () => {
      it('should return true when offer has been booked by current user', () => {
        // given
        getIsBooked.mockReturnValue(true)

        const state = {
          data: {
            bookings: [{ id: 'A1', stockId: 'B1' }],
            offers: [{ id: 'C1', isBookable: false }],
            stocks: [{ id: 'B1', offerId: 'C1' }],
          },
        }
        const ownProps = {
          match: {
            params: {
              bookingId: 'A1',
            },
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCanBeBooked).toBe(true)
      })

      it('should return false when offer is not bookable anymore and current user has not booked it', () => {
        // given
        getIsBooked.mockReturnValue(false)
        const state = {
          data: {
            bookings: [{ id: 'A1', stockId: 'B1' }],
            offers: [{ id: 'C1', isBookable: false }],
            stocks: [{ id: 'B1', offerId: 'C1' }],
          },
        }
        const ownProps = {
          match: {
            params: {
              bookingId: 'A1',
            },
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCanBeBooked).toBe(false)
      })

      it('should return true when offer is bookable', () => {
        // given
        const state = {
          data: {
            bookings: [{ id: 'A1', stockId: 'B1' }],
            offers: [{ id: 'C1', isBookable: true }],
            stocks: [{ id: 'B1', offerId: 'C1' }],
          },
        }
        const ownProps = {
          match: {
            params: {
              bookingId: 'A1',
            },
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCanBeBooked).toBe(true)
      })
    })

    describe('when coming from other routes', () => {
      it('should return false when offer is not bookable', () => {
        // given
        getIsBooked.mockReturnValue(false)

        const state = {
          data: {
            bookings: [{ id: 'A1', stockId: 'B1' }],
            offers: [{ id: 'A1', isBookable: false }],
            stocks: [{ id: 'B1', offerId: 'C1' }],
          },
        }
        const ownProps = {
          match: {
            params: {
              offerId: 'A1',
            },
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCanBeBooked).toBe(false)
      })

      it('should return true when offer is bookable', () => {
        // given
        getIsBooked.mockReturnValue(false)

        const state = {
          data: {
            bookings: [{ id: 'A1', stockId: 'B1' }],
            offers: [{ id: 'A1', isBookable: true }],
            stocks: [{ id: 'B1', offerId: 'C1' }],
          },
        }
        const ownProps = {
          match: {
            params: {
              offerId: 'A1',
            },
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCanBeBooked).toBe(true)
      })
    })
  })
})
