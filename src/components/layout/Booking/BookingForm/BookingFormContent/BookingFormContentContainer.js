import { connect } from 'react-redux'

import BookingFormContent from './BookingFormContent'
import {
  selectIsStockDuo,
  selectStockById,
} from '../../../../../redux/selectors/data/stocksSelectors'
import { selectOfferById } from '../../../../../redux/selectors/data/offersSelectors'
import { selectSubcategory } from '../../../../../redux/selectors/data/categoriesSelectors'

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

  return {
    isDigital,
    isStockDuo,
    canExpire,
    hasActivationCode,
  }
}

export default connect(mapStateToProps)(BookingFormContent)
