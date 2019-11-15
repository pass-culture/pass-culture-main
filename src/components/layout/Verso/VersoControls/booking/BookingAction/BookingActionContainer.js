import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import BookingAction from './BookingAction'
import getPriceRangeFromStocks from '../../../../../../helpers/getPriceRangeFromStocks'
import { selectOfferByRouterMatch } from '../../../../../../selectors/data/offersSelectors'
import { selectStocksByOfferId } from '../../../../../../selectors/data/stocksSelectors'
import { selectIsNotBookableByRouterMatch } from '../../../../../../selectors/data/bookablesSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { match, location } = ownProps
  const { pathname, search } = location

  const bookingUrl = `${pathname}/reservation${search}`
  const isNotBookable = selectIsNotBookableByRouterMatch(state, match)
  const offer = selectOfferByRouterMatch(state, match) || {}
  const stocks = selectStocksByOfferId(state, offer.id)
  const priceRange = getPriceRangeFromStocks(stocks)

  return {
    bookingUrl,
    isNotBookable,
    priceRange,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookingAction)
