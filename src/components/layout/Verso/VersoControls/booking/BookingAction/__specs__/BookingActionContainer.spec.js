import { mapStateToProps } from '../BookingActionContainer'

describe('components | BookingActionContainer', () => {
  describe('mapStateToProps', () => {
    describe('isNotBookable', () => {
      it('should return true when offer is not bookable and offer is not fully booked', () => {
        // given
        const ownProps = {
          location: {
            pathname: '/fake-url',
            search: ''
          },
          match: {
            params: {
              offerId: 'AE'
            }
          }
        }
        const state = {
          data: {
            offers: [{ id: 'AE', isFullyBooked: false, isNotBookable: true }],
            stocks: [{ id: 'BE', offerId: 'AE' }]
          }
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCannotBeBooked).toBe(true)
      })

      it('should return true when offer is not bookable and offer is fully booked', () => {
        // given
        const ownProps = {
          location: {
            pathname: '/fake-url',
            search: ''
          },
          match: {
            params: {
              offerId: 'AE'
            }
          }
        }
        const state = {
          data: {
            offers: [{ id: 'AE', isFullyBooked: true, isNotBookable: true }],
            stocks: [{ id: 'BE', offerId: 'AE' }]
          }
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCannotBeBooked).toBe(true)
      })

      it('should return true when offer is bookable and offer is fully booked', () => {
        // given
        const ownProps = {
          location: {
            pathname: '/fake-url',
            search: ''
          },
          match: {
            params: {
              offerId: 'AE'
            }
          }
        }
        const state = {
          data: {
            offers: [{ id: 'AE', isFullyBooked: true, isNotBookable: false }],
            stocks: [{ id: 'BE', offerId: 'AE' }]
          }
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCannotBeBooked).toBe(true)
      })

      it('should return false when offer is bookable and offer is not fully booked', () => {
        // given
        const ownProps = {
          location: {
            pathname: '/fake-url',
            search: ''
          },
          match: {
            params: {
              offerId: 'AE'
            }
          }
        }
        const state = {
          data: {
            offers: [{ id: 'AE', isFullyBooked: false, isNotBookable: false }],
            stocks: [{ id: 'BE', offerId: 'AE' }]
          }
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.offerCannotBeBooked).toBe(false)
      })
    })

    describe('bookingUrl', () => {
      it('should return booking url', () => {
        // given
        const ownProps = {
          location: {
            pathname: '/fake-url',
            search: ''
          },
          match: {
            params: {
              offerId: 'AE'
            }
          }
        }
        const state = {
          data: {
            offers: [{ id: 'AE', isFullyBooked: false, isNotBookable: true }],
            stocks: [{ id: 'BE', offerId: 'AE' }]
          }
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
            search: ''
          },
          match: {
            params: {
              offerId: 'AE'
            }
          }
        }
        const state = {
          data: {
            offers: [{ id: 'AE', isFullyBooked: false, isNotBookable: true }],
            stocks: [
              { id: 'BE', offerId: 'AE', price: 10, available: 10, isBookable: true },
              { id: 'CE', offerId: 'AE', price: 20, available: 10, isBookable: true }
            ]
          }
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props.priceRange).toStrictEqual([10, 20])
      })
    })
  })
})
