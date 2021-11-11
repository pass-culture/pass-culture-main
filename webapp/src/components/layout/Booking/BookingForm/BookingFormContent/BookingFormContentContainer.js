import { connect } from 'react-redux'

import BookingFormContent from './BookingFormContent'
import {
  selectIsStockDuo,
  selectStockById,
} from '../../../../../redux/selectors/data/stocksSelectors'
import { selectOfferById } from '../../../../../redux/selectors/data/offersSelectors'
import { selectSubcategory } from '../../../../../redux/selectors/data/categoriesSelectors'
import selectIsFeatureDisabled from '../../../../router/selectors/selectIsFeatureDisabled'
import { FEATURES } from '../../../../router/selectors/features'

const LIVRE_PAPIER_SUBCATEGORY_ID = 'LIVRE_PAPIER'

export const mapStateToProps = (state, ownProps) => {
  const { offerId, values } = ownProps
  const { stockId } = values
  const isStockDuo = selectIsStockDuo(state, stockId, offerId)
  const offer = selectOfferById(state, offerId)
  const stock = selectStockById(state, stockId)
  const hasActivationCode = !!(stock && stock.hasActivationCode)
  const subcategory = selectSubcategory(state, offer)
  const canExpire = subcategory.canExpire
  const isDigital = offer.isDigital
  const isLivrePapier = subcategory.id === LIVRE_PAPIER_SUBCATEGORY_ID
  const isNewAutoExpiryDelayBooksBookingEnabled = !selectIsFeatureDisabled(
    state,
    FEATURES.ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS
  )

  return {
    isDigital,
    isLivrePapier,
    isNewAutoExpiryDelayBooksBookingEnabled,
    isStockDuo,
    canExpire,
    hasActivationCode,
  }
}

export default connect(mapStateToProps)(BookingFormContent)
