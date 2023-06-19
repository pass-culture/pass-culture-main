import React from 'react'

import AppLayout from 'app/AppLayout'
import SkipLinks from 'components/SkipLinks'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { ROOT_PATH } from 'utils/config'

import styles from './Signin.module.scss'
import SigninForm from './SigninForm/SigninForm'

const SignIn = (): JSX.Element => {
  useRedirectLoggedUser()

  return (
    <>
      <SkipLinks displayMenu={false} />
      <div className={styles['sign-in']}>
        <header className={styles['logo-side']}>
          <SvgIcon
            className="logo-unlogged"
            viewBox="0 0 282 120"
            alt="Pass Culture pro, l'espace des acteurs culturels"
            src={`${ROOT_PATH}/icons/logo-pass-culture-primary.svg`}
          />
        </header>
        <AppLayout
          layoutConfig={{
            fullscreen: true,
            pageName: 'sign-in',
          }}
        >
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
