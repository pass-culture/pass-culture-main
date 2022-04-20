import * as pcapi from 'repository/pcapi/pcapi'

type IPayloadSuccess = null
type IPayloadFailure = null
type PatchIsOfferActiveAdapter = Adapter<
  { offerId: string; isActive: boolean },
  IPayloadSuccess,
  IPayloadFailure
>

export const patchIsOfferActiveAdapter: PatchIsOfferActiveAdapter = async ({
  offerId,
  isActive,
}) => {
  try {
    await pcapi.updateOffersActiveStatus(false, {
      // @ts-expect-error type number is not assigable to type never
      ids: [offerId],
      isActive,
    })

    return {
      isOk: true,
      message: isActive
        ? 'Votre offre est maintenant active et visible dans ADAGE'
        : 'Votre offre est maintenant inactive et sera invisible pour les utilisateurs d’ADAGE',
      payload: null,
    }
  } catch (error) {
    return {
      isOk: false,
      message: `Une erreur est survenue lors de ${
        isActive ? 'l’activation' : 'la désactivation'
      } de votre offre`,
      payload: null,
    }
  }
}
