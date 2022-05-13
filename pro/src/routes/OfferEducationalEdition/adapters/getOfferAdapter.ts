import * as pcapi from 'repository/pcapi/pcapi'

import { Offer } from 'custom_types/offer'

type IPayloadFailure = null
type GetOfferAdapter = Adapter<string, Offer, IPayloadFailure>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la récupération de votre offre',
  payload: null,
}

const getOfferAdapter: GetOfferAdapter = async offerId => {
  try {
    const offer = (await pcapi.loadOffer(offerId)) as Offer
    /* @debt bugRisk "Gaël: we can't be sure this way that the stock is really booked, it can also be USED"*/
    const isBooked = offer?.stocks[0]?.bookingsQuantity > 0

    return {
      isOk: true,
      message: '',
      payload: { ...offer, isBooked },
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getOfferAdapter
