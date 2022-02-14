import {
  createStockDataPayload,
  GetStockOfferSuccessPayload,
  hasStatusCode,
  OfferEducationalStockFormValues,
  StockPayload,
} from 'core/OfferEducational'
import * as pcapi from 'repository/pcapi/pcapi'

import { StockResponse } from '../types'

type Params = {
  offer: GetStockOfferSuccessPayload
  stockId: string
  values: OfferEducationalStockFormValues
}

type PatchShadowStockIntoEducationalStockAdapter = Adapter<
  Params,
  StockResponse,
  null
>

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la mise à jour de votre stock.',
  payload: null,
}

const patchShadowStockIntoEducationalStockAdapter: PatchShadowStockIntoEducationalStockAdapter =
  async ({ offer, stockId, values }: Params) => {
    // We send the whole stock to create a new one in db
    const patchStockPayload: StockPayload = createStockDataPayload(
      values,
      offer.venueDepartmentCode
    )

    try {
      const stock = (await pcapi.transformShadowStockIntoEducationalStock(
        stockId,
        { ...patchStockPayload, offerId: offer.id }
      )) as StockResponse
      return {
        isOk: true,
        message: 'Le détail de votre stock a bien été modifié.',
        payload: stock,
      }
    } catch (error) {
      if (hasStatusCode(error) && error.status === 400) {
        return BAD_REQUEST_FAILING_RESPONSE
      } else {
        return UNKNOWN_FAILING_RESPONSE
      }
    }
  }

export default patchShadowStockIntoEducationalStockAdapter
