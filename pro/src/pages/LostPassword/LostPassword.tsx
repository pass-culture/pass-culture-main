import { yupResolver } from '@hookform/resolvers/yup'
import cn from 'classnames'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useInitReCaptcha } from 'commons/hooks/useInitReCaptcha'
import { useMediaQuery } from 'commons/hooks/useMediaQuery'
import { useNotification } from 'commons/hooks/useNotification'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import { getReCaptchaToken } from 'commons/utils/recaptcha'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { Hero } from 'ui-kit/Hero/Hero'

import emailIcon from './assets/email.svg'
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
  const is2025SignUpEnabled = useActiveFeature('WIP_2025_SIGN_UP')
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
      const token = await getReCaptchaToken('resetPassword')
      await api.resetPassword({ token, email: formValues.email })
      setEmail(formValues.email)
    } catch (e) {
      if (e === RECAPTCHA_ERROR) {
        notification.error(RECAPTCHA_ERROR_MESSAGE)
      }
      notification.error('Une erreur est survenue')
    }
  }

  const successComponent = is2025SignUpEnabled ? (
    <section className={styles['change-password-request-success']}>
      <img
        src={emailIcon}
        alt=""
        className={styles['change-password-request-success-icon']}
      />
      <h1 className={styles['change-password-request-success-title']}>
        Vous allez recevoir un email !
      </h1>
      <p className={styles['change-password-request-success-body']}>
        Cliquez sur le lien envoyé par email à <b>{email}</b>
      </p>
      <Callout>
        <p className={styles['change-password-request-success-info']}>
          Vous n’avez pas reçu d’email ? <br /> Vérifiez vos spams ou cliquez
          ici pour le recevoir à nouveau.
        </p>
      </Callout>
    </section>
  ) : (
    <Hero
      linkLabel="Retourner sur la page de connexion"
      linkTo="/"
      text="Vous allez recevoir par email les instructions pour définir un nouveau mot de passe."
      title="Merci !"
    />
  )

  return (
    <Layout layout={is2025SignUpEnabled ? 'sign-up' : 'logged-out'}>
      {email ? (
        successComponent
      ) : (
        <section
          className={cn(styles['change-password-request-form'], {
            [styles['change-password-request-form-old']]: !is2025SignUpEnabled,
          })}
        >
          <h1 className={styles['title']}>
            Mot de passe oublié{!is2025SignUpEnabled && ' ?'}
          </h1>
          <p className={styles['subtitle']}>
            {is2025SignUpEnabled
              ? 'Entrez votre email pour recevoir un lien de réinitialisation.'
              : 'Indiquez ci-dessous l’adresse email avec laquelle vous avez créé votre compte.'}
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
                  {is2025SignUpEnabled ? 'Réinitialiser' : 'Valider'}
                </Button>
              </FormLayout.Row>
              {is2025SignUpEnabled && (
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
              )}
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
