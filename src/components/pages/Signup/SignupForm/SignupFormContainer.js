import get from 'lodash.get'
import { removeWhitespaces } from 'react-final-form-utils'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { removeErrors } from 'store/reducers/errors'
import { closeNotification, showNotificationV1 } from 'store/reducers/notificationReducer'

import SignupForm from './SignupForm'

const STATE_ERROR_NAME = 'user'

export const mapStateToProps = state => ({
  errors: get(state, `errors["${STATE_ERROR_NAME}"]`),
})

export const mapDispatchToProps = (dispatch, ownProps) => ({
  createNewProUser: (payload, onHandleFail, onHandleSuccess) => {
    dispatch(removeErrors(STATE_ERROR_NAME))

    const { firstName, siren } = payload
    dispatch(
      requestData({
        apiPath: '/users/signup/pro',
        method: 'POST',
        body: { ...payload, siren: removeWhitespaces(siren), publicName: firstName },
        name: STATE_ERROR_NAME,
        handleFail: onHandleFail,
        handleSuccess: onHandleSuccess,
      })
    )
  },

  redirectToConfirmation: () => {
    ownProps.history.replace('/inscription/confirmation')
  },

  showNotification: (message, type) => {
    dispatch(
      showNotificationV1({
        text: message,
        type: type,
      })
    )
  },

  closeNotification: () => {
    dispatch(closeNotification())
  },
})

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(SignupForm)
