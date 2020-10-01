import { connect } from 'react-redux'
import { compose } from 'redux'
import get from 'lodash.get'

import StocksManager from './StocksManager'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'
import { selectProductById } from 'store/selectors/data/productsSelectors'
import { selectStocksByOfferId } from 'store/selectors/data/stocksSelectors'
import { selectProviderById } from 'store/selectors/data/providersSelectors'
import { selectOfferById } from 'store/selectors/data/offersSelectors'

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
