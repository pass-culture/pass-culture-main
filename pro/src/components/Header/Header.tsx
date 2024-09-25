import cn from 'classnames'
import { ForwardedRef, forwardRef } from 'react'
import { NavLink, useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
// import { appLogo } from 'appConfig'
import { AppLogo } from 'appConfig'
import { HeaderHelpDropdown } from 'components/Header/HeaderHelpDropdown/HeaderHelpDropdown'
import { Events } from 'core/FirebaseEvents/constants'
import fullBurgerIcon from 'icons/full-burger.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Header.module.scss'
import { HeaderDropdown } from './HeaderDropdown/HeaderDropdown'
import { Headeri18nDropdown } from './Headeri18nDropdown/Headeri18nDropdown'

type HeaderProps = {
  lateralPanelOpen?: boolean
  setLateralPanelOpen?: (state: boolean) => void
  focusCloseButton?: () => void
  disableHomeLink?: boolean
}

export const Header = forwardRef(
  (
    {
      lateralPanelOpen = false,
      setLateralPanelOpen = () => undefined,
      focusCloseButton = () => undefined,
      disableHomeLink = false,
    }: HeaderProps,
    openButtonRef: ForwardedRef<HTMLButtonElement>
  ) => {
    const { logEvent } = useAnalytics()
    const location = useLocation()

    return (
      <header className={styles['top-menu']} id="top-navigation">
        <div className={styles['top-menu-content']}>
          {!disableHomeLink && (
            <Button
              ref={openButtonRef}
              aria-expanded={lateralPanelOpen}
              className={styles['burger-icon']}
              variant={ButtonVariant.TERNARY}
              onClick={() => {
                setLateralPanelOpen(!lateralPanelOpen)
                focusCloseButton()
              }}
              aria-label="Menu"
              aria-controls="lateral-panel"
            >
              <SvgIcon src={fullBurgerIcon} alt="" width="24" />
            </Button>
          )}
          <div className={styles['nav-brand']}>
            {disableHomeLink ? (
              <div className={cn(styles['logo'], styles['logo-link-disabled'])}>
                <AppLogo />
                {/* <SvgIcon
                  alt="Pass Culture pro, l’espace des acteurs culturels"
                  src={appLogo.name}
                  viewBox={appLogo.viewBox}
                  width={appLogo.width}
                /> */}
              </div>
            ) : (
              <NavLink
                className={styles['logo']}
                to="/accueil"
                onClick={() => {
                  logEvent(Events.CLICKED_PRO, { from: location.pathname })
                }}
              >
                <AppLogo />
              </NavLink>
            )}
          </div>
          <div className={styles['tablet-and-above']}>
            <HeaderHelpDropdown />
          </div>
          <HeaderDropdown />
          <Headeri18nDropdown />
        </div>
      </header>
    )
  }
)
Header.displayName = 'Header'
