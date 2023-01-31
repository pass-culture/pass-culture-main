import { api } from 'apiClient/api'

type IPayloadSuccess = null
type IPayloadFailure = null
type PatchIsOfferActiveAdapter = Adapter<
  { offerId: string; isActive: boolean },
  IPayloadSuccess,
  IPayloadFailure
>

export const patchIsCollectiveOfferActiveAdapter: PatchIsOfferActiveAdapter =
  async ({ offerId, isActive }) => {
    try {
      // the api returns no understandable error when the id is not valid, so we deal before calling the api
      if (!offerId || offerId === '') {
        throw new Error('L’identifiant de l’offre n’est pas valide.')
      }

      // @ts-expect-error type string is not assignable to type number
      await api.patchCollectiveOffersActiveStatus({ ids: [offerId], isActive })

      return {
        isOk: true,
        message: isActive
          ? 'Votre offre est maintenant active et visible dans ADAGE'
          : 'Votre offre est désactivée et n’est plus visible sur ADAGE',
        payload: null,
      }
    } catch (error) {
      return {
        isOk: false,
        message: `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } de votre offre. ${
          // @ts-expect-error
          error?.message ?? ''
        }`,
        payload: null,
      }
    }
  }
