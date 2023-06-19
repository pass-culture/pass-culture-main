import React from 'react'
import { Route, Routes } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import { IRoute } from 'app/AppRouter/routesMap'
import { routesSignup } from 'app/AppRouter/subroutesSignupMap'
import SkipLinks from 'components/SkipLinks'
import useActiveFeature from 'hooks/useActiveFeature'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { ROOT_PATH } from 'utils/config'

import styles from './Signup.module.scss'
import SignupUnavailable from './SignupUnavailable/SignupUnavailable'

const Signup = () => {
  const isProAccountCreationEnabled = useActiveFeature(
    'ENABLE_PRO_ACCOUNT_CREATION'
  )
  return (
    <>
      <SkipLinks displayMenu={false} />
      <div className={styles['sign-up']}>
        <header className={styles['logo-side']}>
          <SvgIcon
            className="logo-unlogged"
            viewBox="0 0 282 120"
            alt="Pass Culture pro, l'espace des acteurs culturels"
            src={`${ROOT_PATH}/icons/logo-pass-culture-primary.svg`}
            width="282"
          />
        </header>
        <AppLayout
          layoutConfig={{
            fullscreen: true,
            pageName: 'sign-up',
          }}
        >
          {isProAccountCreationEnabled ? (
            <Routes>
              {routesSignup.map(({ path, element }: IRoute) => (
                <Route key={path} path={path} element={element} />
              ))}
            </Routes>
          ) : (
            <SignupUnavailable />
          )}
        </AppLayout>
      </div>
    </>
  )
}

export default Signup
