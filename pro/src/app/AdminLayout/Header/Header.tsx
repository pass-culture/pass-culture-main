import React from 'react'
import { useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import Logo from 'ui-kit/Logo/Logo'

import { MenuUser } from '../MenuUser'

import styles from './Header.module.scss'

const Header = () => {
  const { currentUser } = useCurrentUser()

  const { logEvent } = useAnalytics()
  const location = useLocation()

  return (
    <header className={styles['header']}>
      <div className={styles['nav-brand']}>
        <Logo
          className={styles['nav-item']}
          isUserAdmin={currentUser.isAdmin}
          onClick={() => {
            logEvent?.(Events.CLICKED_PRO, { from: location.pathname })
          }}
        />
      </div>
      <div className={styles['menu-user']}>
        <MenuUser />
      </div>
    </header>
  )
}

export default Header
