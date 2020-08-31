import withTracking from '../../../../../hocs/withTracking'
import SeeMore from './SeeMore'
import { compose } from 'redux'
import { connect } from 'react-redux'

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackSeeMoreHasBeenClicked: moduleName => {
      ownProps.tracking.trackEvent({ action: 'seeMoreHasBeenClicked', name: moduleName })
    },
  }
}

export default compose(
  withTracking('Home'),
  connect(
    null,
    null,
    mergeProps,
  ),
)(SeeMore)
