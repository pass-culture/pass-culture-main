import { isReserved, mapStateToProps, reservationStatus } from '../MyFavoriteContainer'

describe('src | components | pages | my-favorite | MyFavorite | MyFavoriteContainer', () => {
  describe('isReserved()', () => {
    describe('when the offer is reserved', () => {
      it('should return true', () => {
        // given
        const status = [
          {
            class: 'booked',
          },
        ]

        // when
        const result = isReserved(status)

        // then
        expect(result).toBe(true)
      })
    })

    describe('when the offer is cancelled, finished or fully-booked', () => {
      it('should return false', () => {
        // given
        const status = [
          {
            class: 'cancelled',
          },
        ]

        // when
        const result = isReserved(status)

        // then
        expect(result).toBe(false)
      })
    })
  })

  describe('reservationStatus()', () => {
    describe('when the reservation is not booked, fully booked, finished and expired', () => {
      describe('when the reservation is tomorrow', () => {
        it('should return an object with "Demain" and "tomorrow"', () => {
          // given
          const isActive = true
          const isFinished = false
          const isFullyBooked = false
          const hasBookings = false
          const isBooked = false
          const humanizeRelativeDate = 'Demain'

          // when
          const result = reservationStatus(
            isActive,
            isFinished,
            isFullyBooked,
            hasBookings,
            isBooked,
            humanizeRelativeDate
          )

          // then
          expect(result).toStrictEqual([
            {
              label: 'Demain',
              class: 'tomorrow',
            },
          ])
        })
      })

      describe('when the reservation is today', () => {
        it('should return an object with "Aujourd’hui" and "today"', () => {
          // given
          const isActive = true
          const isFinished = false
          const isFullyBooked = false
          const hasBookings = false
          const isBooked = false
          const humanizeRelativeDate = 'Aujourd’hui'

          // when
          const result = reservationStatus(
            isActive,
            isFinished,
            isFullyBooked,
            hasBookings,
            isBooked,
            humanizeRelativeDate
          )

          // then
          expect(result).toStrictEqual([
            {
              label: 'Aujourd’hui',
              class: 'today',
            },
          ])
        })
      })
    })

    describe('when the reservation is booked', () => {
      describe('when the reservation is tomorrow', () => {
        it('should return an object with "Demain" and "tomorrow" and "Réservé" and "booked"', () => {
          // given
          const isActive = true
          const isFinished = false
          const isFullyBooked = false
          const hasBookings = true
          const isBooked = true
          const humanizeRelativeDate = 'Demain'

          // when
          const result = reservationStatus(
            isActive,
            isFinished,
            isFullyBooked,
            hasBookings,
            isBooked,
            humanizeRelativeDate
          )

          // then
          expect(result).toStrictEqual([
            {
              label: 'Réservé',
              class: 'booked',
            },
            {
              label: 'Demain',
              class: 'tomorrow',
            },
          ])
        })
      })

      describe('when the reservation is today', () => {
        it('should return an object with "Aujourd’hui" and "today" and "Réservé" and "booked"', () => {
          // given
          const isActive = true
          const isFinished = false
          const isFullyBooked = false
          const hasBookings = true
          const isBooked = true
          const humanizeRelativeDate = 'Aujourd’hui'

          // when
          const result = reservationStatus(
            isActive,
            isFinished,
            isFullyBooked,
            hasBookings,
            isBooked,
            humanizeRelativeDate
          )

          // then
          expect(result).toStrictEqual([
            {
              label: 'Réservé',
              class: 'booked',
            },
            {
              label: 'Aujourd’hui',
              class: 'today',
            },
          ])
        })
      })
    })

    describe('when the reservation is finished', () => {
      it('should return an object with "Terminé" and "finished"', () => {
        // given
        const isActive = true
        const isFinished = true
        const isFullyBooked = null
        const hasBookings = null
        const isBooked = null
        const humanizeRelativeDate = ''

        // when
        const result = reservationStatus(
          isActive,
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(result).toStrictEqual([
          {
            label: 'Terminé',
            class: 'finished',
          },
        ])
      })
    })

    describe('when the reservation is fully booked', () => {
      describe('when the reservation is not cancelled', () => {
        it('should return an object with "Épuisé" and "fully-booked"', () => {
          // given
          const isActive = true
          const isFinished = false
          const isFullyBooked = true
          const hasBookings = null
          const isBooked = null
          const humanizeRelativeDate = ''

          // when
          const result = reservationStatus(
            isActive,
            isFinished,
            isFullyBooked,
            hasBookings,
            isBooked,
            humanizeRelativeDate
          )

          // then
          expect(result).toStrictEqual([
            {
              label: 'Épuisé',
              class: 'fully-booked',
            },
          ])
        })
      })

      describe('when the reservation is cancelled', () => {
        it('should return an object with "Annulé" and "cancel"', () => {
          // given
          const isActive = true
          const isFinished = false
          const isFullyBooked = true
          const hasBookings = true
          const isBooked = false
          const humanizeRelativeDate = ''

          // when
          const result = reservationStatus(
            isActive,
            isFinished,
            isFullyBooked,
            hasBookings,
            isBooked,
            humanizeRelativeDate
          )

          // then
          expect(result).toStrictEqual([
            {
              label: 'Annulé',
              class: 'cancelled',
            },
          ])
        })
      })
    })

    describe('when the reservation has bookings and is booked', () => {
      it('should return an object with "Réservé" and "booked"', () => {
        // given
        const isActive = true
        const isFinished = false
        const isFullyBooked = false
        const hasBookings = true
        const isBooked = true
        const humanizeRelativeDate = ''

        // when
        const result = reservationStatus(
          isActive,
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(result).toStrictEqual([
          {
            label: 'Réservé',
            class: 'booked',
          },
        ])
      })
    })

    describe('when the reservation has bookings and is not booked', () => {
      it('should return an object with "Annulé" and "cancelled" even if there is a date', () => {
        // given
        const isActive = true
        const isFinished = false
        const isFullyBooked = false
        const hasBookings = true
        const isBooked = false
        const humanizeRelativeDate = 'Demain'

        // when
        const result = reservationStatus(
          isActive,
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(result).toStrictEqual([
          {
            label: 'Annulé',
            class: 'cancelled',
          },
        ])
      })
    })

    describe('when the reservation is disabled', () => {
      it('should return an object with "Annulé" and "cancelled" even if there is a date', () => {
        // given
        const isActive = false
        const isFinished = false
        const isFullyBooked = false
        const hasBookings = true
        const isBooked = false
        const humanizeRelativeDate = 'Demain'

        // when
        const result = reservationStatus(
          isActive,
          isFinished,
          isFullyBooked,
          hasBookings,
          isBooked,
          humanizeRelativeDate
        )

        // then
        expect(result).toStrictEqual([
          {
            label: 'Annulé',
            class: 'cancelled',
          },
        ])
      })
    })
  })

  describe('mapStateToProps()', () => {
    it('should return default props', () => {
      // given
      const ownProps = {
        favorite: {
          offerId: 'o1',
          thumbUrl: 'fake/thumb/url',
        },
        handleToggleFavorite: jest.fn(),
        isEditMode: false,
      }
      const offer = {
        dateRange: ['2030-07-21T20:00:00Z', '2030-08-21T20:00:00Z'],
        id: 'o1',
        isActive: true,
        isFinished: false,
        isFullyBooked: false,
        name: 'Fake offer name',
        offerType: {
          appLabel: 'Fake offer type',
        },
        venue: {
          latitude: 48.91683,
          longitude: 2.4388,
        },
      }
      const state = {
        data: {
          bookings: [
            {
              id: 'b1',
              isCancelled: false,
              stockId: 's1',
            },
          ],
          offers: [offer],
          stocks: [
            {
              id: 's1',
              beginningDatetime: '2030-08-21T20:00:00Z',
              offerId: 'o1',
            },
          ],
        },
        geolocation: {
          latitude: 48.8636537,
          longitude: 2.3371206000000004,
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        date: 'du 2030-7-21 au 2030-8-21',
        detailsUrl: '//details/o1',
        handleToggleFavorite: expect.any(Function),
        humanizeRelativeDistance: '10 km',
        isEditMode: false,
        name: 'Fake offer name',
        offerId: 'o1',
        offerTypeLabel: 'Fake offer type',
        status: [{ class: 'booked', label: 'Réservé' }],
        thumbUrl: 'fake/thumb/url',
      })
    })
  })
})
