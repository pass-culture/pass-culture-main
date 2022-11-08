import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { StockIdResponseModel } from 'apiClient/v1'
import { IStockEventFormValues } from 'components/StockEventForm'

import { serializeStockEventList } from './serializers'

type TSuccessPayload = { stockIds: string[] }
type TFailurePayload = { errors: Record<string, string>[] }
export type TUpdateStocksAdapter = Adapter<
  {
    offerId: string
    formValues: IStockEventFormValues[]
    departementCode: string
  },
  TSuccessPayload,
  TFailurePayload
>

const upsertStocksEventAdapter: TUpdateStocksAdapter = async ({
  offerId,
  formValues,
  departementCode,
}) => {
  try {
    const response = await api.upsertStocks({
      humanizedOfferId: offerId,
      stocks: serializeStockEventList(formValues, departementCode),
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
    let formErrors = []
    /* istanbul ignore next */
    if (isErrorAPIError(error)) {
      formErrors = error.body.map(serializeApiErrors)
    }
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la mise à jours de votre stock',
      payload: {
        errors: formErrors,
      },
    }
  }
}
export default upsertStocksEventAdapter
