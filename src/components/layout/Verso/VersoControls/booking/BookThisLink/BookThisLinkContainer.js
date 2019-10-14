import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import BookThisLink from './BookThisLink'
import getPriceRangeFromStocks from '../../../../../../helpers/getPriceRangeFromStocks'
import selectIsNotBookableByRouterMatch from '../../../../../../selectors/selectIsNotBookableByRouterMatch'
import selectOfferByRouterMatch from '../../../../../../selectors/selectOfferByRouterMatch'
import selectStocksByOfferId from '../../../../../../selectors/selectStocksByOfferId'

const getDestinationLink = (params, url, search = '') => {
  if (params.bookings) {
    return url
  }
  return `${url}/reservation${search}`
}

export const mapStateToProps = (state, ownProps) => {
  const { match, location } = ownProps
  const { params, url } = match
  const { search } = location

  const isNotBookable = selectIsNotBookableByRouterMatch(state, match)
  const offer = selectOfferByRouterMatch(state, match) || {}
  const stocks = selectStocksByOfferId(state, offer.id)
  const priceRange = getPriceRangeFromStocks(stocks)

  return {
    isNotBookable,
    priceRange,
    destinationLink: getDestinationLink(params, url, search),
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookThisLink)
