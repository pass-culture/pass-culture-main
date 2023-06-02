import { api } from 'apiClient/api'
import { CollectiveStockResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

type PayloadSuccess = {
  stock: CollectiveStockResponseModel | null
}
type PayloadFailure = { stock: null }
type GetCollectiveStockAdapter = Adapter<
  { offerId: string },
  PayloadSuccess,
  PayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<PayloadFailure> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: { stock: null },
}

export const getCollectiveStockAdapter: GetCollectiveStockAdapter = async ({
  offerId,
}) => {
  try {
    const stock = await api.getCollectiveStock(offerId)
    return {
      isOk: true,
      message: '',
      payload: {
        stock,
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}
