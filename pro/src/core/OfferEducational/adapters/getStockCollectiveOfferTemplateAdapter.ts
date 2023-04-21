import { api } from 'apiClient/api'

import { GetStockOfferSuccessPayload } from '../types'

type IPayloadFailure = null
type GetStockCollectiveOfferTemplateAdapter = Adapter<
  number,
  GetStockOfferSuccessPayload,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
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
