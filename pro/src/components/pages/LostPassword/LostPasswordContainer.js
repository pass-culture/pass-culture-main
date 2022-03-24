import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import * as pcapi from 'repository/pcapi/pcapi'
import { showNotification } from 'store/reducers/notificationReducer'
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
        pcapi
          .resetPassword(token, emailValue)
          .then(() => success())
          .catch(() => fail())
      )
    } else {
      pcapi
        .resetPassword('test_token', emailValue)
        .then(() => success())
        .catch(() => fail())
    }
  },

  submitResetPassword: (newPassword, token, success, fail) => {
    pcapi
      .submitResetPassword(newPassword, token)
      .then(() => success())
      .catch(() => fail())
  },
})

export default compose(
  withRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(LostPassword)
