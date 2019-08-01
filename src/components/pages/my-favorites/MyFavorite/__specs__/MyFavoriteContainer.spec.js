import { isBooked, mapStateToProps, reservationStatus } from '../MyFavoriteContainer'

describe('src | components | pages | my-favorite | MyFavorite | MyFavoriteContainer', () => {
  describe('isBooked()', () => {
    describe('when there is at least one booking', () => {
      it('should return true', () => {
        // given
        const offer = {
          stocks: [
            {
              bookings: [
                {
                  isCancelled: false,
                },
                {
                  isCancelled: true,
                },
                {
                  isCancelled: false,
                },
              ],
            },
          ],
        }

        // when
        const expected = isBooked(offer)

        // then
        expect(expected).toBe(true)
      })
    })

    describe('when there is no booking', () => {
      it('should return false', () => {
        // given
        const offer = {
          stocks: [
            {
              bookings: [
                {
                  isCancelled: false,
                },
                {
                  isCancelled: true,
                },
                {
                  isCancelled: false,
                },
                {
                  isCancelled: true,
                },
              ],
            },
          ],
        }

        // when
        const expected = isBooked(offer)

        // then
        expect(expected).toBe(false)
      })
    })
  })

  describe('reservationStatus()', () => {
    describe('when the reservation is finished', () => {
      it('should return an object with "Terminé" and "finished"', () => {
        // given
        const isFinished = true
        const isFullyBooked = null
        const hasBookings = null
        const isBooked = null
        const humanizeRelativeDate = ''

        // when
        const expected = reservationStatus(
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(expected).toStrictEqual({
          label: 'Terminé',
          class: 'finished',
        })
      })
    })

    describe('when the reservation is fully booked', () => {
      it('should return an object with "Épuisé" and "fully-booked"', () => {
        // given
        const isFinished = false
        const isFullyBooked = true
        const hasBookings = null
        const isBooked = null
        const humanizeRelativeDate = ''

        // when
        const expected = reservationStatus(
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(expected).toStrictEqual({
          label: 'Épuisé',
          class: 'fully-booked',
        })
      })
    })

    describe('when the reservation has bookings and is booked', () => {
      it('should return an object with "Réservé" and "booked"', () => {
        // given
        const isFinished = false
        const isFullyBooked = false
        const hasBookings = true
        const isBooked = true
        const humanizeRelativeDate = ''

        // when
        const expected = reservationStatus(
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(expected).toStrictEqual({
          label: 'Réservé',
          class: 'booked',
        })
      })
    })

    describe('when the reservation has bookings and is not booked', () => {
      it('should return an object with "Annulé" and "cancelled"', () => {
        // given
        const isFinished = false
        const isFullyBooked = false
        const hasBookings = true
        const isBooked = false
        const humanizeRelativeDate = ''

        // when
        const expected = reservationStatus(
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(expected).toStrictEqual({
          label: 'Annulé',
          class: 'cancelled',
        })
      })
    })

    describe('when the reservation is tomorrow', () => {
      it('should return an object with "Demain" and "tomorrow"', () => {
        // given
        const isFinished = false
        const isFullyBooked = false
        const hasBookings = false
        const isBooked = false
        const humanizeRelativeDate = 'Demain'

        // when
        const expected = reservationStatus(
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(expected).toStrictEqual({
          label: 'Demain',
          class: 'tomorrow',
        })
      })
    })

    describe('when the reservation is today', () => {
      it('should return an object with "Aujourd’hui" and "today"', () => {
        // given
        const isFinished = false
        const isFullyBooked = false
        const hasBookings = false
        const isBooked = false
        const humanizeRelativeDate = 'Aujourd’hui'

        // when
        const expected = reservationStatus(
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(expected).toStrictEqual({
          label: 'Aujourd’hui',
          class: 'today',
        })
      })
    })
  })

  describe('mapStateToProps()', () => {
    it('should return default props', () => {
      // given
      const ownProps = {
        favorite: {
          offerId: 'ME',
          offer: {
            id: 'ME',
            name: 'Fake favorite name',
            dateRange: ['2018-07-21T20:00:00Z', '2018-08-21T20:00:00Z'],
            product: {
              offerType: {
                appLabel: 'Fake offer type',
              },
            },
            stocks: [
              {
                bookings: [],
              },
            ],
            venue: {
              latitude: 48.91683,
              longitude: 2.4388,
            },
          },
          mediationId: 'FA',
          mediation: {
            id: 'FA',
            thumbUrl: 'https://example.net/mediation/image',
          },
        },
      }
      const state = {
        geolocation: {
          latitude: 48.8636537,
          longitude: 2.3371206000000004,
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        humanizeRelativeDistance: '10 km',
        name: 'Fake favorite name',
        offerTypeLabel: 'Fake offer type',
        status: null,
        thumbUrl: 'https://example.net/mediation/image',
        versoUrl: '/decouverte/ME/FA/verso',
      })
    })
  })
})
