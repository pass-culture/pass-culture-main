import { connect } from 'react-redux'

import BookingFormContent from './BookingFormContent'
import { selectIsStockDuo } from '../../../../../redux/selectors/data/stocksSelectors'
import { selectOfferById } from '../../../../../redux/selectors/data/offersSelectors'
import { FEATURES } from '../../../../router/selectors/features'
import selectIsFeatureEnabled from '../../../../router/selectors/selectIsFeatureEnabled'

export const mapStateToProps = (state, ownProps) => {
  const { offerId, values } = ownProps
  const { stockId } = values
  const isStockDuo = selectIsStockDuo(state, stockId, offerId)
  const offer = selectOfferById(state, offerId)
  const canExpire = offer && offer.offerType && offer.offerType.canExpire
  const isDigital = offer.isDigital
  const autoActivateDigitalBookings = selectIsFeatureEnabled(
    state,
    FEATURES.AUTO_ACTIVATE_DIGITAL_BOOKINGS
  )

  return {
    isDigital,
    isStockDuo,
    canExpire,
    autoActivateDigitalBookings,
  }
}

export default connect(mapStateToProps)(BookingFormContent)
