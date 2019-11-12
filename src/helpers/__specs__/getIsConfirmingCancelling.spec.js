import isCancelView from '../isCancelView'

describe('src | helpers | isCancelView', () => {
  describe('when we just clicked on annuler', () => {
    it('should return false', () => {
      // given
      const match = {
        params: {
          booking: 'reservations',
          cancellation: 'reservations',
        },
      }

      // when
      const isConfirmingCancelling = isCancelView(match)

      //then
      expect(isConfirmingCancelling).toBe(false)
    })
  })

  describe('when we have confirmed the cancellation', () => {
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
      const isConfirmingCancelling = isCancelView(match)

      //then
      expect(isConfirmingCancelling).toBe(true)
    })
  })
})
