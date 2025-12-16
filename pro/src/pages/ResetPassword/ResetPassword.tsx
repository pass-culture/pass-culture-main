import { yupResolver } from '@hookform/resolvers/yup'
import { useCallback, useEffect, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { type Params, useNavigate, useParams } from 'react-router'

import { api } from '@/apiClient/api'
import { SignUpLayout } from '@/app/App/layouts/logged-out/SignUpLayout/SignUpLayout'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { ChangePasswordForm } from './ChangePasswordForm/ChangePasswordForm'
import styles from './ResetPassword.module.scss'
import { validationSchema } from './validationSchema'

export type ResetPasswordValues = {
  newPassword: string
  newConfirmationPassword: string
}

export const ResetPassword = (): JSX.Element => {
  const [isLoading, setIsLoading] = useState(true)
  const { token } = useParams<Params>()
  const snackBar = useSnackBar()
  const navigate = useNavigate()

  const invalidTokenHandler = useCallback(() => {
    snackBar.error('Le lien est invalide ou a expiré. Veuillez recommencer.')
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/demande-mot-de-passe')
  }, [navigate, snackBar])

  useEffect(() => {
    if (token) {
      api.postCheckToken({ token }).then(() => {
        setIsLoading(false)
      }, invalidTokenHandler)
    }
  }, [token, invalidTokenHandler])

  const submitChangePassword = async (values: ResetPasswordValues) => {
    const { newPassword } = values
    try {
      // `as string` is used because TS it can be undefined
      // token is always defined as `submitChangePassword` is callable only in that case.
      await api.postNewPassword({ newPassword, token: token as string })

      snackBar.success('Mot de passe modifié.')
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
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

  return (
    <SignUpLayout mainHeading="Réinitialisez votre mot de passe">
      <div>
        <section>
          <p className={styles['mandatory-info']}>
            Veuillez définir votre nouveau mot de passe afin d’accéder à la
            plateforme.
          </p>
          <FormProvider {...hookForm}>
            <ChangePasswordForm onSubmit={submitChangePassword} />
          </FormProvider>
        </section>
      </div>
    </SignUpLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = ResetPassword
