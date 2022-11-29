import { Menu, MenuButton, MenuItem, MenuPopover } from '@reach/menu-button'
import { positionRight } from '@reach/popover'
import React, { useCallback } from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import { useNavigate } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import { IcoUserFilled, IcoSignout } from 'icons'

import styles from './MenuUser.module.scss'

const MenuUser = () => {
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()
  const onSignoutClick = useCallback(() => {
    logEvent?.(Events.CLICKED_LOGOUT, { from: location.pathname })
    navigate('/logout')
  }, [history, logEvent, location.pathname])

  return (
    <Menu>
      <MenuButton
        className={styles['menu-button']}
        title="User"
        type="button"
        data-testid="stock-form-actions-button-open"
      >
        <IcoUserFilled
          title="Opérations sur le stock"
          className={styles['menu-button-icon']}
        />
      </MenuButton>

      <MenuPopover position={positionRight} className={styles['menu-list']}>
        <MenuItem
          className={styles['menu-item']}
          onSelect={() => navigate('/profil')}
        >
          <IcoUserFilled className={styles['menu-item-icon']} />
          Profil
        </MenuItem>
        <MenuItem className={styles['menu-item']} onSelect={onSignoutClick}>
          <IcoSignout className={styles['menu-item-icon']} />
          Déconnexion
        </MenuItem>
      </MenuPopover>
    </Menu>
  )
}

export default MenuUser
