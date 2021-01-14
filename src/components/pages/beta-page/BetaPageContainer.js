import BetaPage from './BetaPage'
import { compose } from 'redux'
import withTracking from '../../hocs/withTracking'
import { connect } from 'react-redux'
import { ANDROID_APPLICATION_ID } from '../../../utils/config'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import selectIsFeatureEnabled from '../../router/selectors/selectIsFeatureEnabled'
import { FEATURES } from '../../router/selectors/features'

export const mapStateToProps = state => ({
  isNewBookingLimitsActived: !selectIsFeatureDisabled(state, FEATURES.APPLY_BOOKING_LIMITS_V2),
  wholeFranceOpening: selectIsFeatureEnabled(state, 'WHOLE_FRANCE_OPENING'),
})

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
  withTracking('BetaPage'),
  connect(mapStateToProps, null, mergeProps)
)(BetaPage)
