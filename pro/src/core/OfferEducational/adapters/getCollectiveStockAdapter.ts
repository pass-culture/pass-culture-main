import { CollectiveStockResponseModel } from 'apiClient/v1'
import { api } from 'apiClient/api'

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
  message: 'Nous avons rencontré un problème lors du chargemement des données',
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
