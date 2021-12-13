import { hasStatusCode } from 'core/OfferEducational/utils'
import { OfferEducationalStockFormValues } from 'core/OfferEducationalStock/types'
import { createStockDataPayload } from 'core/OfferEducationalStock/utils/createStockDataPayload'
import { Offer } from 'custom_types/offer'
import * as pcapi from 'repository/pcapi/pcapi'
import { StockPayload as StockPayload } from 'routes/OfferEducationalStockCreation/types'

type Params = {
  offer: Offer
  stockId?: string
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
  message: 'Une erreur est survenue lors de la création de votre stock.',
  payload: null,
}

const patchEducationalStockAdapter: PatchEducationalStockAdapter = async ({
  offer,
  stockId,
  values,
}: Params) => {
  if (stockId) {
    const stockPayload: StockPayload = createStockDataPayload(
      values,
      offer.venue.departementCode
    )
    try {
      await pcapi.editEducationalStock(stockId, stockPayload)
      return {
        isOk: true,
        message: 'Le détail de votre offre a bien été modifié.', // voir wording avec ux
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
  return BAD_REQUEST_FAILING_RESPONSE
}

export default patchEducationalStockAdapter
