import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'

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
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
import { Hero } from 'ui-kit/Hero/Hero'

import styles from './LostPassword.module.scss'
import { validationSchema } from './validationSchema'

type FormValues = { email: string }

type UserEmailFormValues = {
  email: string
}

export const LostPassword = (): JSX.Element => {
  useRedirectLoggedUser()
  useInitReCaptcha()

  const notification = useNotification()

  const hookForm = useForm<UserEmailFormValues>({
    defaultValues: { email: '' },
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    formState: { errors, isValid, isSubmitSuccessful },
  } = hookForm

  const submitChangePasswordRequest = async (formValues: FormValues) => {
    try {
      const token = await getReCaptchaToken('resetPassword')
      await api.resetPassword({ token, email: formValues.email })
    } catch (e) {
      if (e === RECAPTCHA_ERROR) {
        notification.error(RECAPTCHA_ERROR_MESSAGE)
      }
      notification.error('Une erreur est survenue')
    }
  }

  return (
    <Layout layout="logged-out">
      {isSubmitSuccessful ? (
        <Hero
          linkLabel="Retourner sur la page de connexion"
          linkTo="/"
          text="Vous allez recevoir par email les instructions pour définir un nouveau mot de passe."
          title="Merci !"
        />
      ) : (
        <section className={styles['change-password-request-form']}>
          <h1 className={styles['title']}>Mot de passe oublié ?</h1>
          <p className={styles['subtitle']}>
            Indiquez ci-dessous l’adresse email avec laquelle vous avez créé
            votre compte.
          </p>
          <form onSubmit={handleSubmit(submitChangePasswordRequest)}>
            <FormLayout>
              <FormLayout.Row>
                <TextInput
                  label="Adresse email"
                  description="Format : email@exemple.com"
                  error={errors.email?.message}
                  required={true}
                  asterisk={false}
                  {...register('email')}
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <Button
                  type="submit"
                  className={styles['validation-button']}
                  variant={ButtonVariant.PRIMARY}
                  disabled={!isValid}
                >
                  Valider
                </Button>
              </FormLayout.Row>
            </FormLayout>
          </form>
        </section>
      )}
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = LostPassword
