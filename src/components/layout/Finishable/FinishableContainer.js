import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import Finishable from './Finishable'
import { selectStockById } from '../../../selectors/data/stocksSelectors'
import { selectBookingById } from '../../../selectors/data/bookingsSelectors'
import { selectOfferById } from '../../../selectors/data/offersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { isBooked, match } = ownProps
  const { params } = match
  const { bookingId, offerId: offerIdQueryParam } = params

  let offerId = offerIdQueryParam
  if (bookingId) {
    const booking = selectBookingById(state, bookingId)
    const { stockId } = booking
    const stock = selectStockById(state, stockId)
    const { offerId: offerIdFromStock } = stock
    offerId = offerIdFromStock
  }
  const offer = selectOfferById(state, offerId) || {}

  let offerIsNoLongerBookable = false
  if (!isBooked) {
    offerIsNoLongerBookable = offer.isNotBookable || offer.isFullyBooked
  }

  return {
    offerIsNoLongerBookable,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Finishable)
