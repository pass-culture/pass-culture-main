import classnames from 'classnames'
import { useEffect } from 'react'

import { SideNavLinks } from 'components/SideNavLinks/SideNavLinks'
import logoPassCultureProIcon from 'icons/logo-pass-culture-pro.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './LateralPanel.module.scss'

interface LateralPanelProps {
  lateralPanelOpen: boolean
  setLateralPanelOpen: (value: boolean) => void
  openButtonRef: React.RefObject<HTMLButtonElement>
  closeButtonRef: React.RefObject<HTMLButtonElement>
  navPanel: React.RefObject<HTMLDivElement>
}

export const LateralPanel = ({
  lateralPanelOpen,
  setLateralPanelOpen,
  openButtonRef,
  closeButtonRef,
  navPanel,
}: LateralPanelProps) => {
  useEffect(() => {
    const modalElement = navPanel.current
    if (!modalElement) {
      return () => {}
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
          lastElement?.focus()
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault()
          firstElement?.focus()
        }
      }
    }

    if (lateralPanelOpen) {
      modalElement.addEventListener('keydown', handleTabKeyPress)
    }

    return () => {
      modalElement.removeEventListener('keydown', handleTabKeyPress)
    }
  }, [lateralPanelOpen, navPanel])

  return (
    <nav
      id="lateral-panel"
      className={classnames({
        [styles['lateral-panel-wrapper'] ?? '']: true,
        [styles['lateral-panel-wrapper-open'] ?? '']: lateralPanelOpen,
      })}
      ref={navPanel}
      aria-label="Menu principal"
    >
      <div className={styles['lateral-panel-menu']}>
        {lateralPanelOpen && (
          <div
            className={classnames({
              [styles['lateral-panel-nav'] ?? '']: true,
              [styles['lateral-panel-nav-open'] ?? '']: lateralPanelOpen,
            })}
          >
            <Button
              aria-expanded={lateralPanelOpen}
              variant={ButtonVariant.TERNARY}
              onClick={() => {
                setLateralPanelOpen(!lateralPanelOpen)
                openButtonRef.current?.focus()
              }}
              aria-label="Fermer"
              aria-controls="lateral-panel"
              ref={closeButtonRef}
              className={styles['lateral-panel-nav-button']}
            >
              <SvgIcon src={strokeCloseIcon} alt="" width="24" />
            </Button>
            <SvgIcon
              alt="Pass Culture pro, l’espace des acteurs culturels"
              src={logoPassCultureProIcon}
              viewBox="0 0 119 40"
              width="119"
              className={styles['lateral-panel-logo']}
            />
          </div>
        )}
        <SideNavLinks isLateralPanelOpen={lateralPanelOpen} />
      </div>
    </nav>
  )
}
