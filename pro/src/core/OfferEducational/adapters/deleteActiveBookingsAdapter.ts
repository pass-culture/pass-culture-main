import * as pcapi from 'repository/pcapi/pcapi'

type IPayloadSuccess = null
type IPayloadFailure = null
type DeleteActiveBookingsAdapter = Adapter<
  { offerId: string },
  IPayloadSuccess,
  IPayloadFailure
>

export const deleteActiveBookingsAdapter: DeleteActiveBookingsAdapter = async ({
  offerId,
}) => {
  try {
    await pcapi.cancelEducationalBooking(offerId)

    /* @debt bugRisk "Gaël: we can't be sure this way that the stock is really booked, it can also be USED or CANCELED"*/
    return {
      isOk: true,
      message:
        'Les réservations et pré-reservations sur cette offre ont été annulés avec succès, votre offre sera à nouveau visible par tous sur adage',
      payload: null,
    }
  } catch (error) {
    console.log(error.status)
    console.log(error.code)

    return {
      isOk: false,
      message:
        'Une erreur inconnue est survenue lors de l’annulation des reservation.',
      payload: null,
    }
  }
}
