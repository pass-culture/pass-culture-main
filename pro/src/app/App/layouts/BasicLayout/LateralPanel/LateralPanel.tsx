/** biome-ignore-all lint/correctness/useUniqueElementIds: LateralPanel is used once per page. There cannot be id duplications. */
import classnames from 'classnames'
import { useEffect } from 'react'

import { noop } from '@/commons/utils/noop'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import logoPassCultureProIcon from '@/icons/logo-pass-culture-pro.svg'
import strokeCloseIcon from '@/icons/stroke-close.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { AdminSideNavLinks } from './components/AdminSideNavLinks'
import { HubPageNavigation } from './components/HubPageNavigation'
import { SideNavLinks } from './components/SideNavLinks'
import styles from './LateralPanel.module.scss'

interface LateralPanelProps {
  closeButtonRef: React.RefObject<HTMLButtonElement>
  isAdminArea?: boolean
  isHubPage?: boolean
  isOpen: boolean
  navPanel: React.RefObject<HTMLDivElement>
  openButtonRef: React.RefObject<HTMLButtonElement>
  onToggle: (value: boolean) => void
}

export const LateralPanel = ({
  closeButtonRef,
  isAdminArea = false,
  isHubPage = false,
  isOpen,
  navPanel,
  openButtonRef,
  onToggle,
}: LateralPanelProps) => {
  useEffect(() => {
    const modalElement = navPanel.current
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
  }, [isOpen, navPanel])

  return (
    <nav
      data-testid="lateral-panel"
      id="lateral-panel"
      tabIndex={-1}
      className={classnames({
        [styles['lateral-panel-wrapper']]: true,
        [styles['lateral-panel-wrapper-open']]: isOpen,
      })}
      ref={navPanel}
      aria-label="Menu principal"
    >
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

        {isHubPage && <HubPageNavigation isLateralPanelOpen={isOpen} />}
        {!isHubPage && (
          <>
            {!isAdminArea && <SideNavLinks isLateralPanelOpen={isOpen} />}
            {isAdminArea && <AdminSideNavLinks isLateralPanelOpen={isOpen} />}
          </>
        )}
      </div>
    </nav>
  )
}
