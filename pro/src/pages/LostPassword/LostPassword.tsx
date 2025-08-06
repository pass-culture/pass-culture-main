import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient//api'
import { Layout } from '@/app/App/layout/Layout'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import { useInitReCaptcha } from '@/commons/hooks/useInitReCaptcha'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { useNotification } from '@/commons/hooks/useNotification'
import { useRedirectLoggedUser } from '@/commons/hooks/useRedirectLoggedUser'
import { getReCaptchaToken } from '@/commons/utils/recaptcha'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ReSendEmailCallout } from '@/components/ReSendEmailCallout/ReSendEmailCallout'
import fullNextIcon from '@/icons/full-next.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import styles from './LostPassword.module.scss'
import { validationSchema } from './validationSchema'

type FormValues = { email: string }

type UserEmailFormValues = {
  email: string
}

export const LostPassword = (): JSX.Element => {
  const [email, setEmail] = useState<string>('')
  useRedirectLoggedUser()
  useInitReCaptcha()
  const isLaptopScreenAtLeast = useMediaQuery('(min-width: 64rem)')

  const notification = useNotification()

  const hookForm = useForm<UserEmailFormValues>({
    defaultValues: { email: '' },
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = hookForm

  const submitChangePasswordRequest = async (formValues: FormValues) => {
    try {
      await sendChangePasswordRequest(formValues.email)
      setEmail(formValues.email)
    } catch (e) {
      if (e === RECAPTCHA_ERROR) {
        notification.error(RECAPTCHA_ERROR_MESSAGE)
      }
      notification.error('Une erreur est survenue')
    }
  }

  const sendChangePasswordRequest = async (email: string): Promise<void> => {
    const token = await getReCaptchaToken('resetPassword')
    return api.resetPassword({ token, email: email })
  }

  const mainHeading = email
    ? 'Vous allez recevoir un email'
    : 'Réinitialisez votre mot de passe'

  return (
    <Layout layout="sign-up" mainHeading={mainHeading}>
      {email ? (
        <section className={styles['change-password-request-success']}>
          <p className={styles['change-password-request-success-body']}>
            Cliquez sur le lien envoyé par email à <b>{email}</b>
          </p>
          <ReSendEmailCallout action={() => sendChangePasswordRequest(email)} />
        </section>
      ) : (
        <section className={styles['change-password-request-form']}>
          <p className={styles['subtitle']}>
            Entrez votre email pour recevoir un lien de réinitialisation.
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
                  className={styles['change-password-request-form-input']}
                  {...register('email')}
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <Button
                  type="submit"
                  className={styles['validation-button']}
                  variant={ButtonVariant.PRIMARY}
                >
                  Réinitialiser
                </Button>
              </FormLayout.Row>
              <FormLayout.Row>
                <ButtonLink
                  to="/connexion"
                  className={styles['back-button']}
                  variant={
                    isLaptopScreenAtLeast
                      ? ButtonVariant.TERNARY
                      : ButtonVariant.QUATERNARY
                  }
                  icon={fullNextIcon}
                >
                  Retour à la connexion
                </ButtonLink>
              </FormLayout.Row>
            </FormLayout>
          </form>
        </section>
      )}
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = LostPassword
