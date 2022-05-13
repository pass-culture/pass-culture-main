import * as pcapi from 'repository/pcapi/pcapi'

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
      const offer = await pcapi.getCollectiveOffer(offerId)

      const isBooked = offer?.collectiveStock?.isBooked

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
          isEducational: true,
          isShowcase: false,
          offerId: offer.offerId,
        },
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }
