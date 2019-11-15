import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import withTracking from '../../hocs/withTracking'
import Booking from './Booking'
import { selectOfferByRouterMatch } from '../../../selectors/data/offersSelectors'
import { bookingNormalizer } from '../../../utils/normalizers'
import { selectRecommendationByRouterMatch } from '../../../selectors/data/recommendationsSelectors'
import { selectBookables } from '../../../selectors/data/bookablesSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match)
  const bookables = selectBookables(state, offer)
  const recommendation = selectRecommendationByRouterMatch(state, match)

  return {
    bookables,
    offer,
    recommendation,
  }
}

export const mapDispatchToProps = dispatch => ({
  handleSubmit: (payload, handleRequestFail, handleRequestSuccess) => {
    dispatch(
      requestData({
        apiPath: '/bookings',
        body: payload,
        handleFail: handleRequestFail,
        handleSuccess: handleRequestSuccess,
        method: 'POST',
        name: 'booking',
        normalizer: bookingNormalizer,
      })
    )
  },
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { offer: { id: offerId } = {} } = stateProps

  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackBookingSuccess: () => {
      ownProps.tracking.trackEvent({ action: 'bookingOffer', name: offerId })
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(Booking)
