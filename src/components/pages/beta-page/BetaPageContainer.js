import withNotRequiredLogin from '../../hocs/with-login/withNotRequiredLogin'
import BetaPage from './BetaPage'
import { compose } from 'redux'
import withTracking from '../../hocs/withTracking'
import { connect } from 'react-redux'
import { ANDROID_APPLICATION_ID } from '../../../utils/config'

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
  connect(
    null,
    null,
    mergeProps
  )
)(BetaPage)
