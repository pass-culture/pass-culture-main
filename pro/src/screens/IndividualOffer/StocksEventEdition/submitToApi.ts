import { GetOfferStockResponseModel } from 'apiClient/v1'

import { serializeStockEventEdition } from './adapters/serializers'
import upsertStocksEventAdapter from './adapters/upsertStocksEventAdapter'
import { StockEventFormValues, StocksEventFormik } from './StockFormList/types'

type SubmitToApi = {
  editedStocks: StockEventFormValues[]
  offerId: number
  departmentCode: string
  setErrors: StocksEventFormik['setErrors']
}

export const submitToApi = async ({
  editedStocks,
  offerId,
  departmentCode,
  setErrors,
}: SubmitToApi): Promise<GetOfferStockResponseModel[]> => {
  const {
    isOk,
    payload,
    message: upsertStocksMessage,
  } = await upsertStocksEventAdapter({
    offerId,
    stocks: serializeStockEventEdition(editedStocks, departmentCode),
  })
  if (!isOk) {
    setErrors({ stocks: payload.errors })
    throw new Error(upsertStocksMessage)
  }

  return payload.stocks
}
