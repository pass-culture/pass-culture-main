import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { apiNew } from '@/apiClient/api'
import { LoggedOutLayout } from '@/app/App/layouts/logged-out/LoggedOutLayout/LoggedOutLayout'
import { logout } from '@/commons/store/user/dispatchers/logout'
import { parse } from '@/commons/utils/query-string'
import { Button } from '@/design-system/Button/Button'

import styles from './EmailChangeValidation.module.scss'

export const EmailChangeValidation = () => {
  const [isSuccess, setIsSuccess] = useState<boolean | undefined>(undefined)
  const location = useLocation()

  useEffect(() => {
    const changeEmail = async () => {
      const { token } = parse(location.search)

      try {
        await apiNew.patchValidateEmail({ body: { token: token } })
        setIsSuccess(true)
        await logout(false)
      } catch {
        setIsSuccess(false)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    changeEmail()
  }, [location.search])

  if (isSuccess === undefined) {
    return null
  }

  return (
    <LoggedOutLayout
      mainHeading={isSuccess ? 'Et voilà !' : 'Votre lien a expiré !'}
    >
      {isSuccess && (
        <>
          <p className={styles['subtitle']}>
            Merci d’avoir confirmé votre changement d’adresse email.
          </p>
          <Button
            onClick={() => {
              // redirection using this to handle store reload
              globalThis.location.href = '/connexion'
            }}
            label="Se connecter"
          />
        </>
      )}
      {!isSuccess && (
        <>
          <p className={styles['subtitle']}>
            Votre adresse email n’a pas été modifiée car le lien reçu par mail
            expire 24 heures après sa réception.
          </p>
          <p className={styles['subtitle']}>
            Connectez-vous avec votre ancienne adresse email.
          </p>
          <Button as="a" to="/" label="Se connecter" />
        </>
      )}
    </LoggedOutLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = EmailChangeValidation
