import { cancelActiveBookingsAdapter } from '../cancelActiveBookingsAdapter'

describe('cancelActiveBookingsAdapter', () => {
  describe('cancelCollectiveBookingAdapter', () => {
    it('should return an error when the offer id is not valid', async () => {
      // given

      // when
      const response = await cancelActiveBookingsAdapter({ offerId: '' })

      // then
      expect(response.isOk).toBeFalsy()
      expect(response.message).toBe(
        'Une erreur est survenue lors de l’annulation de la réservation. Error: L’identifiant de l’offre n’est pas valide.'
      )
    })

    it('should return an error when there are no bookings for this offer', async () => {
      // given
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        status: 400,
        json: async () => ({
          code: 'NO_BOOKING',
        }),
      })

      // when
      const response = await cancelActiveBookingsAdapter({ offerId: '12' })

      // then
      expect(response.isOk).toBeFalsy()
      expect(response.message).toBe(
        'Cette offre n’a aucune reservation en cours. Il est possible que la réservation que vous tentiez d’annuler ait déjà été utilisée.'
      )
    })
    it('should return a confirmation when the booking was cancelled', async () => {
      // given
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: true,
        status: 204,
      })

      // when
      const response = await cancelActiveBookingsAdapter({ offerId: '12' })

      // then
      expect(response.isOk).toBeTruthy()
      expect(response.message).toBe(
        'La réservation / préreservation sur cette offre à été annulée avec succès, votre offre sera à nouveau visible sur ADAGE.'
      )
    })
  })
})
