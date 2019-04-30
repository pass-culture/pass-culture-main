import get from 'lodash.get'
import { connect } from 'react-redux'
import { selectBookables } from '../../selectors/selectBookables'
import { selectBookingById } from '../../selectors/selectBookings'
import { currentRecommendationSelector } from '../../selectors'
import Booking from './Booking'

export const mapStateToProps = (state, { match }) => {
  const { offerId, mediationId, view, bookingId } = match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const isEvent = (get(recommendation, 'offer.eventId') && true) || false
  const bookables = selectBookables(state, recommendation, match)
  const booking = selectBookingById(state, bookingId)

  return {
    bookables,
    booking,
    isCancelled: view === 'cancelled',
    isEvent,
    recommendation,
  }
}

export default connect(mapStateToProps)(Booking)
