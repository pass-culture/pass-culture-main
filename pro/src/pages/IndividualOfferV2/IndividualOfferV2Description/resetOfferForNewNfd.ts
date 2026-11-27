import { api } from '@/apiClient/api'
import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'

// Removes the data that the PATCH endpoint cannot reset (stocks and image)
// before applying a new nature/format to an existing offer.
export const resetOfferForNewNfd = async (
  offer: GetIndividualOfferResponseModelV2
): Promise<void> => {
  if (offer.hasStocks) {
    const { totalStockCount } = await api.getStocks({
      path: { offer_id: offer.id },
    })
    const { stocks } = await api.getStocks({
      path: { offer_id: offer.id },
      query: { stocks_limit_per_page: totalStockCount },
    })
    if (stocks.length > 0) {
      await api.deleteStocks({
        path: { offer_id: offer.id },
        body: { ids_to_delete: stocks.map((stock) => stock.id) },
      })
    }
  }

  if (offer.activeMediation?.thumbUrl || offer.thumbUrl) {
    await api.deleteThumbnail({ path: { offer_id: offer.id } })
  }
}
