import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import getPriceRangeFromStocks from '../../../../../../utils/getPriceRangeFromStocks'
import { selectOfferByRouterMatch } from '../../../../../../selectors/data/offersSelectors'
import { selectStocksByOfferId } from '../../../../../../selectors/data/stocksSelectors'
import BookingAction from './BookingAction'
import { selectPastBookingByOfferId } from '../../../../../../selectors/data/bookingsSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { location, match } = ownProps
  const { pathname, search } = location

  const bookingUrl = `${pathname}/reservation${search}`

  const offer = selectOfferByRouterMatch(state, match) || {}
  const stocks = selectStocksByOfferId(state, offer.id)
  const priceRange = getPriceRangeFromStocks(stocks)

  const userPastBookingForThisOffer = selectPastBookingByOfferId(state, offer.id)

  const offerCannotBeBooked = userPastBookingForThisOffer !== null || !offer.isBookable

  return {
    bookingUrl,
    offerCannotBeBooked,
    priceRange,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookingAction)
