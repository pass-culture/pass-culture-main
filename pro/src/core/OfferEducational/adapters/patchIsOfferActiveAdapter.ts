import { api } from 'apiClient/api'

import { offerAdageActivated, offerAdageDeactivate } from '../'

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
    // @ts-expect-error type string is not assignable to type number
    await api.patchOffersActiveStatus({ ids: [offerId], isActive })

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
      } de votre offre`,
      payload: null,
    }
  }
}
