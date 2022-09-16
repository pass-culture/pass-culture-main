import { api } from 'apiClient/api'

import { GetStockOfferSuccessPayload } from '../types'

type IPayloadFailure = null
type GetStockCollectiveOfferAdapter = Adapter<
  string,
  GetStockOfferSuccessPayload,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

export const getStockCollectiveOfferAdapter: GetStockCollectiveOfferAdapter =
  async offerId => {
    try {
      const offer = await api.getCollectiveOffer(offerId)

      const isBooked = Boolean(offer?.collectiveStock?.isBooked)

      return {
        isOk: true,
        message: '',
        payload: {
          id: offer.id,
          managingOffererId: offer.venue.managingOffererId,
          isActive: offer.isActive,
          status: offer.status,
          venueDepartmentCode: offer.venue.departementCode ?? '',
          isBooked,
          isCancellable: offer.isCancellable,
          isEducational: true,
          isShowcase: false,
          offerId: offer.offerId,
          institution: offer.institution,
        },
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }
