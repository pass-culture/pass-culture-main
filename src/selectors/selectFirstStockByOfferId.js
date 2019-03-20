import createCachedSelector from 're-reselect'

import selectStocksByOfferId from './selectStocksByOfferId'

function mapArgsToKey(state, offerId) {
  return offerId || ''
}

export const selectFirstStockByOfferId = createCachedSelector(
  selectStocksByOfferId,
  stocks => stocks && stocks[0]
)(mapArgsToKey)

export default selectFirstStockByOfferId
