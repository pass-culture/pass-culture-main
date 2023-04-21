import { api } from 'apiClient/api'

import { CollectiveOfferTemplate } from '../types'

type IPayloadFailure = null
export type GetCollectiveOfferTemplateAdapter = Adapter<
  number,
  CollectiveOfferTemplate,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getCollectiveOfferTemplateAdapter: GetCollectiveOfferTemplateAdapter =
  async offerId => {
    try {
      const offer = await api.getCollectiveOfferTemplate(offerId)

      return {
        isOk: true,
        message: '',
        payload: { ...offer, isTemplate: true },
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }

export default getCollectiveOfferTemplateAdapter
