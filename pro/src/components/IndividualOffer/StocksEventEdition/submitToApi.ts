import { api } from 'apiClient/api'

import { serializeStockEventEdition } from './serializers'
import { StockEventFormValues } from './types'

export const submitToApi = async (
  allStockValues: StockEventFormValues[],
  offerId: number,
  departmentCode: string
) => {
  try {
    await api.bulkUpdateEventStocks({
      offerId,
      stocks: serializeStockEventEdition(allStockValues, departmentCode),
    })
  } catch {
    throw new Error(
      'Une erreur est survenue lors de la mise à jour de votre stock'
    )
  }
}
