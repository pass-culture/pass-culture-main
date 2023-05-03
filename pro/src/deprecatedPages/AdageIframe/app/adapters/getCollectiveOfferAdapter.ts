import { apiAdage } from 'apiClient/api'

import { HydratedCollectiveOffer } from '../types/offers'

type GetCollectiveOfferAdapter = Adapter<number, HydratedCollectiveOffer, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: null,
}

export const getCollectiveOfferAdapter: GetCollectiveOfferAdapter =
  async offerId => {
    try {
      const result = await apiAdage.getCollectiveOffer(offerId)

      return {
        isOk: true,
        message: null,
        payload: { ...result, isTemplate: false },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
