import { hasStatusCode } from 'core/OfferEducational/utils'
import {
  OfferEducationalStockFormValues,
  StockPayload,
} from 'core/OfferEducationalStock/types'
import { createStockDataPayload } from 'core/OfferEducationalStock/utils/createStockDataPayload'
import { Offer } from 'custom_types/offer'
import * as pcapi from 'repository/pcapi/pcapi'

type Params = {
  offer: Offer
  stockId: string
  values: OfferEducationalStockFormValues
}

type PatchEducationalStockAdapter = Adapter<Params, null, null>

const BAD_REQUEST_FAILING_RESPONSE = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE = {
  isOk: false,
  message: 'Une erreur est survenue lors de la mise à jour de votre stock.',
  payload: null,
}

const patchEducationalStockAdapter: PatchEducationalStockAdapter = async ({
  offer,
  stockId,
  values,
}: Params) => {
  const stockPayload: StockPayload = createStockDataPayload(
    values,
    offer.venue.departementCode
  )
  try {
    await pcapi.editEducationalStock(stockId, stockPayload)
    return {
      isOk: true,
      message: 'Le détail de votre stock a bien été modifié.',
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

export default patchEducationalStockAdapter
