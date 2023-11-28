import { api } from 'apiClient/api'
import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'

type SuccessPayload = number
type FailurePayload = { errors: string }
type UpdateStocksAdapter = Adapter<
  {
    offerId: number
    stocks: Array<StockCreationBodyModel | StockEditionBodyModel>
  },
  SuccessPayload,
  FailurePayload
>

const upsertStocksEventAdapter: UpdateStocksAdapter = async ({
  offerId,
  stocks,
}) => {
  try {
    const response = await api.upsertStocks({
      offerId: offerId,
      stocks,
    })
    return {
      isOk: true,
      message: 'Vos modifications ont bien été prises en compte',
      payload: response.stocks_count,
    }
  } catch (error) {
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la mise à jour de votre stock',
      payload: {
        errors: '',
      },
    }
  }
}
export default upsertStocksEventAdapter
