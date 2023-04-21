import { api } from 'apiClient/api'

import { CollectiveOffer } from '../types'

type IPayloadFailure = null
export type GetCollectiveOfferAdapter = Adapter<
  number,
  CollectiveOffer,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getCollectiveOfferAdapter: GetCollectiveOfferAdapter = async offerId => {
  try {
    const offer = await api.getCollectiveOffer(offerId)

    return {
      isOk: true,
      message: '',
      payload: { ...offer, isTemplate: false },
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getCollectiveOfferAdapter
