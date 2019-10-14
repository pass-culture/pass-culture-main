import { connect } from 'react-redux'

import DuoOffer from './DuoOffer'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import { selectIsEnoughStockForOfferDuo } from '../../../selectors/data/stocksSelector'
import selectOfferById from '../../../selectors/selectOfferById'

export const mapStateToProps = (state, ownProps) => {
  const { offerId } = ownProps
  const isFeatureDisabled = selectIsFeatureDisabled(state, 'DUO_OFFER')
  const isEnoughStockForDuo = selectIsEnoughStockForOfferDuo(state, offerId)
  const offer = selectOfferById(state, offerId)
  const { isDuo } = offer
  const isDuoOffer = !isFeatureDisabled && isEnoughStockForDuo && isDuo

  return {
    isDuoOffer,
  }
}

export default connect(mapStateToProps)(DuoOffer)
