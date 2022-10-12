import { api, serializeApiErrors } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { StockIdResponseModel } from 'apiClient/v1'
import { IStockThingFormValues } from 'new_components/StockThingForm'

import { serializeStockThingList } from './serializers'

type TSuccessPayload = { stockIds: string[] }
type TFailurePayload = { errors: Record<string, string> }
export type TUpdateStocksAdapter = Adapter<
  {
    offerId: string
    formValues: IStockThingFormValues
    departementCode: string
  },
  TSuccessPayload,
  TFailurePayload
>

const upsertStocksThingAdapter: TUpdateStocksAdapter = async ({
  offerId,
  formValues,
  departementCode,
}) => {
  try {
    const response = await api.upsertStocks({
      humanizedOfferId: offerId,
      stocks: serializeStockThingList(formValues, departementCode),
    })
    return {
      isOk: true,
      message: 'Vos modifications ont bien été prises en compte',
      payload: {
        stockIds: response.stockIds.map(
          (stock: StockIdResponseModel) => stock.id
        ),
      },
    }
  } catch (error) {
    let formErrors = {}
    if (isErrorAPIError(error)) {
      formErrors = error.body
    }
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la mise à jours de votre stock',
      payload: {
        errors: serializeApiErrors(formErrors),
      },
    }
  }
}
export default upsertStocksThingAdapter
