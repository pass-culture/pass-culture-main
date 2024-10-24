import React from 'react'
import { Outlet } from 'react-router-dom'

import { OldLayout } from 'app/App/layout/OldLayout'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import logoStyles from 'styles/components/_Logo.module.scss'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Signup.module.scss'
import { SignupUnavailable } from './SignupUnavailable/SignupUnavailable'

export const Signup = () => {
  const isProAccountCreationEnabled = useActiveFeature(
    'ENABLE_PRO_ACCOUNT_CREATION'
  )
  return (
    <OldLayout>
      <header className={styles['logo-side']}>
        <SvgIcon
          className={logoStyles['logo-unlogged']}
          viewBox="0 0 282 120"
          alt="Pass Culture pro, l’espace des acteurs culturels"
          src={logoPassCultureProFullIcon}
          width="135"
        />
      </header>
      {isProAccountCreationEnabled ? <Outlet /> : <SignupUnavailable />}
    </OldLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Signup
