import { yupResolver } from '@hookform/resolvers/yup'
import { useCallback, useEffect, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { type Params, useNavigate, useParams } from 'react-router'

import { api } from '@/apiClient/api'
import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { SignUpLayout } from '@/app/App/layouts/logged-out/SignUpLayout/SignUpLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { ChangePasswordForm } from './ChangePasswordForm/ChangePasswordForm'
import styles from './ResetPassword.module.scss'
import { validationSchema } from './validationSchema'

export type ResetPasswordValues = {
  newPassword: string
  newConfirmationPassword: string
}

// TODO (jclery-pass, 2026-09-30): Once WIP_PRE_SIGNUP_SIMULATION is removed,
// just remove this temporary component and directly use the <FullLayout> inside <ResetPassword>’s render
const ResetPasswordFullLayout = ({
  children,
}: {
  children: React.ReactNode
}) => (
  <FullLayout verticallyCenteredContent>
    <div className={styles['resetpassword-wrapper']}>{children}</div>
  </FullLayout>
)

export const ResetPassword = (): JSX.Element => {
  const [isLoading, setIsLoading] = useState(true)
  const { token } = useParams<Params>()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )

  const invalidTokenHandler = useCallback(() => {
    snackBar.error('Le lien est invalide ou a expiré. Veuillez recommencer.')
    navigate('/demande-mot-de-passe')
  }, [navigate, snackBar])

  useEffect(() => {
    if (token) {
      api.postCheckToken({ body: { token } }).then(() => {
        setIsLoading(false)
      }, invalidTokenHandler)
    }
  }, [token, invalidTokenHandler])

  const submitChangePassword = async (values: ResetPasswordValues) => {
    const { newPassword } = values
    try {
      // `as string` is used because TS it can be undefined
      // token is always defined as `submitChangePassword` is callable only in that case.
      await api.postNewPassword({
        body: { newPassword, token: token as string },
      })

      snackBar.success('Mot de passe modifié.')
      navigate('/connexion')
    } catch {
      invalidTokenHandler()
    }
  }

  const hookForm = useForm<ResetPasswordValues>({
    defaultValues: {
      newPassword: '',
      newConfirmationPassword: '',
    },
    resolver: yupResolver(validationSchema),
    mode: 'onTouched',
  })

  if (isLoading) {
    return <Spinner />
  }

  const LayoutComponent = isSignupSimulationEnabled
    ? ResetPasswordFullLayout
    : SignUpLayout

  return (
    <LayoutComponent>
      <h1 className={styles['title']}>Réinitialisez votre mot de passe</h1>
      <section>
        <p className={styles['mandatory-info']}>
          Veuillez définir votre nouveau mot de passe afin d’accéder à la
          plateforme.
        </p>
        <FormProvider {...hookForm}>
          <ChangePasswordForm onSubmit={submitChangePassword} />
        </FormProvider>
      </section>
    </LayoutComponent>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = ResetPassword
