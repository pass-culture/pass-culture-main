import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import Finishable from './Finishable'
import getIsBooked from '../../../utils/getIsBooked'
import { selectStockById } from '../../../redux/selectors/data/stocksSelectors'
import {
  selectBookingByRouterMatch,
  selectPastEventBookingByOfferId,
} from '../../../redux/selectors/data/bookingsSelectors'
import { selectOfferById } from '../../../redux/selectors/data/offersSelectors'

function computeShouldDisplayFinishedBanner(offer, userBookingsForThisOffer, offerIsBookedByUser) {
  if (userBookingsForThisOffer) {
    return true
  } else {
    return !offer.isBookable && !offerIsBookedByUser
  }
}

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
  const userPastBookingForThisOffer = selectPastEventBookingByOfferId(state, offerId)
  const shouldDisplayFinishedBanner = computeShouldDisplayFinishedBanner(
    offer,
    userPastBookingForThisOffer,
    isBookedByCurrentUser
  )

  return { shouldDisplayFinishedBanner }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Finishable)
