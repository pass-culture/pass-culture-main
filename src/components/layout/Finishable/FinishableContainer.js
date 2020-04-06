import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import Finishable from './Finishable'
import getIsBooked from '../../../utils/getIsBooked'
import { selectStockById } from '../../../selectors/data/stocksSelectors'
import {
  selectBookingByRouterMatch,
  selectPastBookingByOfferId,
} from '../../../selectors/data/bookingsSelectors'
import { selectOfferById } from '../../../selectors/data/offersSelectors'

function computeShouldDisplayBanner(offer, userBookingsForThisOffer, offerIsBookedByUser) {
  const isOfferTuto = Object.keys(offer).length === 0

  let shouldDisplayFinishedBanner = false

  if (isOfferTuto) {
    shouldDisplayFinishedBanner = false
  } else if (userBookingsForThisOffer) {
    shouldDisplayFinishedBanner = true
  } else {
    shouldDisplayFinishedBanner = !offer.isBookable && !offerIsBookedByUser
  }
  return shouldDisplayFinishedBanner
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
  const userBookingsForThisOffer = selectPastBookingByOfferId(state, offerId)

  let shouldDisplayFinishedBanner = computeShouldDisplayBanner(
    offer,
    userBookingsForThisOffer,
    isBookedByCurrentUser
  )

  return {
    shouldDisplayFinishedBanner: shouldDisplayFinishedBanner,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Finishable)
