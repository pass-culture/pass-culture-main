import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { StockResponseModel } from 'apiClient/v1'

import { StockThingFormValues } from '../types'

import { serializeStockThingList } from './serializers'

type SuccessPayload = { stockIds: number[] }
type FailurePayload = { errors: Record<string, string> }
type UpdateStocksAdapter = Adapter<
  {
    offerId: number
    values: StockThingFormValues
    departementCode: string
  },
  SuccessPayload,
  FailurePayload
>

const upsertStocksThingAdapter: UpdateStocksAdapter = async ({
  offerId,
  values,
  departementCode,
}) => {
  try {
    const response = await api.upsertStocks({
      offerId: offerId,
      stocks: serializeStockThingList(values, departementCode),
    })
    return {
      isOk: true,
      message: 'OK',
      payload: {
        stockIds: response.stocks.map((stock: StockResponseModel) => stock.id),
      },
    }
  } catch (error) {
    let formErrors = {}
    /* istanbul ignore next */
    if (isErrorAPIError(error)) {
      formErrors = error.body
    }
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la mise à jour de votre stock',
      payload: {
        errors: serializeApiErrors(formErrors),
      },
    }
  }
}
export default upsertStocksThingAdapter
