import * as pcapi from 'repository/pcapi/pcapi'

import {
  GetStockOfferSuccessPayload,
  OfferEducationalStockFormValues,
  StockPayload,
  createStockDataPayload,
  hasStatusCode,
  hasStatusCodeAndErrorsCode,
} from 'core/OfferEducational'

type Params = {
  offer: GetStockOfferSuccessPayload
  values: OfferEducationalStockFormValues
  enableIndividualAndCollectiveSeparation: boolean
}

type PostEducationalStockAdapter = Adapter<Params, null, null>

const KNOWN_BAD_REQUEST_CODES: Record<string, string> = {
  EDUCATIONAL_STOCK_ALREADY_EXISTS:
    "Une erreur s'est produite. Les informations date et prix existent déjà pour cette offre.",
}

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
  enableIndividualAndCollectiveSeparation,
}: Params) => {
  const stockPayload: StockPayload = createStockDataPayload(
    values,
    offer.venueDepartmentCode
  )
  const offerId = enableIndividualAndCollectiveSeparation
    ? offer.offerId
    : offer.id

  const stockCreationPayload = { offerId: offerId, ...stockPayload }
  try {
    await pcapi.createEducationalStock(stockCreationPayload)
    return {
      isOk: true,
      message: null,
      payload: null,
    }
  } catch (error) {
    if (hasStatusCodeAndErrorsCode(error) && error.status === 400) {
      if (error.errors.code in KNOWN_BAD_REQUEST_CODES) {
        return {
          ...BAD_REQUEST_FAILING_RESPONSE,
          message: KNOWN_BAD_REQUEST_CODES[error.errors.code],
        }
      }
    }
    if (hasStatusCode(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    } else {
      return UNKNOWN_FAILING_RESPONSE
    }
  }
}

export default postEducationalStockAdapter
