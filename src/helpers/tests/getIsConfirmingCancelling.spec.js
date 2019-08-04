import getIsConfirmingCancelling from '../getIsConfirmingCancelling'

describe('src | helpers | getIsConfirmingCancelling', () => {
  describe('when we just clicked on annuler', () => {
    it('should return false', () => {
      // given
      const match = {
        params: {
          bookings: 'reservations',
          cancellation: 'reservations',
        },
      }

      // when
      const isConfirmingCancelling = getIsConfirmingCancelling(match)

      //then
      expect(isConfirmingCancelling).toBe(false)
    })
  })

  describe('when we have confirmed the cancellation', () => {
    it('should return true', () => {
      // given
      const match = {
        params: {
          bookings: 'reservations',
          cancellation: 'annulation',
          confirmation: 'confirmation',
        },
      }

      // when
      const isConfirmingCancelling = getIsConfirmingCancelling(match)

      //then
      expect(isConfirmingCancelling).toBe(true)
    })
  })
})
