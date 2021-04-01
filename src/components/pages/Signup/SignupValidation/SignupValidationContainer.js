import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { showNotificationV2 } from 'store/reducers/notificationReducer'
import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import SignupValidation from './SignupValidation'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
    isNewHomepageActive: selectIsFeatureActive(state, 'PRO_HOMEPAGE'),
  }
}

export const mapDispatchToProps = dispatch => ({
  dispatch,
  notifyError: message => {
    dispatch(
      showNotificationV2({
        text: message,
        type: 'error',
      })
    )
  },
  notifySuccess: message => {
    dispatch(
      showNotificationV2({
        text: message,
        type: 'success',
      })
    )
  },
})

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(SignupValidation)
