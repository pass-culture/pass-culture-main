import { api } from 'apiClient/api'

import { serializeStockEventEdition } from './adapters/serializers'
import { StockEventFormValues, StocksEventFormik } from './StockFormList/types'

export const submitToApi = async (
  allStockValues: StockEventFormValues[],
  offerId: number,
  departmentCode: string,
  setErrors: StocksEventFormik['setErrors']
) => {
  try {
    await api.upsertStocks({
      offerId: offerId,
      stocks: serializeStockEventEdition(allStockValues, departmentCode),
    })
  } catch (error) {
    setErrors({ stocks: '' })
    throw new Error(
      'Une erreur est survenue lors de la mise à jour de votre stock'
    )
  }
}
