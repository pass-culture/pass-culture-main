import { type KeyboardEvent, useCallback, useId, useRef, useState } from 'react'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useOnClickOrFocusOutside } from '@/commons/hooks/useOnClickOrFocusOutside'
import { logout } from '@/commons/store/user/dispatchers/logout'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullCloseIcon from '@/icons/full-close.svg'
import fullLogoutIcon from '@/icons/full-logout.svg'
import fullProfilIcon from '@/icons/full-profil.svg'

import styles from './HeaderDropdown.module.scss'

export const HeaderDropdown = () => {
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false)
  const profileMenuWrapperRef = useRef<HTMLDivElement>(null)
  const profileBtnRef = useRef<HTMLButtonElement>(null)
  const profileMenuId = useId()
  const { logEvent } = useAnalytics()
  const currentUser = useAppSelector(selectCurrentUser)
  const { pathname } = useLocation()
  const IN_STRUCTURE_CREATION_FUNNEL = pathname.startsWith(
    '/inscription/structure'
  )
  const closeProfileMenu = useCallback(() => {
    setIsProfileMenuOpen(false)
    profileBtnRef.current?.focus()
  }, [])

  const closeProfileMenuOnOutsideInteraction = useCallback(() => {
    if (isProfileMenuOpen) {
      setIsProfileMenuOpen(false)
    }
  }, [isProfileMenuOpen])

  useOnClickOrFocusOutside(
    profileMenuWrapperRef,
    closeProfileMenuOnOutsideInteraction
  )

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      closeProfileMenu()
    }
  }

  const logEventAndLogout = async () => {
    logEvent(Events.CLICKED_LOGOUT)

    await logout()
  }

  const isCurrentPageProfilePage = globalThis.location.href.includes('/profil')

  return (
    <div ref={profileMenuWrapperRef} className={styles['profile-menu-wrapper']}>
      <Button
        data-testid="profile-button"
        aria-label="Profil"
        icon={fullProfilIcon}
        variant={ButtonVariant.SECONDARY}
        aria-expanded={isProfileMenuOpen}
        aria-controls={profileMenuId}
        onClick={() => setIsProfileMenuOpen((previous) => !previous)}
        onKeyDown={handleKeyDown}
        size={ButtonSize.SMALL}
        ref={profileBtnRef}
      ></Button>
      <div
        id={profileMenuId}
        data-testid="header-dropdown-menu-div"
        aria-hidden={!isProfileMenuOpen}
        className={`${styles['profile-menu-panel-wrapper']} ${
          isProfileMenuOpen ? styles['profile-menu-panel-wrapper-open'] : ''
        }`}
      >
        <div className={styles['profile-menu-panel-wrapper-close']}>
          <Button
            aria-label="Fermer le menu de profil"
            icon={fullCloseIcon}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            onClick={closeProfileMenu}
            onKeyDown={handleKeyDown}
          ></Button>
        </div>
        <div className={styles['profile-menu-details']}>
          <p className={styles['profile-menu-details-title']}>Profil</p>
          <p className={styles['profile-menu-details-email']}>
            {currentUser?.email}
          </p>
          {!IN_STRUCTURE_CREATION_FUNNEL && (
            <Button
              as="router-link"
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={fullProfilIcon}
              to="/profil"
              label="Voir mon profil"
              aria-current={isCurrentPageProfilePage ? 'page' : undefined}
              onKeyDown={handleKeyDown}
            />
          )}
          <hr
            aria-hidden
            className={styles['profile-menu-details-separator']}
          ></hr>
          <Button
            icon={fullLogoutIcon}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            onClick={logEventAndLogout}
            label="Se déconnecter"
            onKeyDown={handleKeyDown}
          />
        </div>
      </div>
    </div>
  )
}
