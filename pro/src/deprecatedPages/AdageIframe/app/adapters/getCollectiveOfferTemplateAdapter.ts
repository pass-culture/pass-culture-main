import { apiAdage } from 'apiClient/api'

import { HydratedCollectiveOfferTemplate } from '../types/offers'

type GetCollectiveOfferTemplateAdapter = Adapter<
  number,
  HydratedCollectiveOfferTemplate,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: null,
}

export const getCollectiveOfferTemplateAdapter: GetCollectiveOfferTemplateAdapter =
  async offerId => {
    try {
      const result = await apiAdage.getCollectiveOfferTemplate(offerId)

      return {
        isOk: true,
        message: null,
        payload: { ...result, isTemplate: true },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
