import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'

import BookingCancellation from './BookingCancellation'
import { selectBookingByRouterMatch } from '../../../selectors/data/bookingsSelector'
import { selectOfferByRouterMatch } from '../../../selectors/data/offersSelector'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match)
  const booking = selectBookingByRouterMatch(state, match)

  return {
    booking,
    offer,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookingCancellation)
