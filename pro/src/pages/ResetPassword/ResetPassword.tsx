import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import AppLayout from 'app/AppLayout'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import Hero from 'ui-kit/Hero'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { parse } from 'utils/query-string'
import { initReCaptchaScript } from 'utils/recaptcha'

import ChangePasswordForm from './ChangePasswordForm'
import styles from './ResetPassword.module.scss'

const ResetPassword = (): JSX.Element => {
  const [passwordChanged, setPasswordChanged] = useState(false)
  const [isBadToken, setIsBadToken] = useState(false)
  const location = useLocation()
  const { search } = location
  const { token } = parse(search)

  useRedirectLoggedUser()

  useEffect(() => {
    const gcaptchaScript = initReCaptchaScript()

    return function cleanup() {
      gcaptchaScript.remove()
    }
  })

  const submitChangePassword = async (values: Record<string, string>) => {
    const { newPasswordValue } = values
    try {
      await api.postNewPassword({ newPassword: newPasswordValue, token })
      setPasswordChanged(true)
    } catch {
      setIsBadToken(true)
    }
  }

  return (
    <div className={styles['reset-password']}>
      <header className={styles['logo-side']}>
        <SvgIcon
          className="logo-unlogged"
          viewBox="0 0 282 120"
          alt="Pass Culture pro, l'espace des acteurs culturels"
          src={logoPassCultureProFullIcon}
          width="135"
        />
      </header>
      <AppLayout
        layoutConfig={{
          fullscreen: true,
          pageName: 'reset-password',
        }}
      >
        <div className={styles['content']}>
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
            <ChangePasswordForm onSubmit={submitChangePassword} />
          )}
        </div>
      </AppLayout>
    </div>
  )
}

export default ResetPassword
