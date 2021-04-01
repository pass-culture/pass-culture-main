import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { showNotification } from 'store/reducers/notificationReducer'
import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { searchSelector } from 'store/selectors/search'
import { IS_DEV } from 'utils/config'
import { getReCaptchaToken } from 'utils/recaptcha'

import LostPassword from './LostPassword'

export const mapStateToProps = (state, ownProps) => {
  const userErrors = state.errors.user || []
  const {
    location: { search },
  } = ownProps
  const { change, envoye, token } = searchSelector(state, search)
  return {
    change,
    currentUser: selectCurrentUser(state),
    errors: userErrors,
    envoye,
    isNewHomepageActive: selectIsFeatureActive(state, 'PRO_HOMEPAGE'),
    token,
  }
}

export const mapDispatchToProps = dispatch => ({
  showErrorNotification: errorText =>
    dispatch(
      showNotification({
        type: 'error',
        text: errorText,
      })
    ),
  submitResetPasswordRequest: (emailValue, success, fail) => {
    if (!IS_DEV) {
      getReCaptchaToken('resetPassword').then(token =>
        dispatch(
          requestData({
            apiPath: '/users/reset-password',
            body: { email: emailValue, token: token },
            handleFail: fail,
            handleSuccess: success,
            method: 'POST',
          })
        )
      )
    } else {
      dispatch(
        requestData({
          apiPath: '/users/reset-password',
          body: { email: emailValue, token: 'test_token' },
          handleFail: fail,
          handleSuccess: success,
          method: 'POST',
        })
      )
    }
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

export default compose(connect(mapStateToProps, mapDispatchToProps))(LostPassword)
