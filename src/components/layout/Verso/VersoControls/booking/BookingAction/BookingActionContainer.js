import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import getPriceRangeFromStocks from '../../../../../../utils/getPriceRangeFromStocks'
import { selectOfferById } from '../../../../../../selectors/data/offersSelectors'
import { selectStocksByOfferId } from '../../../../../../selectors/data/stocksSelectors'
import BookingAction from './BookingAction'
import { selectPassedBookingsByOfferId } from '../../../../../../selectors/data/bookingsSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { location, match } = ownProps
  const { params } = match
  const { offerId } = params
  const { pathname, search } = location

  const bookingUrl = `${pathname}/reservation${search}`

  const offer = selectOfferById(state, offerId) || {}
  const stocks = selectStocksByOfferId(state, offerId)
  const priceRange = getPriceRangeFromStocks(stocks)

  let offerCannotBeBooked = !offer.isBookable

  let userPassedBookingsForThisOffer = selectPassedBookingsByOfferId(state, offerId)

  if (userPassedBookingsForThisOffer && userPassedBookingsForThisOffer.length) {
    offerCannotBeBooked = true
  }

  return {
    bookingUrl,
    offerCannotBeBooked: offerCannotBeBooked,
    priceRange,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookingAction)
