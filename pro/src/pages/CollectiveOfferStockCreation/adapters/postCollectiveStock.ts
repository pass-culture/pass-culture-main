import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { CollectiveStockResponseModel } from 'apiClient/v1'
import {
  OfferEducationalStockFormValues,
  createStockDataPayload,
  hasStatusCodeAndErrorsCode,
  CollectiveOfferTemplate,
  CollectiveOffer,
} from 'core/OfferEducational'

type Params = {
  offer: CollectiveOfferTemplate | CollectiveOffer
  values: OfferEducationalStockFormValues
}

type PostCollectiveStockAdapter = Adapter<
  Params,
  CollectiveStockResponseModel,
  null
>

const KNOWN_BAD_REQUEST_CODES: Record<string, string> = {
  EDUCATIONAL_STOCK_ALREADY_EXISTS:
    "Une erreur s'est produite. Les informations date et prix existent déjà pour cette offre.",
}

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre stock.',
  payload: null,
}

const postCollectiveStockAdapter: PostCollectiveStockAdapter = async ({
  offer,
  values,
}: Params) => {
  const stockPayload = createStockDataPayload(
    values,
    offer.venue.departementCode ?? '',
    offer.id
  )
  try {
    const stock = await api.createCollectiveStock(stockPayload)
    return {
      isOk: true,
      message: null,
      payload: stock,
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
    if (isErrorAPIError(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    } else {
      return UNKNOWN_FAILING_RESPONSE
    }
  }
}

export default postCollectiveStockAdapter
