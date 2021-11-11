import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { selectOfferByRouterMatch } from '../../../redux/selectors/data/offersSelectors'
import { selectBookablesWithoutDateNotAvailable } from '../../../redux/selectors/data/stocksSelectors'
import { requestData } from '../../../utils/fetch-normalize-data/requestData'
import { bookingNormalizer } from '../../../utils/normalizers'
import withTracking from '../../hocs/withTracking'
import Booking from './Booking'
import { setCurrentUser } from '../../../redux/actions/currentUser'
import { getCurrentUser } from '../../../redux/actions/repository/currentUser'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match)
  const bookables = selectBookablesWithoutDateNotAvailable(state, offer)

  return {
    bookables,
    offer,
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
  getCurrentUserInformation: async () => {
    const currentUser = await getCurrentUser()
    return dispatch(setCurrentUser(currentUser))
  },
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const {
    history: {
      location: { pathname },
    },
  } = ownProps
  const basePathRegExp = '^/([^/]*)/'
  const basePath = pathname.match(basePathRegExp)[1]
  const { offer: { id: offerId } = {} } = stateProps

  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackBookingSuccess: () => {
      ownProps.tracking.trackEvent({
        action: `${basePath.toUpperCase()} - bookingOffer`,
        name: offerId,
      })
    },
    trackBookOfferClickFromHomepage: (moduleName, offerId) => {
      ownProps.tracking.trackEvent({
        action: 'BookOfferClick_FromHomepage',
        name: `Module name: ${moduleName} - Offer id: ${offerId}`,
      })
    },
    trackBookOfferSuccessFromHomepage: (moduleName, offerId) => {
      ownProps.tracking.trackEvent({
        action: 'BookOfferSuccess_FromHomepage',
        name: `Module name: ${moduleName} - Offer id: ${offerId}`,
      })
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(Booking)
