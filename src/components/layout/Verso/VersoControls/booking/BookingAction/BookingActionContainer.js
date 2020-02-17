import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import getPriceRangeFromStocks from '../../../../../../utils/getPriceRangeFromStocks'
import { selectOfferById } from '../../../../../../selectors/data/offersSelectors'
import { selectStocksByOfferId } from '../../../../../../selectors/data/stocksSelectors'
import BookingAction from './BookingAction'

export const mapStateToProps = (state, ownProps) => {
  const { location, match } = ownProps
  const { params } = match
  const { offerId } = params
  const { pathname, search } = location

  const bookingUrl = `${pathname}/reservation${search}`
  const offer = selectOfferById(state, offerId) || {}
  let offerIsNoLongerBookable = offer.isNotBookable || offer.isFullyBooked
  const stocks = selectStocksByOfferId(state, offerId)
  const priceRange = getPriceRangeFromStocks(stocks)

  return {
    bookingUrl,
    isNotBookable: offerIsNoLongerBookable,
    priceRange,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookingAction)
