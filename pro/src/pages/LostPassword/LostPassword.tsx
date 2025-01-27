import { Formik } from 'formik'
import { useState } from 'react'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from 'commons/core/shared/constants'
import { useInitReCaptcha } from 'commons/hooks/useInitReCaptcha'
import { useNotification } from 'commons/hooks/useNotification'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import { getReCaptchaToken } from 'commons/utils/recaptcha'
import { Hero } from 'ui-kit/Hero/Hero'

import { ChangePasswordRequestForm } from './ChangePasswordRequestForm/ChangePasswordRequestForm'
import { validationSchema } from './validationSchema'

type FormValues = { email: string }

export const LostPassword = (): JSX.Element => {
  const [mailSent, setMailSent] = useState(false)

  useRedirectLoggedUser()
  useInitReCaptcha()

  const notification = useNotification()

  const submitChangePasswordRequest = async (formValues: FormValues) => {
    try {
      const token = await getReCaptchaToken('resetPassword')
      await api.resetPassword({ token, email: formValues.email })
      setMailSent(true)
    } catch (e) {
      if (e === RECAPTCHA_ERROR) {
        notification.error(RECAPTCHA_ERROR_MESSAGE)
      }
      notification.error('Une erreur est survenue')
    }
  }

  return (
    <Layout layout="logged-out">
      {mailSent ? (
        <Hero
          linkLabel="Retourner sur la page de connexion"
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
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = LostPassword
