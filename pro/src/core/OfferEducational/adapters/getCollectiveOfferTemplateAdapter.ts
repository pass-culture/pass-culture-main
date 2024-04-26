import { api } from 'apiClient/api'
import { GetCollectiveOfferTemplateResponseModel } from 'apiClient/v1'

type PayloadFailure = null
type GetCollectiveOfferTemplateAdapter = Adapter<
  number,
  GetCollectiveOfferTemplateResponseModel,
  PayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<PayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

export const getCollectiveOfferTemplateAdapter: GetCollectiveOfferTemplateAdapter =
  async (offerId) => {
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
