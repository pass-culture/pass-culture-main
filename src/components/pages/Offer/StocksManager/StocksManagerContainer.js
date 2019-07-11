import { connect } from 'react-redux'
import { compose } from 'redux'
import get from 'lodash.get'

import StocksManager from './StocksManager'
import { withFrenchQueryRouter } from '../../../hocs'
import selectOfferById from '../../../../selectors/selectOfferById'
import selectProductById from '../../../../selectors/selectProductById'
import selectProviderById from '../../../../selectors/selectProviderById'
import selectStocksByOfferId from '../../../../selectors/selectStocksByOfferId'

export const mapStateToProps = (state, ownProps) => {
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
  const creationOfSecondStockIsPrevented = offer.isThing && stocks.length > 0
  const provider = selectProviderById(state, product && product.lastProviderId)

  return {
    isEvent: offer.isEvent,
    offer,
    product,
    provider,
    creationOfSecondStockIsPrevented,
    stocks,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(StocksManager)
