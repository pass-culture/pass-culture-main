import { connect } from 'react-redux'

import BookingFormContent from './BookingFormContent'
import {
  selectIsStockDuo,
  selectStockById,
} from '../../../../../redux/selectors/data/stocksSelectors'
import { selectOfferById } from '../../../../../redux/selectors/data/offersSelectors'
import { FEATURES } from '../../../../router/selectors/features'
import selectIsFeatureEnabled from '../../../../router/selectors/selectIsFeatureEnabled'

export const mapStateToProps = (state, ownProps) => {
  const { offerId, values } = ownProps
  const { stockId } = values
  const isStockDuo = selectIsStockDuo(state, stockId, offerId)
  const offer = selectOfferById(state, offerId)
  const stock = selectStockById(state, stockId)
  const hasActivationCode = !!(stock && stock.hasActivationCode)
  const canExpire = offer && offer.offerType && offer.offerType.canExpire
  const isDigital = offer.isDigital
  const autoActivateDigitalBookings = selectIsFeatureEnabled(
    state,
    FEATURES.AUTO_ACTIVATE_DIGITAL_BOOKINGS
  )
  const enableActivationCodes = selectIsFeatureEnabled(state, FEATURES.ENABLE_ACTIVATION_CODES)

  return {
    isDigital,
    isStockDuo,
    canExpire,
    autoActivateDigitalBookings,
    enableActivationCodes,
    hasActivationCode,
  }
}

export default connect(mapStateToProps)(BookingFormContent)
