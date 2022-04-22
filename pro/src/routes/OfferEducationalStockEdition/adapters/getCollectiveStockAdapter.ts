import { CollectiveStockResponseModel } from 'core/OfferEducational'
import * as pcapi from 'repository/pcapi/pcapi'

type IPayloadSuccess = {
  stock: CollectiveStockResponseModel | null
}
type IPayloadFailure = { stock: null }
type GetCollectiveStockAdapter = Adapter<
  string,
  IPayloadSuccess,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: { stock: null },
}

export const getCollectiveStockAdapter: GetCollectiveStockAdapter =
  async offerId => {
    try {
      const stock = await pcapi.getCollectiveStockForOffer(offerId)
      return {
        isOk: true,
        message: '',
        // FIXME (MathildeDuboille, 25-04-22): remove id override when FF USE_NEW_COLLECTIVE_MODELS is active
        payload: { stock: { ...stock, id: stock.stockId ?? '' } },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
