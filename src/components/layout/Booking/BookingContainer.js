import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Booking from './Booking'
import selectBookables from '../../../selectors/selectBookables'
import selectBookingByMatch from '../../../selectors/selectBookingByMatch'
import selectOfferByMatch from '../../../selectors/selectOfferByMatch'
import selectRecommendationByMatch from '../../../selectors/selectRecommendationByMatch'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps

  const offer = selectOfferByMatch(state, match)
  const bookables = selectBookables(state, offer)
  const booking = selectBookingByMatch(state, match)
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
