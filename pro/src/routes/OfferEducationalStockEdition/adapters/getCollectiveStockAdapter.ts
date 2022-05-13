import { CollectiveStockResponseModel } from 'core/OfferEducational'
import * as pcapi from 'repository/pcapi/pcapi'

type IPayloadSuccess = {
  stock: CollectiveStockResponseModel | null
}
type IPayloadFailure = { stock: null }
type GetCollectiveStockAdapter = Adapter<
  { offerId: string; isNewCollectiveModelEnabled: boolean },
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
  isNewCollectiveModelEnabled,
}) => {
  try {
    const stock = await pcapi.getCollectiveStockForOffer(offerId)
    return {
      isOk: true,
      message: '',
      payload: {
        stock: {
          ...stock,
          id: isNewCollectiveModelEnabled ? stock.id : stock.stockId ?? '',
        },
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}
