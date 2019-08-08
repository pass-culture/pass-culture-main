import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Booking from './Booking'
import selectBookables from '../../../selectors/selectBookables'
import selectBookingByRouterMatch from '../../../selectors/selectBookingByRouterMatch'
import selectOfferByMatch from '../../../selectors/selectOfferByMatch'
import selectRecommendationByMatch from '../../../selectors/selectRecommendationByMatch'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps

  const offer = selectOfferByMatch(state, match)
  const bookables = selectBookables(state, offer)
  const booking = selectBookingByRouterMatch(state, match)
  const recommendation = selectRecommendationByMatch(state, match)

  return {
    bookables,
    booking,
    recommendation,
    offer,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Booking)
