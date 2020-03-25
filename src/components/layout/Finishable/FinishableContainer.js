import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import Finishable from './Finishable'
import getIsBooked from '../../../utils/getIsBooked'
import { selectStockById } from '../../../selectors/data/stocksSelectors'
import { selectBookingByRouterMatch } from '../../../selectors/data/bookingsSelectors'
import { selectOfferById } from '../../../selectors/data/offersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { bookingId, offerId: offerIdQueryParam } = params
  const booking = selectBookingByRouterMatch(state, match)
  const isBookedByCurrentUser = getIsBooked(booking)
  let offerId = offerIdQueryParam

  if (bookingId) {
    const { stockId } = booking
    const stock = selectStockById(state, stockId)
    const { offerId: offerIdFromStock } = stock
    offerId = offerIdFromStock
  }

  const offer = selectOfferById(state, offerId) || {}
  const isOfferTuto = Object.keys(offer).length === 0
  const isOfferBookableOrBooked = offer.isBookable || isBookedByCurrentUser

  return {
    offerCanBeOrIsBooked: isOfferTuto ? true : isOfferBookableOrBooked,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Finishable)
