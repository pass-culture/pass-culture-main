import React from 'react'
import { useHistory, useLocation } from 'react-router'

import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import * as pcapi from 'repository/pcapi/pcapi'
import { IS_DEV } from 'utils/config'
import { parse } from 'utils/query-string'
import { getReCaptchaToken } from 'utils/recaptcha'

import LostPassword from './LostPassword'

const LostPasswordRoute = () => {
  const location = useLocation()
  const history = useHistory()
  const { search } = location
  const { change, envoye, token } = parse(search)
  const { currentUser } = useCurrentUser()

  const notification = useNotification()
  const submitResetPasswordRequest = (emailValue, success, fail) => {
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
  }

  const submitResetPassword = (newPassword, token, success, fail) => {
    pcapi
      .submitResetPassword(newPassword, token)
      .then(() => success())
      .catch(() => fail())
  }

  return (
    <LostPassword
      change={change}
      currentUser={currentUser}
      envoye={envoye}
      history={history}
      location={location}
      showErrorNotification={notification.error}
      submitResetPassword={submitResetPassword}
      submitResetPasswordRequest={submitResetPasswordRequest}
      token={token}
    />
  )
}

export default LostPasswordRoute
