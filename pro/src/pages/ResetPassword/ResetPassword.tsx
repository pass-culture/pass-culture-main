import { yupResolver } from '@hookform/resolvers/yup'
import { useCallback, useEffect, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { Params, useNavigate, useParams } from 'react-router'

import { api } from '@/apiClient//api'
import { Layout } from '@/app/App/layout/Layout'
import { useNotification } from '@/commons/hooks/useNotification'
import { useRedirectLoggedUser } from '@/commons/hooks/useRedirectLoggedUser'
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
  const notify = useNotification()
  const navigate = useNavigate()

  useRedirectLoggedUser()

  const invalidTokenHandler = useCallback(() => {
    notify.error('Le lien est invalide ou a expiré. Veuillez recommencer.')
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/demande-mot-de-passe')
  }, [navigate, notify])

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

      notify.success('Mot de passe modifié.')
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
    <Layout layout="sign-up" mainHeading="Réinitialisez votre mot de passe">
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
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = ResetPassword
