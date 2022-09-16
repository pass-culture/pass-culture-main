import { api } from 'apiClient/api'

import { GetCollectiveOfferTemplateSuccessPayload } from '../types'

type IPayloadFailure = null
type GetCollectiveOfferTemplateAdapter = Adapter<
  string,
  GetCollectiveOfferTemplateSuccessPayload,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

export const getCollectiveOfferTemplateAdapter: GetCollectiveOfferTemplateAdapter =
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
          isBooked: false,
          isCancellable: true,
          isEducational: true,
          isShowcase: true,
          offerId: offer.offerId,
          educationalPriceDetails: offer.educationalPriceDetail,
        },
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }
