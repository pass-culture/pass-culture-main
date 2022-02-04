import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import SignupValidation from './SignupValidation'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export const mapDispatchToProps = dispatch => ({
  dispatch,
  notifyError: message => {
    dispatch(
      showNotification({
        text: message,
        type: 'error',
      })
    )
  },
  notifySuccess: message => {
    dispatch(
      showNotification({
        text: message,
        type: 'success',
      })
    )
  },
})

export default compose(
  withRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(SignupValidation)
