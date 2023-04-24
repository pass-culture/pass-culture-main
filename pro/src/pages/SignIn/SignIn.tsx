import React from 'react'

import AppLayout from 'app/AppLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import SkipLinks from 'components/SkipLinks'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import Logo from 'ui-kit/Logo/Logo'

import styles from './Signin.module.scss'
import SigninForm from './SigninForm/SigninForm'

const SignIn = (): JSX.Element => {
  useRedirectLoggedUser()

  return (
    <>
      <SkipLinks displayMenu={false} />
      <div className={styles['sign-in']}>
        <header className={styles['logo-side']}>
          <Logo noLink signPage />
        </header>
        <AppLayout
          layoutConfig={{
            fullscreen: true,
            pageName: 'sign-in',
          }}
        >
          <PageTitle title="Se connecter" />
          <section className={styles['scrollable-content-side']}>
            <div className={styles['content']}>
              <h1>Bienvenue sur l’espace dédié aux acteurs culturels</h1>
              <span className={styles['has-text-grey']}>
                Tous les champs sont obligatoires
              </span>
              <SigninForm />
            </div>
          </section>
        </AppLayout>
      </div>
    </>
  )
}

export default SignIn
