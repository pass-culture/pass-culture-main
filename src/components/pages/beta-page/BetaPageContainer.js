import BetaPage from './BetaPage'
import { compose } from 'redux'

import withNotRequiredLogin from '../../hocs/with-login/withNotRequiredLogin'
import withTracking from '../../hocs/withTracking'
import { connect } from 'react-redux'
import { ANDROID_APPLICATION_ID } from '../../../utils/config'
import { DEFAULT_WHOLE_FRANCE_OPENING_VALUE } from '../../router/selectors/features'

export const mapStateToProps = state => {
  if (state.features.fetchHasFailed) {
    return {
      isNewBookingLimitsActived: true,
      wholeFranceOpening: DEFAULT_WHOLE_FRANCE_OPENING_VALUE,
    }
  }

  return {
    isNewBookingLimitsActived: true,
    wholeFranceOpening: true,
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackSignup: () => {
      window.gtag_report_conversion()

      const userDevice = document.referrer.includes('android-app://' + ANDROID_APPLICATION_ID)
        ? 'application'
        : 'browser'
      ownProps.tracking.trackEvent({ action: 'signup', name: userDevice })
    },
  }
}

export default compose(
  withNotRequiredLogin,
  withTracking('BetaPage'),
  connect(mapStateToProps, null, mergeProps)
)(BetaPage)
