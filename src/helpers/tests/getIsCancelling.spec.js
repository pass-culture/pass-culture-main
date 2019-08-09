import getIsCancelling from '../getIsCancelling'

describe('src | helpers | getIsCancelling', () => {
  describe('when we just clicked on annuler', () => {
    it('should return true', () => {
      // given
      const match = {
        params: {
          booking: 'reservations',
          cancellation: 'reservations',
        },
      }

      // when
      const isCancelling = getIsCancelling(match)

      //then
      expect(isCancelling).toBe(true)
    })
  })

  describe('when we have confirmed the cancellation', () => {
    it('should return false', () => {
      // given
      const match = {
        params: {
          booking: 'reservations',
          cancellation: 'annulation',
          confirmation: 'confirmation',
        },
      }

      // when
      const isCancelling = getIsCancelling(match)

      //then
      expect(isCancelling).toBe(false)
    })
  })
})
