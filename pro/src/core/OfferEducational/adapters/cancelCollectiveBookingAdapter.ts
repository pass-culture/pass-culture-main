import { api } from 'apiClient/api'
import { getErrorCode, isErrorAPIError } from 'apiClient/helpers'
import { OfferStatus } from 'apiClient/v2'

type PayloadSuccess = null
type PayloadFailure = null
type cancelCollectiveBookingAdapter = Adapter<
  { offerId?: string; offerStatus?: string },
  PayloadSuccess,
  PayloadFailure
>

export const cancelCollectiveBookingAdapter: cancelCollectiveBookingAdapter =
  async ({ offerId, offerStatus }) => {
    const message =
      offerStatus === OfferStatus.EXPIRED
        ? 'La réservation sur cette offre a été annulée.'
        : 'La réservation sur cette offre a été annulée avec succès, votre offre sera à nouveau visible sur ADAGE.'

    try {
      // the api returns no understandable error when the id is not valid, so we deal before calling the api
      if (!offerId || offerId === '') {
        throw new Error('L’identifiant de l’offre n’est pas valide.')
      }
      await api.cancelCollectiveOfferBooking(offerId)
      return {
        isOk: true,
        message: message,
        payload: null,
      }
    } catch (error) {
      const errorResponse = {
        isOk: false,
        payload: null,
      }

      if (isErrorAPIError(error) && getErrorCode(error) === 'NO_BOOKING') {
        return {
          ...errorResponse,
          message:
            'Cette offre n’a aucune reservation en cours. Il est possible que la réservation que vous tentiez d’annuler ait déjà été utilisée.',
        }
      }

      return {
        ...errorResponse,
        message: `Une erreur est survenue lors de l’annulation de la réservation. ${error}`,
      }
    }
  }
