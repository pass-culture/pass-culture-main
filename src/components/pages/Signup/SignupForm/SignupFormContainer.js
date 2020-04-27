import { closeNotification, showNotification } from 'pass-culture-shared'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { connect } from 'react-redux'
import get from 'lodash.get'
import SignupForm from './SignupForm'
import { requestData } from 'redux-saga-data'
import { removeWhitespaces } from 'react-final-form-utils'
import { removeErrors } from '../../../../reducers/errors'

const STATE_ERROR_NAME = 'user'

export const mapStateToProps = state => ({
  offererName: get(state, 'form.user.name'),
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
      showNotification({
        text: message,
        type: type,
      })
    )
  },

  closeNotification: () => {
    dispatch(closeNotification())
  },
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(SignupForm)
