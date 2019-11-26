import { connect } from 'react-redux'

import BookingFormContent from './BookingFormContent'
import { selectIsStockDuo } from '../../../../../selectors/data/stocksSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { offerId, values } = ownProps
  const { stockId } = values
  const isStockDuo = selectIsStockDuo(state, stockId, offerId, 'DUO_OFFER')

  return {
    isStockDuo,
  }
}

export default connect(mapStateToProps)(BookingFormContent)
