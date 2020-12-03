import { connect } from 'react-redux'

import BookingFormContent from './BookingFormContent'
import { selectIsStockDuo } from '../../../../../redux/selectors/data/stocksSelectors'
import { selectOfferById } from '../../../../../redux/selectors/data/offersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { offerId, values } = ownProps
  const { stockId } = values
  const isStockDuo = selectIsStockDuo(state, stockId, offerId)
  const offer = selectOfferById(state, offerId)
  const canExpire = offer.offerType.canExpire
  const isDigital = offer.isDigital

  return {
    isDigital,
    isStockDuo,
    canExpire,
  }
}

export default connect(mapStateToProps)(BookingFormContent)
