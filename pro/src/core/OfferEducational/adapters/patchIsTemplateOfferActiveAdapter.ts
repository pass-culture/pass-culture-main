import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'

type IPayloadSuccess = null
type IPayloadFailure = null
type PatchIsOfferActiveAdapter = Adapter<
  { offerId: string; isActive: boolean },
  IPayloadSuccess,
  IPayloadFailure
>

export const patchIsTemplateOfferActiveAdapter: PatchIsOfferActiveAdapter =
  async ({ offerId, isActive }) => {
    try {
      // the api returns no understandable error when the id is not valid, so we deal before calling the api
      if (!offerId || offerId === '')
        throw new Error('L’identifiant de l’offre n’est pas valide.')

      await api.patchCollectiveOffersTemplateActiveStatus({
        // @ts-expect-error string is not assignable to type number
        ids: [offerId],
        isActive,
      })
      return {
        isOk: true,
        message: isActive
          ? 'Votre offre est maintenant active et visible dans ADAGE.'
          : 'Votre offre est maintenant inactive et sera invisible pour les utilisateurs d’ADAGE.',
        payload: null,
      }
    } catch (error) {
      return {
        isOk: false,
        message: `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } de votre offre. ${isErrorAPIError(error) && error.message}`,
        payload: null,
      }
    }
  }
