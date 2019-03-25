import createCachedSelector from 're-reselect'

import selectStocksByOfferId from './selectStocksByOfferId'

function mapArgsToCacheKey(state, offerId) {
  return offerId || ''
}

export const selectFirstStockByOfferId = createCachedSelector(
  selectStocksByOfferId,
  stocks => stocks && stocks[0]
)(mapArgsToCacheKey)

export default selectFirstStockByOfferId
