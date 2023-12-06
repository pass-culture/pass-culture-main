import { Formik } from 'formik'
import React, { useState } from 'react'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import SkipLinks from 'components/SkipLinks'
import useInitReCaptcha from 'hooks/useInitReCaptcha'
import useNotification from 'hooks/useNotification'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import Hero from 'ui-kit/Hero'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { getReCaptchaToken } from 'utils/recaptcha'

import ChangePasswordRequestForm from './ChangePasswordRequestForm'
import styles from './LostPassword.module.scss'
import { validationSchema } from './validationSchema'

type FormValues = { email: string }

const LostPassword = (): JSX.Element => {
  const [mailSent, setMailSent] = useState(false)

  useRedirectLoggedUser()
  useInitReCaptcha()

  const notification = useNotification()

  const submitChangePasswordRequest = async (formValues: FormValues) => {
    const token = await getReCaptchaToken('resetPassword')

    try {
      await api.resetPassword({ token, email: formValues.email })
      setMailSent(true)
    } catch {
      notification.error('Une erreur est survenue')
    }
  }

  return (
    <>
      <SkipLinks displayMenu={false} />

      <div className={styles['lost-password']}>
        <header className={styles['logo-side']}>
          <SvgIcon
            className="logo-unlogged"
            viewBox="0 0 282 120"
            alt="Pass Culture pro, l’espace des acteurs culturels"
            src={logoPassCultureProFullIcon}
            width="135"
          />
        </header>

        <AppLayout fullscreen pageName="lost-password">
          <div className={styles['content']}>
            {mailSent ? (
              <Hero
                linkLabel="Revenir à l’accueil"
                linkTo="/"
                text="Vous allez recevoir par email les instructions pour définir un nouveau mot de passe."
                title="Merci !"
              />
            ) : (
              <Formik
                initialValues={{ email: '' }}
                onSubmit={submitChangePasswordRequest}
                validationSchema={validationSchema}
              >
                <ChangePasswordRequestForm />
              </Formik>
            )}
          </div>
        </AppLayout>
      </div>
    </>
  )
}

export default LostPassword
