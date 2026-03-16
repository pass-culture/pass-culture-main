/** biome-ignore-all lint/correctness/useUniqueElementIds: LateralPanel is used once per page. There cannot be id duplications. */
import classnames from 'classnames'
import { useEffect } from 'react'
import { createPortal } from 'react-dom'

import {
  LAPTOP_MEDIA_QUERY,
  useMediaQuery,
} from '@/commons/hooks/useMediaQuery'
import { noop } from '@/commons/utils/noop'
import { useSkipLinksContext } from '@/components/SkipLinks/SkipLinksContext'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullNextIcon from '@/icons/full-next.svg'
import logoPassCultureProIcon from '@/icons/logo-pass-culture-pro.svg'
import strokeCloseIcon from '@/icons/stroke-close.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { AdminSideNavLinks } from './AdminSideNav/AdminSideNav'
import { LateralMenu } from './LateralMenu/LateralMenu'
import styles from './LateralPanel.module.scss'

interface LateralPanelProps {
  closeButtonRef: React.RefObject<HTMLButtonElement | null>
  isAdminArea?: boolean
  isHubPage?: boolean
  isOpen: boolean
  navPanelRef: React.RefObject<HTMLDivElement | null>
  openButtonRef: React.RefObject<HTMLButtonElement | null>
  onToggle: (value: boolean) => void
}

export const LateralPanel = ({
  isAdminArea = false,
  isOpen,
  closeButtonRef,
  navPanelRef,
  openButtonRef,
  onToggle,
}: LateralPanelProps) => {
  useEffect(() => {
    const modalElement = navPanelRef.current
    if (!modalElement) {
      return () => noop
    }

    const focusableElements = modalElement.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    const handleTabKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault()
          lastElement.focus()
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault()
          firstElement.focus()
        }
      }
    }

    if (isOpen) {
      modalElement.addEventListener('keydown', handleTabKeyPress)
    }

    return () => {
      modalElement.removeEventListener('keydown', handleTabKeyPress)
    }
  }, [isOpen, navPanelRef])

  const { menuContainer } = useSkipLinksContext()

  // Gives the right target for the skip link button depending on the screen size.
  const skipLinkTarget = useMediaQuery(LAPTOP_MEDIA_QUERY)
    ? '#header-nav-toggle'
    : '#lateral-panel'

  return (
    <nav
      data-testid="lateral-panel"
      id="lateral-panel"
      tabIndex={-1}
      className={classnames({
        [styles['lateral-panel-wrapper']]: true,
        [styles['lateral-panel-wrapper-open']]: isOpen,
      })}
      ref={navPanelRef}
      aria-label="Menu principal"
    >
      {/* Skip link button to access the lateral panel menu (will be injected into the <SkipLinks> component via createPortal) */}
      {menuContainer &&
        createPortal(
          <Button
            as="a"
            to={skipLinkTarget}
            isExternal
            icon={fullNextIcon}
            label="Aller au menu"
            size={ButtonSize.SMALL}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
          />,
          menuContainer
        )}
      <div className={styles['lateral-panel-menu']}>
        {isOpen && (
          <div
            className={classnames({
              [styles['lateral-panel-nav']]: true,
              [styles['lateral-panel-nav-open']]: isOpen,
            })}
          >
            <SvgIcon
              alt="Pass Culture pro, l’espace des acteurs culturels"
              src={logoPassCultureProIcon}
              viewBox="0 0 119 40"
              width="119"
              className={styles['lateral-panel-logo']}
            />
            <Button
              aria-expanded={isOpen}
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              onClick={() => {
                onToggle(!isOpen)
                openButtonRef.current?.focus()
              }}
              aria-label="Fermer"
              aria-controls="lateral-panel"
              ref={closeButtonRef}
              icon={strokeCloseIcon}
            />
          </div>
        )}

        {isAdminArea ? (
          <AdminSideNavLinks />
        ) : (
          <LateralMenu isLateralPanelOpen={isOpen} />
        )}
      </div>
    </nav>
  )
}
