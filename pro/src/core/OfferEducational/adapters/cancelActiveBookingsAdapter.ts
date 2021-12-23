import * as pcapi from 'repository/pcapi/pcapi'

import { hasStatusCodeAndCode } from '../utils'

type IPayloadSuccess = null
type IPayloadFailure = null
type CancelActiveBookingsAdapter = Adapter<
  { offerId: string },
  IPayloadSuccess,
  IPayloadFailure
>

export const cancelActiveBookingsAdapter: CancelActiveBookingsAdapter = async ({
  offerId,
}) => {
  try {
    await pcapi.cancelEducationalBooking(offerId)
    /* @debt bugRisk "Gaël: we can't be sure this way that the stock is really booked, it can also be USED"*/
    return {
      isOk: true,
      message:
        'La réservation / préreservation sur cette offre à été annulée avec succès, votre offre sera à nouveau visible sur ADAGE',
      payload: null,
    }
  } catch (error) {
    const errorResponse = {
      isOk: false,
      payload: null,
    }

    if (
      hasStatusCodeAndCode(error) &&
      error.status === 400 &&
      error.code === 'NO_BOOKING'
    ) {
      return {
        ...errorResponse,
        message:
          'Cette offre n’a aucune reservation en cours. Il est possible que la réservation que vous tentiez d’annuler ai déjà été utilisée.',
      }
    }

    return {
      ...errorResponse,
      message:
        'Une erreur inconnue est survenue lors de l’annulation de la réservation.',
    }
  }
}
