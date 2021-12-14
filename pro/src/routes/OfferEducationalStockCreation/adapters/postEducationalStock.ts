import {
  createStockDataPayload,
  hasStatusCode,
  OfferEducationalStockFormValues,
  StockPayload,
} from 'core/OfferEducational'
import { Offer } from 'custom_types/offer'
import * as pcapi from 'repository/pcapi/pcapi'

type Params = { offer: Offer; values: OfferEducationalStockFormValues }

type PostEducationalStockAdapter = Adapter<Params, null, null>

const BAD_REQUEST_FAILING_RESPONSE = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre stock.',
  payload: null,
}

const postEducationalStockAdapter: PostEducationalStockAdapter = async ({
  offer,
  values,
}: Params) => {
  const stockPayload: StockPayload = createStockDataPayload(
    values,
    offer.venue.departementCode
  )
  const stockCreationPayload = { offerId: offer.id, ...stockPayload }
  try {
    await pcapi.createEducationalStock(stockCreationPayload)
    return {
      isOk: true,
      message: null,
      payload: null,
    }
  } catch (error) {
    if (hasStatusCode(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    } else {
      return UNKNOWN_FAILING_RESPONSE
    }
  }
}

export default postEducationalStockAdapter
