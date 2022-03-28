import React, { useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router'

import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import Logo from 'components/layout/Logo'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { redirectLoggedUser } from 'components/router/helpers'
import * as pcapi from 'repository/pcapi/pcapi'
import Hero from 'ui-kit/Hero'
import { IS_DEV } from 'utils/config'
import { parse } from 'utils/query-string'
import { getReCaptchaToken } from 'utils/recaptcha'

import { initReCaptchaScript } from '../../../utils/recaptcha'

import ChangePasswordForm from './ChangePasswordForm'
import ChangePasswordRequestForm from './ChangePasswordRequestForm'

interface iAction {
  payload: {
    errors: { newPassword: string[] }
  }
}

type ISubmitResetPasswordRequest = (
  email: string,
  onSuccess: () => void,
  onFail: () => void
) => void

type ISubmitResetPassword = (
  newPasswordValue: string,
  token: string,
  onSuccess: () => void,
  onFail: (state: string, action: iAction) => void
) => void

const LostPassword = (): JSX.Element => {
  const [emailValue, setEmailValue] = useState('')
  const [newPasswordErrorMessage, setNewPasswordErrorMessage] = useState('')
  const history = useHistory()
  const location = useLocation()
  const { search } = location
  const { change, envoye, token } = parse(search)
  const { currentUser } = useCurrentUser()

  const notification = useNotification()
  const submitResetPasswordRequest: ISubmitResetPasswordRequest = (
    emailValue,
    success,
    fail
  ) => {
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

  const submitResetPassword: ISubmitResetPassword = (
    newPassword,
    token,
    success
  ) => {
    pcapi
      .submitResetPassword(newPassword, token)
      .then(() => success())
      .catch(() => displayPasswordResetRequestErrorMessage())
  }

  useEffect(() => {
    redirectLoggedUser(history, location, currentUser)
  }, [currentUser]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const gcaptchaScript = initReCaptchaScript()

    return function cleanup() {
      gcaptchaScript.remove()
    }
  })

  const redirectToResetPasswordRequestSuccessPage = () => {
    history.push('/mot-de-passe-perdu?envoye=1')
  }

  const displayPasswordResetRequestErrorMessage = () => {
    notification.error(
      'Un problème est survenu pendant la réinitialisation du mot de passe, veuillez réessayer plus tard.'
    )
  }

  const submitChangePasswordRequest = (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault()

    return submitResetPasswordRequest(
      emailValue,
      redirectToResetPasswordRequestSuccessPage,
      displayPasswordResetRequestErrorMessage
    )
  }

  const redirectToResetPasswordSuccessPage = () => {
    history.push('/mot-de-passe-perdu?change=1')
  }

  const submitChangePassword = (values: Record<string, string>) => {
    const { newPasswordValue } = values

    return submitResetPassword(
      newPasswordValue,
      token,
      redirectToResetPasswordSuccessPage,
      (state, action) => {
        if (action.payload.errors.newPassword) {
          setNewPasswordErrorMessage(action.payload.errors.newPassword[0])
        } else {
          notification.error(
            "Une erreur s'est produite, veuillez réessayer ultérieurement."
          )
        }
      }
    )
  }

  const handleInputEmailChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setEmailValue(event.target.value)
  }

  const isChangePasswordRequestSubmitDisabled = () => {
    return emailValue === ''
  }

  const isChangePasswordSubmitDisabled = (values: Record<string, string>) => {
    if (!values.newPasswordValue) {
      return true
    }

    return values.newPasswordValue === ''
  }

  return (
    <>
      <PageTitle title="Mot de passe perdu" />
      <div className="logo-side">
        <Logo noLink signPage />
      </div>
      <div className="scrollable-content-side">
        <div className="content">
          {change && (
            <Hero
              linkLabel="Se connecter"
              linkTo="/connexion"
              text="Vous pouvez dès à présent vous connecter avec votre nouveau mot de passe"
              title="Mot de passe changé !"
            />
          )}
          {envoye && (
            <Hero
              linkLabel="Revenir à l’accueil"
              linkTo="/"
              text="Vous allez recevoir par e-mail les instructions pour définir un nouveau mot de passe."
              title="Merci !"
            />
          )}
          {token && (
            <ChangePasswordForm
              isChangePasswordSubmitDisabled={isChangePasswordSubmitDisabled}
              newPasswordErrorMessage={newPasswordErrorMessage}
              onSubmit={submitChangePassword}
            />
          )}
          {!token && !envoye && !change && (
            <ChangePasswordRequestForm
              emailValue={emailValue}
              isChangePasswordRequestSubmitDisabled={
                isChangePasswordRequestSubmitDisabled
              }
              onChange={handleInputEmailChange}
              onSubmit={submitChangePasswordRequest}
            />
          )}
        </div>
      </div>
    </>
  )
}

export default LostPassword
