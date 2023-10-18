import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'

import { StockThingFormValues } from '../types'

import { serializeStockThingList } from './serializers'

type SuccessPayload = object
type FailurePayload = { errors: Record<string, string> }
type UpdateStocksAdapter = Adapter<
  {
    offerId: number
    values: StockThingFormValues
    departementCode?: string | null
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
    await api.upsertStocks({
      offerId: offerId,
      stocks: serializeStockThingList(values, departementCode),
    })
    return {
      isOk: true,
      message: 'OK',
      payload: {},
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
