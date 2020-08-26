import { searchSelector } from 'pass-culture-shared'
import { connect } from 'react-redux'
import LostPassword from './LostPassword'
import { requestData } from 'redux-saga-data'
import { compose } from 'redux'

export const mapStateToProps = (state, ownProps) => {
  const userErrors = state.errors.user || []
  const {
    location: { search },
  } = ownProps
  const { change, envoye, token } = searchSelector(state, search)
  return {
    change,
    errors: userErrors,
    envoye,
    token,
  }
}

export const mapDispatchToProps = dispatch => ({
  submitResetPasswordRequest: (emailValue, success, fail) => {
    dispatch(
      requestData({
        apiPath: '/users/reset-password',
        body: { email: emailValue },
        handleFail: fail,
        handleSuccess: success,
        method: 'POST',
      })
    )
  },

  submitResetPassword: (newPassword, token, success, fail) => {
      dispatch(
          requestData({
              apiPath: '/users/new-password',
              body: { newPassword, token },
              handleFail: fail,
              handleSuccess: success,
              method: 'POST',
          })
      )
  },
})

export default compose(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(LostPassword)
