import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import BookThisLink from './BookThisLink'
import getPriceRangeFromStocks from '../../../../../../helpers/getPriceRangeFromStocks'
import selectIsFinishedByMatch from '../../../../../../selectors/selectIsFinishedByMatch'
import selectOfferByMatch from '../../../../../../selectors/selectOfferByMatch'
import selectStocksByOfferId from '../../../../../../selectors/selectStocksByOfferId'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const isFinished = selectIsFinishedByMatch(state, match)
  const offer = selectOfferByMatch(state, match) || {}
  const stocks = selectStocksByOfferId(state, offer.id)
  const priceRange = getPriceRangeFromStocks(stocks)

  return {
    isFinished,
    priceRange,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookThisLink)
