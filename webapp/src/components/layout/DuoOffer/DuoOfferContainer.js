import { connect } from 'react-redux'

import DuoOffer from './DuoOffer'
import { selectIsEnoughStockForOfferDuo } from '../../../redux/selectors/data/stocksSelectors'
import { selectOfferById } from '../../../redux/selectors/data/offersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { offerId } = ownProps
  const isEnoughStockForDuo = selectIsEnoughStockForOfferDuo(state, offerId)
  const offer = selectOfferById(state, offerId)
  const { isDuo } = offer
  const isDuoOffer = isEnoughStockForDuo && isDuo

  return {
    isDuoOffer,
  }
}

export default connect(mapStateToProps)(DuoOffer)
