import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Navigation from './Navigation'
import selectCurrentRecommendation from '../../selectors/selectCurrentRecommendation'
import { getHeaderColor } from '../../../../../utils/colors'
import getPriceRangeFromStocks from '../../../../../helpers/getPriceRangeFromStocks'
import selectDistanceByOfferId from '../../../../../selectors/selectDistanceByOfferId'
import selectOfferById from '../../../../../selectors/selectOfferById'
import selectStocksByOfferId from '../../../../../selectors/selectStocksByOfferId'

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { mediationId, offerId } = params
  const currentRecommendation = selectCurrentRecommendation(state, offerId, mediationId)
  const { firstThumbDominantColor } = currentRecommendation || {}
  const headerColor = getHeaderColor(firstThumbDominantColor)
  const backgroundGradient = `linear-gradient(to bottom, rgba(0,0,0,0) 0%,${headerColor} 30%,${headerColor} 100%)`
  const offer = selectOfferById(state, offerId)
  const { venue } = offer || {}
  const stocks = selectStocksByOfferId(state, offerId)
  const { isVirtual } = venue || {}
  const distance = selectDistanceByOfferId(state, offerId)
  let distanceClue = ' '
  if (venue) {
    distanceClue = isVirtual ? 'offre numérique' : distance
  }
  const priceRange = getPriceRangeFromStocks(stocks)

  const separator = offer ? '\u00B7' : ' '
  return {
    backgroundGradient,
    distanceClue,
    headerColor,
    priceRange,
    separator,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Navigation)
