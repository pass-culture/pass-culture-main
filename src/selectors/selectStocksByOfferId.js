import moment from 'moment'
import createCachedSelector from 're-reselect'

import selectOfferById from './selectOfferById'

function mapArgsToCacheKey(state, offerId) {
  return offerId || ''
}

export const selectStocksByOfferId = createCachedSelector(
  state => state.data.stocks,
  (state, offerId) => offerId,
  selectOfferById,
  (stocks, offerId, offer) => {
    let filteredStocks = stocks.filter(stock => stock.offerId === offerId)

    if (offer && offer.eventId) {
      filteredStocks.sort(
        (s1, s2) =>
          moment(s2.beginningDatetime).unix() -
          moment(s1.beginningDatetime).unix()
      )
    }

    return filteredStocks
  }
)(mapArgsToCacheKey)

export default selectStocksByOfferId
