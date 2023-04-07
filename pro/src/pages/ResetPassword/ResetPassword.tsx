import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import AppLayout from 'app/AppLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import useNotification from 'hooks/useNotification'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import Hero from 'ui-kit/Hero'
import Logo from 'ui-kit/Logo/Logo'
import { IS_DEV } from 'utils/config'
import { parse } from 'utils/query-string'
import { getReCaptchaToken, initReCaptchaScript } from 'utils/recaptcha'

import ChangePasswordForm from './ChangePasswordForm'
import ChangePasswordRequestForm from './ChangePasswordRequestForm'
import styles from './ResetPassword.module.scss'

const ResetPassword = (): JSX.Element => {
  const [emailValue, setEmailValue] = useState('')
  const [passwordSent, setPasswordSent] = useState(false)
  const [passwordChanged, setPasswordChanged] = useState(false)
  const location = useLocation()
  const { search } = location
  const { token } = parse(search)

  useRedirectLoggedUser()

  const notification = useNotification()

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

    api
      .resetPassword({ token, email: emailValue })
      .then(() => setPasswordSent(true))
      .catch(() => notification.error(error))
  }

  const submitChangePassword = (values: Record<string, string>) => {
    const { newPasswordValue } = values
    api
      .postNewPassword({ newPassword: newPasswordValue, token })
      .then(() => setPasswordChanged(true))
      .catch(() => {
        notification.error(
          "Une erreur s'est produite, veuillez réessayer ultérieurement."
        )
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

  return (
    <div className={styles['lost-password']}>
      <header className={styles['logo-side']}>
        <Logo noLink signPage />
      </header>
      <AppLayout
        layoutConfig={{
          fullscreen: true,
          pageName: 'lost-password',
        }}
      >
        <PageTitle title="Mot de passe perdu" />

        <div className={styles['scrollable-content-side']}>
          <div className={styles['content']}>
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
              <ChangePasswordForm onSubmit={submitChangePassword} />
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
      </AppLayout>
    </div>
  )
}

export default ResetPassword
