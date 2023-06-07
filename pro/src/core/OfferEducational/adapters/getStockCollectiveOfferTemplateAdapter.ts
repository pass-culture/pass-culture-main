import { api } from 'apiClient/api'

import { GetStockOfferSuccessPayload } from '../'

type PayloadFailure = null
type GetStockCollectiveOfferTemplateAdapter = Adapter<
  number,
  GetStockOfferSuccessPayload,
  PayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<PayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

export const getStockCollectiveOfferTemplateAdapter: GetStockCollectiveOfferTemplateAdapter =
  async offerId => {
    try {
      const offer = await api.getCollectiveOfferTemplate(offerId)

      return {
        isOk: true,
        message: '',
        payload: {
          id: offer.id,
          managingOffererId: offer.venue.managingOffererId,
          isActive: offer.isActive,
          status: offer.status,
          venueDepartmentCode: offer.venue.departementCode ?? '',
          isCancellable: false,
          isBooked: false,
          isEducational: true,
          isShowcase: true,
          offerId: offer.offerId,
          name: offer.name,
        },
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }
