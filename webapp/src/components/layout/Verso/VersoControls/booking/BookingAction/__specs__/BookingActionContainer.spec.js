import { mapStateToProps } from '../BookingActionContainer'
import moment from 'moment'

describe('components | BookingActionContainer', () => {
  describe('mapStateToProps', () => {
    describe('when offer is not bookable', () => {
      it('should return true', () => {
        // given
        const ownProps = {
          location: {
            pathname: '/fake-url',
            search: '',
          },
          match: {
            params: {
              offerId: 'AE',
            },
          },
        }
        const state = {
          data: {
            bookings: [],
            offers: [{ id: 'AE', isBookable: false }],
            stocks: [{ id: 'BE', offerId: 'AE' }],
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCannotBeBooked).toBe(true)
      })
    })

    describe('when offer is bookable', () => {
      it('should return false', () => {
        // given
        const ownProps = {
          location: {
            pathname: '/fake-url',
            search: '',
          },
          match: {
            params: {
              offerId: 'AE',
            },
          },
        }
        const state = {
          data: {
            bookings: [],
            offers: [{ id: 'AE', isBookable: true }],
            stocks: [{ id: 'BE', offerId: 'AE' }],
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCannotBeBooked).toBe(false)
      })
    })

    describe('when coming from my bookings', () => {
      describe('when user has already booked this offer', () => {
        it('should return true', () => {
          // given
          const ownProps = {
            location: {
              pathname: '/fake-url',
              search: '',
            },
            match: {
              params: {
                offerId: 'AE',
              },
            },
          }

          const now = moment()
          const oneDayBeforeNow = now.subtract(1, 'days').format()
          const state = {
            data: {
              bookings: [{ id: 'CE', stockId: 'BE', isCancelled: false }],
              offers: [{ id: 'AE', isBookable: true }],
              stocks: [{ id: 'BE', offerId: 'AE', beginningDatetime: oneDayBeforeNow }],
            },
          }

          // when
          const props = mapStateToProps(state, ownProps)

          // then
          expect(props.offerCannotBeBooked).toBe(true)
        })
      })
    })
  })

  describe('bookingUrl', () => {
    it('should return booking url', () => {
      // given
      const ownProps = {
        location: {
          pathname: '/fake-url',
          search: '',
        },
        match: {
          params: {
            offerId: 'AE',
          },
        },
      }
      const state = {
        data: {
          bookings: [],
          offers: [{ id: 'AE', isBookable: false }],
          stocks: [{ id: 'BE', offerId: 'AE' }],
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props.bookingUrl).toBe('/fake-url/reservation')
    })
  })

  describe('priceRange', () => {
    it('should return price range when multiple stocks', () => {
      // given
      const ownProps = {
        location: {
          pathname: '/fake-url',
          search: '',
        },
        match: {
          params: {
            offerId: 'AE',
          },
        },
      }
      const state = {
        data: {
          bookings: [],
          offers: [{ id: 'AE', isBookable: false }],
          stocks: [
            { id: 'BE', offerId: 'AE', price: 10, isBookable: true },
            { id: 'CE', offerId: 'AE', price: 20, isBookable: true },
          ],
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props.priceRange).toStrictEqual([10, 20])
    })

    it('should return price range when coming from my bookings', () => {
      // given
      const ownProps = {
        location: {
          pathname: '/fake-url',
          search: '',
        },
        match: {
          params: {
            bookingId: 'BF',
          },
        },
      }
      const state = {
        data: {
          bookings: [{ id: 'BF', stockId: 'BE' }],
          offers: [{ id: 'AE', isBookable: false }],
          stocks: [{ id: 'BE', offerId: 'AE', price: 10, isBookable: true }],
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props.priceRange).toStrictEqual([10])
    })
  })
})
