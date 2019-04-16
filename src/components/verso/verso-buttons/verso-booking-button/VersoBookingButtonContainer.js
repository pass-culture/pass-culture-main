/* eslint
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { isRecommendationOfferFinished } from '../../../../helpers/isRecommendationOfferFinished'
import { selectBookings } from '../../../../selectors/selectBookings'
import currentRecommendation from '../../../../selectors/currentRecommendation'

import VersoBookingButton from './VersoBookingButton'

export const mapStateToProps = (state, { match, location }) => {
  const { mediationId, offerId } = match.params
  const { search: locationSearch } = location
  const recommendation = currentRecommendation(state, offerId, mediationId)
  const isFinished = isRecommendationOfferFinished(recommendation, offerId)
  // NOTE -> on ne peut pas faire confiance a bookingsIds
  // bookingsIds n'est pas mis à jour avec le state
  const stocks = get(recommendation, 'offer.stocks')
  const stockIds = (stocks || []).map(o => o.id)
  const bookings = selectBookings(state)
  const booking = bookings.find(b => stockIds.includes(b.stockId))
  const onlineOfferUrl = get(booking, 'completedUrl')

  return {
    booking,
    isFinished,
    locationSearch,
    onlineOfferUrl,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoBookingButton)
