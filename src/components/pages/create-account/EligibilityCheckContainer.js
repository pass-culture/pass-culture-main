import { withRouter } from 'react-router'
import EligibilityCheck from './EligibilityCheck'
import { compose } from 'redux'
import { connect } from 'react-redux'
import withTracking from '../../hocs/withTracking'
import selectIsFeatureEnabled from '../../router/selectors/selectIsFeatureEnabled'
import { DEFAULT_WHOLE_FRANCE_OPENING_VALUE, FEATURES } from '../../router/selectors/features'

export const mapStateToProps = state => {
  if (state.features.fetchHasFailed) {
    return {
      isIdCheckAvailable: false,
      wholeFranceOpening: DEFAULT_WHOLE_FRANCE_OPENING_VALUE,
    }
  }

  return {
    isIdCheckAvailable: selectIsFeatureEnabled(state, FEATURES.ALLOW_IDCHECK_REGISTRATION),
    wholeFranceOpening: selectIsFeatureEnabled(state, FEATURES.WHOLE_FRANCE_OPENING),
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackEligibility: eligibilityRule => {
      ownProps.tracking.trackEvent({
        action: eligibilityRule,
        name: eligibilityRule,
      })
    },
  }
}

export default compose(
  withTracking('EligibilityCheck'),
  withRouter,
  connect(mapStateToProps, null, mergeProps)
)(EligibilityCheck)
