import { FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import { parse } from 'commons/utils/query-string'
import { Hero } from 'ui-kit/Hero/Hero'

import { ChangePasswordForm } from './ChangePasswordForm/ChangePasswordForm'
import styles from './ResetPassword.module.scss'
import { validationSchema } from './validationSchema'

export const ResetPassword = (): JSX.Element => {
  const [passwordChanged, setPasswordChanged] = useState(false)
  const [isBadToken, setIsBadToken] = useState(false)
  const location = useLocation()
  const { search } = location
  const { token } = parse(search)

  useRedirectLoggedUser()

  const submitChangePassword = async (values: Record<string, string>) => {
    const { newPasswordValue } = values
    try {
      await api.postNewPassword({ newPassword: newPasswordValue, token })
      setPasswordChanged(true)
    } catch {
      setIsBadToken(true)
    }
  }

  const formik = useFormik({
    initialValues: { newPasswordValue: '' },
    onSubmit: submitChangePassword,
    validationSchema: validationSchema,
  })

  const mainHeading = (passwordChanged && !isBadToken) ? 'Mot de passe changé !' :
    (!token || isBadToken) ? 'Ce lien a expiré !' :
    'Définit un nouveau mot de passe'

  return (
    <Layout layout="logged-out" mainHeading={mainHeading}>
      <div>
        {passwordChanged && !isBadToken && (
          <Hero
            linkLabel="Se connecter"
            linkTo="/connexion"
            text="Vous pouvez dès à présent vous connecter avec votre nouveau mot de passe"
          />
        )}
        {(!token || isBadToken) && (
          <Hero
            linkLabel="Recevoir un nouveau lien"
            linkTo="/demande-mot-de-passe"
            text="Le lien pour réinitialiser votre mot de passe a expiré. Veuillez recommencer la procédure pour recevoir un nouveau lien par email."
          />
        )}
        {token && !passwordChanged && !isBadToken && (
          <section>
            <h1 className={styles['change-password-title']}>
              Définir un nouveau mot de passe
            </h1>
            <FormikProvider value={formik}>
              <ChangePasswordForm />
            </FormikProvider>
          </section>
        )}
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = ResetPassword
