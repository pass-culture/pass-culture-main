import React, { useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import Logo from 'components/layout/Logo'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { redirectLoggedUser } from 'components/router/helpers'
import * as pcapi from 'repository/pcapi/pcapi'
import Hero from 'ui-kit/Hero'
import { IS_DEV } from 'utils/config'
import { parse } from 'utils/query-string'
import { getReCaptchaToken, initReCaptchaScript } from 'utils/recaptcha'

import ChangePasswordForm from './ChangePasswordForm'
import ChangePasswordRequestForm from './ChangePasswordRequestForm'

const LostPassword = (): JSX.Element => {
  const [emailValue, setEmailValue] = useState('')
  const [newPasswordErrorMessage, setNewPasswordErrorMessage] = useState('')
  const [passwordSent, setPasswordSent] = useState(false)
  const [passwordChanged, setPasswordChanged] = useState(false)
  const history = useHistory()
  const location = useLocation()
  const { search } = location
  const { token } = parse(search)
  const { currentUser } = useCurrentUser()

  const notification = useNotification()

  useEffect(() => {
    redirectLoggedUser(history, location, currentUser)
  }, [currentUser])

  useEffect(() => {
    const gcaptchaScript = initReCaptchaScript()

    return function cleanup() {
      gcaptchaScript.remove()
    }
  })

  const submitChangePasswordRequest = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault()
    const error =
      'Un problème est survenu pendant la réinitialisation du mot de passe, veuillez réessayer plus tard.'
    const token = !IS_DEV
      ? await getReCaptchaToken('resetPassword')
      : 'test_token'

    pcapi
      .resetPassword(token, emailValue)
      .then(() => setPasswordSent(true))
      .catch(() => notification.error(error))
  }

  const submitChangePassword = (values: Record<string, string>) => {
    const { newPasswordValue } = values
    pcapi
      .submitResetPassword(newPasswordValue, token)
      .then(() => setPasswordChanged(true))
      .catch(reason => {
        const { errors } = reason
        if (errors.newPassword) {
          setNewPasswordErrorMessage(errors.newPassword[0])
        } else {
          notification.error(
            "Une erreur s'est produite, veuillez réessayer ultérieurement."
          )
        }
      })
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
          {passwordChanged && (
            <Hero
              linkLabel="Se connecter"
              linkTo="/connexion"
              text="Vous pouvez dès à présent vous connecter avec votre nouveau mot de passe"
              title="Mot de passe changé !"
            />
          )}
          {passwordSent && (
            <Hero
              linkLabel="Revenir à l’accueil"
              linkTo="/"
              text="Vous allez recevoir par e-mail les instructions pour définir un nouveau mot de passe."
              title="Merci !"
            />
          )}
          {token && !passwordChanged && (
            <ChangePasswordForm
              isChangePasswordSubmitDisabled={isChangePasswordSubmitDisabled}
              newPasswordErrorMessage={newPasswordErrorMessage}
              onSubmit={submitChangePassword}
            />
          )}
          {!token && !passwordSent && !passwordChanged && (
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
