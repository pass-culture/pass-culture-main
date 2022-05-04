import * as pcapi from 'repository/pcapi/pcapi'

import { hasStatusCodeAndErrorsCode } from '../utils'

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
    // the api returns no understandable error when the id is not valid, so we deal before calling the api
    if (!offerId || offerId === '')
      throw new Error('L’identifiant de l’offre n’est pas valide.')
    await pcapi.cancelEducationalBooking(offerId)
    /* @debt bugRisk "Gaël: we can't be sure this way that the stock is really booked, it can also be USED"*/
    return {
      isOk: true,
      message:
        'La réservation / préreservation sur cette offre à été annulée avec succès, votre offre sera à nouveau visible sur ADAGE.',
      payload: null,
    }
  } catch (error) {
    const errorResponse = {
      isOk: false,
      payload: null,
    }
    if (
      hasStatusCodeAndErrorsCode(error) &&
      error.status === 400 &&
      error.errors.code === 'NO_BOOKING'
    ) {
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
