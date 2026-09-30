import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { SignUpLayout } from '@/app/App/layouts/logged-out/SignUpLayout/SignUpLayout'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useInitReCaptcha } from '@/commons/hooks/useInitReCaptcha'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { getReCaptchaToken } from '@/commons/utils/recaptcha'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ReSendEmailCallout } from '@/components/ReSendEmailCallout/ReSendEmailCallout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullNextIcon from '@/icons/full-next.svg'
import { Title } from '@/ui-kit/Title/Title'

import styles from './LostPassword.module.scss'
import { validationSchema } from './validationSchema'

type FormValues = { email: string }

type UserEmailFormValues = {
  email: string
}

// TODO (jclery-pass, 2026-09-30): Once WIP_PRE_SIGNUP_SIMULATION is removed,
// just remove this temporary component and directly use the <FullLayout> inside <LostPassword>’s render
const LostPasswordFullLayout = ({
  children,
}: {
  children: React.ReactNode
}) => (
  <FullLayout verticallyCenteredContent>
    <div className={styles['lostpassword-wrapper']}>{children}</div>
  </FullLayout>
)

export const LostPassword = (): JSX.Element => {
  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )
  const [email, setEmail] = useState<string>('')
  useInitReCaptcha()

  const snackBar = useSnackBar()

  const hookForm = useForm<UserEmailFormValues>({
    defaultValues: { email: '' },
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = hookForm

  const submitChangePasswordRequest = async (formValues: FormValues) => {
    try {
      await sendChangePasswordRequest(formValues.email)
      setEmail(formValues.email)
    } catch (e) {
      if (e === RECAPTCHA_ERROR) {
        snackBar.error(RECAPTCHA_ERROR_MESSAGE)
      }
      snackBar.error('Une erreur est survenue')
    }
  }

  const sendChangePasswordRequest = async (email: string): Promise<void> => {
    const token = await getReCaptchaToken('resetPassword')
    return api.resetPassword({ body: { token, email: email } })
  }

  const LayoutComponent = isSignupSimulationEnabled
    ? LostPasswordFullLayout
    : SignUpLayout

  const mainHeading = email
    ? 'Vous allez recevoir un email'
    : 'Réinitialisez votre mot de passe'

  return (
    <LayoutComponent>
      <Title level="1" title={mainHeading} marginBottom="xxl" />
      {email ? (
        <section>
          <p className={styles['change-password-request-success-body']}>
            Cliquez sur le lien envoyé par email à <b>{email}</b>
          </p>
          <ReSendEmailCallout action={() => sendChangePasswordRequest(email)} />
        </section>
      ) : (
        <section>
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
                  required
                  requiredIndicator="hidden"
                  type="email"
                  {...register('email')}
                />
              </FormLayout.Row>
              <FormLayout.Row className={styles['validation-button']}>
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  label="Réinitialiser"
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <Button
                  as="router-link"
                  to="/connexion"
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.NEUTRAL}
                  icon={fullNextIcon}
                  label="Retour à la connexion"
                />
              </FormLayout.Row>
            </FormLayout>
          </form>
        </section>
      )}
    </LayoutComponent>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = LostPassword
