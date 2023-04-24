import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import AppLayout from 'app/AppLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import SkipLinks from 'components/SkipLinks'
import useNotification from 'hooks/useNotification'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import Hero from 'ui-kit/Hero'
import Logo from 'ui-kit/Logo/Logo'
import { IS_DEV } from 'utils/config'
import { getReCaptchaToken, initReCaptchaScript } from 'utils/recaptcha'

import ChangePasswordRequestForm from './ChangePasswordRequestForm'
import styles from './LostPassword.module.scss'

const ResetPassword = (): JSX.Element => {
  const [emailValue, setEmailValue] = useState('')
  const [mailSent, setMailSent] = useState(false)

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
    const token = !IS_DEV
      ? await getReCaptchaToken('resetPassword')
      : 'test_token'

    try {
      await api.resetPassword({ token, email: emailValue })
      setMailSent(true)
    } catch {
      notification.error('Une erreur est survenue')
    }
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
    <>
      <SkipLinks displayMenu={false} />
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
          <div className={styles['scrollable-content-side']}>
            <div className={styles['content']}>
              {mailSent ? (
                <Hero
                  linkLabel="Revenir à l’accueil"
                  linkTo="/"
                  text="Vous allez recevoir par e-mail les instructions pour définir un nouveau mot de passe."
                  title="Merci !"
                />
              ) : (
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
    </>
  )
}

export default ResetPassword
