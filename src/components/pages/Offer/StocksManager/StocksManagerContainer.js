import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'

import withFrenchQueryRouter from 'components/hocs/withFrenchQueryRouter'
import { selectOfferById } from 'store/offers/selectors'
import { selectProductById } from 'store/selectors/data/productsSelectors'
import { selectProviderById } from 'store/selectors/data/providersSelectors'
import { selectStocksByOfferId } from 'store/selectors/data/stocksSelectors'

import StocksManager from './StocksManager'

export const mapStateToProps = (state, ownProps) => {
  const { offerId } = ownProps
  const offer = selectOfferById(state, offerId)

  if (!offer) {
    return {}
  }

  const product = selectProductById(state, get(offer, 'productId'))
  const stocks = selectStocksByOfferId(state, offerId)
  const isStockCreationAllowed = !(offer.isThing && stocks.length > 0)
  const provider = selectProviderById(state, product && product.lastProviderId)

  return {
    isEvent: offer.isEvent,
    offer,
    product,
    provider,
    isStockCreationAllowed,
    stocks,
  }
}

export default compose(withFrenchQueryRouter, connect(mapStateToProps))(StocksManager)
