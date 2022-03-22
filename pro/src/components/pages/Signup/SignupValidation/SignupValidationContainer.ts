import { connect } from 'react-redux'

import { showNotification } from 'store/reducers/notificationReducer'

import SignupValidation from './SignupValidation'
import type { Props } from './SignupValidation'

export const mapDispatchToProps: Props = {
  notifyError: message =>
    showNotification({
      text: message,
      type: 'error',
    }),

  notifySuccess: message =>
    showNotification({
      text: message,
      type: 'success',
    }),
}

export default connect<[null, Props]>(
  null,
  mapDispatchToProps
)(SignupValidation)
