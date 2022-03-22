import { connect } from 'react-redux'

import { showNotification } from 'store/reducers/notificationReducer'

import SignupValidation from './SignupValidation'

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

export default connect(null, mapDispatchToProps)(SignupValidation)
