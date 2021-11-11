import getIsBooking from '../getIsBooking'

describe('src | helpers | getIsBooking', () => {
  describe("when we just clicked on j'y vais", () => {
    it('should return true', () => {
      // given
      const match = {
        params: {
          booking: 'reservations',
        },
      }

      // when
      const isBooking = getIsBooking(match)

      //then
      expect(isBooking).toBe(true)
    })
  })

  describe('when we just clicked on annuler', () => {
    it('should return false', () => {
      // given
      const match = {
        params: {
          booking: 'reservations',
          cancellation: 'annulation',
        },
      }

      // when
      const isBooking = getIsBooking(match)

      //then
      expect(isBooking).toBe(false)
    })
  })

  describe('when we have just  cancel a booking', () => {
    it('should return true', () => {
      // given
      const match = {
        params: {
          booking: 'reservations',
          cancellation: 'annulation',
          confirmation: 'confirmation',
        },
      }

      // when
      const isBooking = getIsBooking(match)

      //then
      expect(isBooking).toBe(true)
    })
  })
})
