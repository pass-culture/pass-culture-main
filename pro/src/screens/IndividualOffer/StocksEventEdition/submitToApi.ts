import { serializeStockEventEdition } from './adapters/serializers'
import upsertStocksEventAdapter from './adapters/upsertStocksEventAdapter'
import { StockEventFormValues, StocksEventFormik } from './StockFormList/types'

export const submitToApi = async (
  allStockValues: StockEventFormValues[],
  offerId: number,
  departmentCode: string,
  setErrors: StocksEventFormik['setErrors']
) => {
  const {
    isOk,
    payload,
    message: upsertStocksMessage,
  } = await upsertStocksEventAdapter({
    offerId,
    stocks: serializeStockEventEdition(allStockValues, departmentCode),
  })
  if (!isOk) {
    setErrors({ stocks: payload.errors })
    throw new Error(upsertStocksMessage)
  }
}
