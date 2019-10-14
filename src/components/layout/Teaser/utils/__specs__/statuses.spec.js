import { isReserved, reservationStatuses } from '../statuses'

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

describe('reservationStatuses()', () => {
  describe('when the reservation is not booked, fully booked, finished and expired', () => {
    describe('when the reservation is tomorrow', () => {
      it('should return an object with "Demain" and "tomorrow"', () => {
        // given
        const isActive = true
        const isNotBookable = false
        const isFullyBooked = false
        const hasBookings = false
        const isBooked = false
        const humanizeRelativeDate = 'Demain'

        // when
        const result = reservationStatuses(
          isActive,
          isNotBookable,
          isFullyBooked,
          hasBookings,
          humanizeRelativeDate,
          isBooked
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
        const isNotBookable = false
        const isFullyBooked = false
        const hasBookings = false
        const isBooked = false
        const humanizeRelativeDate = 'Aujourd’hui'

        // when
        const result = reservationStatuses(
          isActive,
          isNotBookable,
          isFullyBooked,
          hasBookings,
          humanizeRelativeDate,
          isBooked
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
        const isNotBookable = false
        const isFullyBooked = false
        const hasBookings = true
        const isBooked = true
        const humanizeRelativeDate = 'Demain'

        // when
        const result = reservationStatuses(
          isActive,
          isNotBookable,
          isFullyBooked,
          hasBookings,
          humanizeRelativeDate,
          isBooked
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
        const isNotBookable = false
        const isFullyBooked = false
        const hasBookings = true
        const isBooked = true
        const humanizeRelativeDate = 'Aujourd’hui'

        // when
        const result = reservationStatuses(
          isActive,
          isNotBookable,
          isFullyBooked,
          hasBookings,
          humanizeRelativeDate,
          isBooked
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
      const isNotBookable = true
      const isFullyBooked = null
      const hasBookings = null
      const isBooked = null
      const humanizeRelativeDate = ''

      // when
      const result = reservationStatuses(
        isActive,
        isNotBookable,
        isFullyBooked,
        hasBookings,
        humanizeRelativeDate,
        isBooked
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
        const isNotBookable = false
        const isFullyBooked = true
        const hasBookings = null
        const isBooked = null
        const humanizeRelativeDate = ''

        // when
        const result = reservationStatuses(
          isActive,
          isNotBookable,
          isFullyBooked,
          hasBookings,
          humanizeRelativeDate,
          isBooked
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
        const isNotBookable = false
        const isFullyBooked = true
        const hasBookings = true
        const isBooked = false
        const humanizeRelativeDate = ''

        // when
        const result = reservationStatuses(
          isActive,
          isNotBookable,
          isFullyBooked,
          hasBookings,
          humanizeRelativeDate,
          isBooked
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
      const isNotBookable = false
      const isFullyBooked = false
      const hasBookings = true
      const isBooked = true
      const humanizeRelativeDate = ''

      // when
      const result = reservationStatuses(
        isActive,
        isNotBookable,
        isFullyBooked,
        hasBookings,
        humanizeRelativeDate,
        isBooked
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
      const isNotBookable = false
      const isFullyBooked = false
      const hasBookings = true
      const isBooked = false
      const humanizeRelativeDate = 'Demain'

      // when
      const result = reservationStatuses(
        isActive,
        isNotBookable,
        isFullyBooked,
        hasBookings,
        humanizeRelativeDate,
        isBooked
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
      const isNotBookable = false
      const isFullyBooked = false
      const hasBookings = true
      const isBooked = false
      const humanizeRelativeDate = 'Demain'

      // when
      const result = reservationStatuses(
        isActive,
        isNotBookable,
        isFullyBooked,
        hasBookings,
        humanizeRelativeDate,
        isBooked
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
