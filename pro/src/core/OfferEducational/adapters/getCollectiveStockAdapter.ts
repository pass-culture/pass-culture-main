import { api } from 'apiClient/api'
import { CollectiveStockResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

export type IPayloadSuccess = {
  stock: CollectiveStockResponseModel | null
}
export type IPayloadFailure = { stock: null }
type GetCollectiveStockAdapter = Adapter<
  { offerId: string },
  IPayloadSuccess,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
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
