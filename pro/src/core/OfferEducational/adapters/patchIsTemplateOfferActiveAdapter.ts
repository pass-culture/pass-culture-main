import { api } from 'apiClient/api'

import { offerAdageActivated, offerAdageDeactivate } from '../constants'

type IPayloadSuccess = null
type IPayloadFailure = null
type PatchIsOfferActiveAdapter = Adapter<
  { offerId: number; isActive: boolean },
  IPayloadSuccess,
  IPayloadFailure
>

export const patchIsTemplateOfferActiveAdapter: PatchIsOfferActiveAdapter =
  async ({ offerId, isActive }) => {
    try {
      // the api returns no understandable error when the id is not valid, so we deal before calling the api
      if (!offerId) {
        throw new Error('L’identifiant de l’offre n’est pas valide.')
      }

      await api.patchCollectiveOffersTemplateActiveStatus({
        ids: [offerId],
        isActive,
      })
      return {
        isOk: true,
        message: isActive ? offerAdageActivated : offerAdageDeactivate,
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
