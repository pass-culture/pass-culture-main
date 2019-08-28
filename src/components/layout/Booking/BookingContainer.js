import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Booking from './Booking'
import selectBookables from '../../../selectors/selectBookables'
import selectBookingByRouterMatch from '../../../selectors/selectBookingByRouterMatch'
import selectOfferByRouterMatch from '../../../selectors/selectOfferByRouterMatch'
import selectRecommendationByRouterMatch from '../../../selectors/selectRecommendationByRouterMatch'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps

  const offer = selectOfferByRouterMatch(state, match)
  const bookables = selectBookables(state, offer)
  const booking = selectBookingByRouterMatch(state, match)
  const recommendation = selectRecommendationByRouterMatch(state, match)

  return {
    bookables,
    booking,
    offer,
    recommendation,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Booking)
