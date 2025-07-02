import { yupResolver } from '@hookform/resolvers/yup'
import { useCallback, useEffect, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate, useParams, Params } from 'react-router'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import { Hero } from 'ui-kit/Hero/Hero'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ChangePasswordForm } from './ChangePasswordForm/ChangePasswordForm'
import styles from './ResetPassword.module.scss'
import { validationSchema } from './validationSchema'

export type ResetPasswordValues = {
  newPassword: string
  newConfirmationPassword?: string
}

export const ResetPassword = (): JSX.Element => {
  const [passwordChanged, setPasswordChanged] = useState(false)
  const [isBadToken, setIsBadToken] = useState(false)
  const is2025SignUpEnabled = useActiveFeature('WIP_2025_SIGN_UP')
  const [isLoading, setIsLoading] = useState(is2025SignUpEnabled ? true : false)
  const { token } = useParams<Params>()
  const notify = useNotification()
  const navigate = useNavigate()

  useRedirectLoggedUser()

  const invalidTokenHandler = useCallback(() => {
    notify.error('Le lien est invalide ou a expiré. Veuillez recommencer.')
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/demande-mot-de-passe')
  }, [navigate, notify])

  // If the FF WIP_2025_SIGN_UP is enabled, we check token validity on page load
  useEffect(() => {
    if (is2025SignUpEnabled && token) {
      api.postCheckToken({ token }).then(() => {
        setIsLoading(false)
      }, invalidTokenHandler)
    }
  }, [token, invalidTokenHandler, is2025SignUpEnabled])

  const submitChangePassword = async (values: ResetPasswordValues) => {
    const { newPassword } = values
    try {
      // `as string` is used because TS it can be undefined
      // token is always defined as `submitChangePassword` is callable only in that case.
      await api.postNewPassword({ newPassword, token: token as string })

      if (is2025SignUpEnabled) {
        notify.success('Mot de passe modifié.')
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        navigate('/connexion')
      } else {
        setPasswordChanged(true)
      }
    } catch {
      if (is2025SignUpEnabled) {
        invalidTokenHandler()
      } else {
        setIsBadToken(true)
      }
    }
  }

  const hookForm = useForm<ResetPasswordValues>({
    defaultValues: {
      newPassword: '',
      ...(is2025SignUpEnabled ? { newConfirmationPassword: '' } : {}),
    },
    resolver: yupResolver(validationSchema(is2025SignUpEnabled)),
    mode: 'onTouched',
  })

  if (isLoading) {
    return <Spinner />
  }

  return (
    <Layout layout={is2025SignUpEnabled ? 'sign-up' : 'logged-out'}>
      <div>
        {passwordChanged && !isBadToken && (
          <Hero
            linkLabel="Se connecter"
            linkTo="/connexion"
            text="Vous pouvez dès à présent vous connecter avec votre nouveau mot de passe"
            title="Mot de passe changé !"
          />
        )}
        {(!token || isBadToken) && (
          <Hero
            linkLabel="Recevoir un nouveau lien"
            linkTo="/demande-mot-de-passe"
            text="Le lien pour réinitialiser votre mot de passe a expiré. Veuillez recommencer la procédure pour recevoir un nouveau lien par email."
            title="Ce lien a expiré !"
          />
        )}
        {token && !passwordChanged && !isBadToken && (
          <section>
            <h1 className={styles['change-password-title']}>
              {is2025SignUpEnabled
                ? 'Réinitialisation de mot de passe'
                : 'Définir un nouveau mot de passe'}
            </h1>
            <p className={styles['mandatory-info']}>
              Veuillez définir votre nouveau mot de passe afin d’accéder à la
              plateforme.
            </p>
            <FormProvider {...hookForm}>
              <ChangePasswordForm onSubmit={submitChangePassword} />
            </FormProvider>
          </section>
        )}
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = ResetPassword
