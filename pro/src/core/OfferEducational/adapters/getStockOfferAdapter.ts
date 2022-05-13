import * as pcapi from 'repository/pcapi/pcapi'

import { GetStockOfferSuccessPayload } from '../types'
import { Offer } from 'custom_types/offer'

type IPayloadFailure = null
type GetOfferAdapter = Adapter<
  string,
  GetStockOfferSuccessPayload,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

export const getStockOfferAdapter: GetOfferAdapter = async offerId => {
  try {
    const offer = (await pcapi.loadOffer(offerId)) as Offer

    /* @debt bugRisk "Gaël: we can't be sure this way that the stock is really booked, it can also be USED"*/
    const isBooked = offer?.stocks[0]?.bookingsQuantity > 0

    return {
      isOk: true,
      message: '',
      payload: {
        id: offer.id,
        managingOffererId: offer.venue.managingOffererId,
        isActive: offer.isActive,
        status: offer.status,
        venueDepartmentCode: offer.venue.departementCode,
        isBooked,
        isEducational: offer.isEducational,
        isShowcase: Boolean(offer.extraData?.isShowcase),
      },
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}
