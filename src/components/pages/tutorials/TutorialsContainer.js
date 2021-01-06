import { connect } from 'react-redux'
import { compose } from 'redux'

import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Tutorials from './Tutorials'
import { updateCurrentUser } from '../../../redux/actions/currentUser'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import { FEATURES } from '../../router/selectors/features'

export const mapStateToProps = state => ({
  isHomepageDisabled: selectIsFeatureDisabled(state, FEATURES.HOMEPAGE),
  isNewBookingLimitsActived: !selectIsFeatureDisabled(state, FEATURES.APPLY_BOOKING_LIMITS_V2),
})

export const mergeProps = (stateProps, { updateCurrentUser, ...dispatchProps }, { history }) => {
  return {
    ...stateProps,
    ...dispatchProps,
    saveUserHasSeenTutorials: async isHomepageDisabled => {
      await updateCurrentUser({
        hasSeenTutorials: true,
      })
      const path = isHomepageDisabled ? '/decouverte' : '/accueil'
      history.push(path)
    },
  }
}

export default compose(
  withRequiredLogin,
  connect(mapStateToProps, { updateCurrentUser }, mergeProps)
)(Tutorials)
