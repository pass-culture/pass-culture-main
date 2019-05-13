import get from 'lodash.get'

import selectOfferById from 'selectors/selectOfferById'
import selectProductById from 'selectors/selectProductById'
import selectProviderById from 'selectors/selectProviderById'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'

function mapStateToProps(state, ownProps) {
  const {
    match: {
      params: { offerId },
    },
  } = ownProps

  const offer = selectOfferById(state, offerId)

  if (!offer) {
    return {}
  }

  const product = selectProductById(state, get(offer, 'productId'))
  const stocks = selectStocksByOfferId(state, offerId)
  const shouldPreventCreationOfSecondStock = offer.isThing && stocks.length > 0
  const provider = selectProviderById(state, product && product.lastProviderId)

  return {
    isEvent: offer.isEvent,
    offer,
    product,
    provider,
    shouldPreventCreationOfSecondStock,
    stocks,
  }
}

export default mapStateToProps
