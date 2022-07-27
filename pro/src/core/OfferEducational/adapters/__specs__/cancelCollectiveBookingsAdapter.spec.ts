import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'

import { cancelCollectiveBookingAdapter } from '../cancelCollectiveBookingAdapter'

describe('cancelCollectiveBookingAdapter', () => {
  it('should return an error when the offer id is not valid', async () => {
    // given

    // when
    const response = await cancelCollectiveBookingAdapter({ offerId: '' })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors de l’annulation de la réservation. Error: L’identifiant de l’offre n’est pas valide.'
    )
  })

  it('should return an error when there are no bookings for this offer', async () => {
    // given
    jest
      .spyOn(api, 'cancelCollectiveOfferBooking')
      .mockRejectedValueOnce(
        new ApiError(
          {} as ApiRequestOptions,
          { body: { code: 'NO_BOOKING' }, status: 400 } as ApiResult,
          ''
        )
      )

    // when
    const response = await cancelCollectiveBookingAdapter({ offerId: '12' })

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
    const response = await cancelCollectiveBookingAdapter({ offerId: '12' })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'La réservation / préreservation sur cette offre à été annulée avec succès, votre offre sera à nouveau visible sur ADAGE.'
    )
  })
})
