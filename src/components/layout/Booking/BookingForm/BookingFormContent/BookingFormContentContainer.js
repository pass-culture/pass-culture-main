import { connect } from 'react-redux'

import BookingFormContent from './BookingFormContent'
import { selectIsStockDuo } from '../../../../../redux/selectors/data/stocksSelectors'
import { selectOfferById } from '../../../../../redux/selectors/data/offersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { offerId, values } = ownProps
  const { stockId } = values
  const isStockDuo = selectIsStockDuo(state, stockId, offerId)
  const offer = selectOfferById(state, offerId)
  const isPressSubscription = offer.offerType.value === 'ThingType.PRESSE_ABO'
  const isDigital = offer.url !== null

  return {
    isDigital,
    isStockDuo,
    isPressSubscription,
  }
}

export default connect(mapStateToProps)(BookingFormContent)
