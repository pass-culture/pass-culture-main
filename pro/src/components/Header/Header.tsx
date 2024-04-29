import cn from 'classnames'
import { ForwardedRef, forwardRef } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullBurgerIcon from 'icons/full-burger.svg'
import fullLogoutIcon from 'icons/full-logout.svg'
import logoPassCultureProIcon from 'icons/logo-pass-culture-pro.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Header.module.scss'

type HeaderProps = {
  lateralPanelOpen?: boolean
  setLateralPanelOpen?: (state: boolean) => void
  focusCloseButton?: () => void
  disableHomeLink?: boolean
}
const Header = forwardRef(
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
                <SvgIcon
                  alt="Pass Culture pro, l’espace des acteurs culturels"
                  src={logoPassCultureProIcon}
                  viewBox="0 0 119 40"
                  width="119"
                />
              </div>
            ) : (
              <NavLink
                className={styles['logo']}
                to="/accueil"
                onClick={() => {
                  logEvent?.(Events.CLICKED_PRO, { from: location.pathname })
                }}
              >
                <SvgIcon
                  alt="Pass Culture pro, l’espace des acteurs culturels"
                  src={logoPassCultureProIcon}
                  viewBox="0 0 119 40"
                  width="119"
                />
              </NavLink>
            )}
          </div>

          {/* These buttons do the same.
            The first one is displayed only on tablet and smaller to get rid of the right margin (and has an alt)
            The second one is displayed on larger screen sizes
        */}
          <Link
            onClick={() =>
              logEvent?.(Events.CLICKED_LOGOUT, { from: location.pathname })
            }
            to={`${location.pathname}?logout}`}
            className={styles['logout-mobile']}
          >
            <SvgIcon
              className="nav-item-icon"
              src={fullLogoutIcon}
              alt="Se déconnecter"
              width="24"
            />
          </Link>
          <Link
            onClick={() =>
              logEvent?.(Events.CLICKED_LOGOUT, { from: location.pathname })
            }
            to={`${location.pathname}?logout}`}
            className={styles['logout']}
          >
            <SvgIcon
              className="nav-item-icon"
              src={fullLogoutIcon}
              alt=""
              width="20"
            />
            Se déconnecter
          </Link>
        </div>
      </header>
    )
  }
)
Header.displayName = 'Header'

export default Header
