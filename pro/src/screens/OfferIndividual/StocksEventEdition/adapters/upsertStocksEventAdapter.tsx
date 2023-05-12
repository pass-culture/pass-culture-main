import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import {
  StockIdResponseModel,
  StockCreationBodyModel,
  StockEditionBodyModel,
} from 'apiClient/v1'

type TSuccessPayload = { stockIds: string[] }
type TFailurePayload = { errors: Record<string, string>[] }
type TUpdateStocksAdapter = Adapter<
  {
    offerId: number
    stocks: Array<StockCreationBodyModel | StockEditionBodyModel>
  },
  TSuccessPayload,
  TFailurePayload
>

const upsertStocksEventAdapter: TUpdateStocksAdapter = async ({
  offerId,
  stocks,
}) => {
  try {
    const response = await api.upsertStocks({
      offerId: offerId,
      stocks: stocks,
    })
    return {
      isOk: true,
      message: 'Vos modifications ont bien été prises en compte',
      payload: {
        stockIds: response.stocks.map(
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
      message: 'Une erreur est survenue lors de la mise à jour de votre stock',
      payload: {
        errors: formErrors,
      },
    }
  }
}
export default upsertStocksEventAdapter
