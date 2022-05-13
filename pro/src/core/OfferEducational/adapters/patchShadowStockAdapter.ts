import * as pcapi from 'repository/pcapi/pcapi'

import {
  OfferEducationalStockFormValues,
  StockPayload,
  hasStatusCode,
} from 'core/OfferEducational'

import { StockResponse } from '../types'

type Params = {
  stockId: string
  values: OfferEducationalStockFormValues
  initialValues: OfferEducationalStockFormValues
}

type PatchShadowStockAdapter = Adapter<Params, StockResponse, null>

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

export const patchShadowStockAdapter: PatchShadowStockAdapter = async ({
  stockId,
  values,
  initialValues,
}: Params) => {
  const patchStockPayload: Partial<StockPayload> =
    values.priceDetail !== initialValues.priceDetail
      ? {
          educationalPriceDetail: values.priceDetail,
        }
      : {}

  try {
    const stock = (await pcapi.editShadowStock(
      stockId,
      patchStockPayload
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
