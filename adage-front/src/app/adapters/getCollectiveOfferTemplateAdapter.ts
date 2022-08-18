import { CollectiveOfferTemplateResponseModel } from 'apiClient'
import { api } from 'apiClient/api'
import { Adapter, AdapterFailure } from 'app/types'

type GetCollectiveOfferTemplateAdapter = Adapter<
  number,
  CollectiveOfferTemplateResponseModel,
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
      const result = await api.getCollectiveOfferTemplate(offerId)

      return {
        isOk: true,
        message: null,
        payload: result,
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
