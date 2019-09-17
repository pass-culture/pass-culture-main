import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import track from 'react-tracking'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import Booking from './Booking'
import selectBookables from '../../../selectors/selectBookables'
import selectBookingByRouterMatch from '../../../selectors/selectBookingByRouterMatch'
import selectOfferByRouterMatch from '../../../selectors/selectOfferByRouterMatch'
import selectRecommendationByRouterMatch from '../../../selectors/selectRecommendationByRouterMatch'
import { bookingNormalizer } from '../../../utils/normalizers'
import { trackEventWrapper } from '../../../helpers/matomo/trackEventWrapper'

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

export const mapDispatchToProps = (dispatch, ownProps) => ({
  trackBookingSuccess: offerId => {
    ownProps.tracking.trackEvent({ action: 'bookingOffer', name: offerId })
  },
  handleSubmit: (formValues, handleRequestFail, handleRequestSuccess) => {
    dispatch(
      requestData({
        apiPath: '/bookings',
        body: { ...formValues, quantity: 1 },
        handleFail: handleRequestFail,
        handleSuccess: handleRequestSuccess,
        method: 'POST',
        name: 'booking',
        normalizer: bookingNormalizer,
      })
    )
  },
})

export default compose(
  withRouter,
  track({ page: 'Offer' }, { dispatch: trackEventWrapper }),
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Booking)
