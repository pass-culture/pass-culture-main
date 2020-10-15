import { withRouter } from 'react-router'
import EligibilityCheck from './EligibilityCheck'
import { compose } from 'redux'
import { connect } from 'react-redux'
import withTracking from '../../hocs/withTracking'

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
  connect(null, null, mergeProps)
)(EligibilityCheck)
