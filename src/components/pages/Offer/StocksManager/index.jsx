import { connect } from 'react-redux'
import { compose } from 'redux'

import RawStocksManager from './RawStocksManager'
import { withFrenchQueryRouter } from 'components/hocs'
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

  const { productId } = offer
  const product = selectProductById(state, productId)
  const { durationMinutes } = product || {}

  const stocks = selectStocksByOfferId(state, offerId)

  const isEventStock = typeof durationMinutes !== 'undefined'

  const shouldPreventCreationOfSecondStock = !isEventStock && stocks.length > 0

  const provider = selectProviderById(state, product && product.lastProviderId)

  return {
    isEventStock,
    offer,
    product,
    provider,
    shouldPreventCreationOfSecondStock,
    stocks,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(RawStocksManager)
