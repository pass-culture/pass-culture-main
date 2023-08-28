import React, { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import SkipLinks from 'components/SkipLinks'
import useNotification from 'hooks/useNotification'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import CookiesFooter from 'pages/CookiesFooter/CookiesFooter'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Signin.module.scss'
import SigninForm from './SigninForm/SigninForm'

const SignIn = (): JSX.Element => {
  useRedirectLoggedUser()
  const notify = useNotification()

  const [searchParams, setSearchParams] = useSearchParams()

  useEffect(() => {
    if (searchParams.get('accountValidation') === 'true') {
      notify.success(
        'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
      )
      setSearchParams('')
    } else if (
      searchParams.get('accountValidation') === 'false' &&
      searchParams.get('message')
    ) {
      notify.error(searchParams.get('message'))
      setSearchParams('')
    }
  }, [searchParams])

  return (
    <>
      <SkipLinks displayMenu={false} />
      <div className={styles['sign-in']}>
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
            pageName: 'sign-in',
          }}
        >
          <section className={styles['content']}>
            <h1>Bienvenue sur l’espace dédié aux acteurs culturels</h1>
            <div className={styles['mandatory']}>
              Tous les champs sont obligatoires
            </div>
            <SigninForm />
            <CookiesFooter className={styles['cookies-footer']} />
          </section>
        </AppLayout>
      </div>
    </>
  )
}

export default SignIn
