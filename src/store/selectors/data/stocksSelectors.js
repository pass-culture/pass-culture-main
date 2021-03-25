import createCachedSelector from 're-reselect'

import { selectOfferById } from '../../offers/selectors'

export const selectStocksByOfferId = createCachedSelector(
  state => state.data.stocks,
  (state, offerId) => offerId,
  selectOfferById,
  (stocks, offerId, offer) => {
    if (!stocks) {
      return []
    }
    let filteredStocks = stocks.filter(stock => stock.offerId === offerId)

    if (offer && offer.isEvent) {
      filteredStocks.sort(
        (s1, s2) => new Date(s2.beginningDatetime) - new Date(s1.beginningDatetime)
      )
    }

    return filteredStocks
  }
)((state, offerId = '') => offerId)
