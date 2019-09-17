import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import track from 'react-tracking'

import Navigation from './Navigation'
import { getHeaderColor } from '../../../../../utils/colors'
import getPriceRangeFromStocks from '../../../../../helpers/getPriceRangeFromStocks'
import { trackEventWrapper } from '../../../../../helpers/matomo/trackEventWrapper'

import selectCurrentRecommendation from '../../selectors/selectCurrentRecommendation'
import selectDistanceByOfferId from '../../../../../selectors/selectDistanceByOfferId'
import selectOfferById from '../../../../../selectors/selectOfferById'
import selectStocksByOfferId from '../../../../../selectors/selectStocksByOfferId'

export const mapStateToProps = (state, ownProps) => {
  const { match: { params: { mediationId, offerId } = {} } = {} } = ownProps
  const { firstThumbDominantColor } = selectCurrentRecommendation(state, offerId, mediationId) || {}
  const offer = selectOfferById(state, offerId)
  const { venue } = offer || {}
  const stocks = selectStocksByOfferId(state, offerId)
  const { isVirtual } = venue || {}

  const headerColor = getHeaderColor(firstThumbDominantColor)
  const backgroundGradient = `linear-gradient(to bottom, rgba(0,0,0,0) 0%,${headerColor} 30%,${headerColor} 100%)`
  const distanceClue = (venue && isVirtual) ? 'offre numérique' : selectDistanceByOfferId(state, offerId)
  const priceRange = getPriceRangeFromStocks(stocks)
  const separator = offer ? '\u00B7' : ' '
  return {
    headerColor,
    backgroundGradient,
    distanceClue,
    priceRange,
    separator,
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => ({
  trackConsultOffer: offerId => {
    ownProps.tracking.trackEvent({ action: 'consultOffer', name: offerId })
  },
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { trackConsultOffer } = dispatchProps
  const { match: { params: { offerId } = {} } = {} } = ownProps

  return {
    ...stateProps,
    ...dispatchProps,
    trackConsultOffer: () => trackConsultOffer(offerId),
    ...ownProps,
  }
}

export default compose(
  withRouter,
  track({ page: 'Offer' }, { dispatch: trackEventWrapper }),
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(Navigation)
