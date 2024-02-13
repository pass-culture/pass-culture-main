import cn from 'classnames'
import { ForwardedRef, forwardRef } from 'react'
import { NavLink, useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import fullBurgerIcon from 'icons/full-burger.svg'
import fullLogoutIcon from 'icons/full-logout.svg'
import logoPassCultureProIcon from 'icons/logo-pass-culture-pro.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import deskIcon from 'icons/stroke-desk.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHomeIcon from 'icons/stroke-home.svg'
import strokeLogoutIcon from 'icons/stroke-logout.svg'
import strokeOffersIcon from 'icons/stroke-offers.svg'
import strokePieIcon from 'icons/stroke-pie.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Header.module.scss'

const NAV_ITEM_ICON_SIZE = '24'

type HeaderProps = {
  lateralPanelOpen?: boolean
  isTopMenuVisible?: boolean
  setLateralPanelOpen?: (state: boolean) => void
  focusCloseButton?: () => void
}
const Header = forwardRef(
  (
    {
      lateralPanelOpen = false,
      isTopMenuVisible = false,
      setLateralPanelOpen = () => undefined,
      focusCloseButton = () => undefined,
    }: HeaderProps,
    openButtonRef: ForwardedRef<HTMLButtonElement>
  ) => {
    const { logEvent } = useAnalytics()
    const location = useLocation()
    const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
    const isNewSideBarNavigation = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')

    if (isNewSideBarNavigation && isTopMenuVisible) {
      return (
        <header className={styles['top-menu']} id="top-navigation">
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
          <div className={styles['nav-brand']}>
            <NavLink
              className={styles['logo']}
              to={'/accueil'}
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
          </div>

          {/* These buttons do the same.
            The first one is displayed only on tablet and smaller to get rid of the right margin (and has an alt)
            The second one is displayed on larger screen sizes
        */}
          <NavLink
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
              width="20"
            />
          </NavLink>
          <NavLink
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
          </NavLink>
        </header>
      )
    }

    return (
      <header className={styles['menu-v2']} id="header-navigation">
        <nav className={styles['nav']} aria-label="Menu principal">
          <div className={styles['nav-brand']}>
            <NavLink
              className={cn('logo', 'nav-item')}
              to={'/accueil'}
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
          </div>

          <ul className={styles['nav-menu']}>
            <li>
              <NavLink
                className={({ isActive }) =>
                  cn(styles['nav-item'], {
                    [styles['nav-item-selected']]: isActive,
                  })
                }
                onClick={() => {
                  logEvent?.(Events.CLICKED_HOME, { from: location.pathname })
                }}
                to={'/accueil'}
              >
                <SvgIcon
                  className={styles['nav-item-icon']}
                  src={strokeHomeIcon}
                  alt=""
                  width={NAV_ITEM_ICON_SIZE}
                />
                Accueil
              </NavLink>
            </li>
            <li>
              <NavLink
                className={({ isActive }) =>
                  cn(styles['nav-item'], {
                    [styles['nav-item-selected']]: isActive,
                  })
                }
                onClick={() => {
                  logEvent?.(Events.CLICKED_TICKET, { from: location.pathname })
                }}
                to="/guichet"
              >
                <SvgIcon
                  className={styles['nav-item-icon']}
                  src={deskIcon}
                  alt=""
                  width={NAV_ITEM_ICON_SIZE}
                />
                Guichet
              </NavLink>
            </li>
            <li>
              <NavLink
                className={({ isActive }) =>
                  cn(styles['nav-item'], {
                    [styles['nav-item-selected']]: isActive,
                  })
                }
                onClick={() => {
                  logEvent?.(Events.CLICKED_OFFER, { from: location.pathname })
                }}
                to="/offres"
              >
                <SvgIcon
                  className={styles['nav-item-icon']}
                  src={strokeOffersIcon}
                  alt=""
                  width={NAV_ITEM_ICON_SIZE}
                />
                Offres
              </NavLink>
            </li>
            <li>
              <NavLink
                className={({ isActive }) =>
                  cn(styles['nav-item'], {
                    [styles['nav-item-selected']]: isActive,
                  })
                }
                onClick={() => {
                  logEvent?.(Events.CLICKED_BOOKING, {
                    from: location.pathname,
                  })
                }}
                to="/reservations"
              >
                <SvgIcon
                  alt=""
                  src={strokeCalendarIcon}
                  className={styles['nav-item-icon']}
                  width={NAV_ITEM_ICON_SIZE}
                />
                Réservations
              </NavLink>
            </li>
            <li>
              <NavLink
                className={({ isActive }) =>
                  cn(styles['nav-item'], {
                    [styles['nav-item-selected']]: isActive,
                  })
                }
                onClick={() => {
                  logEvent?.(Events.CLICKED_REIMBURSEMENT, {
                    from: location.pathname,
                  })
                }}
                to="/remboursements/justificatifs"
              >
                <SvgIcon
                  className={styles['nav-item-icon']}
                  src={strokeEuroIcon}
                  alt=""
                  width={NAV_ITEM_ICON_SIZE}
                />
                Gestion financière
              </NavLink>
            </li>
            {isOffererStatsActive && (
              <li>
                <NavLink
                  className={({ isActive }) =>
                    cn(styles['nav-item'], {
                      [styles['nav-item-selected']]: isActive,
                    })
                  }
                  onClick={() => {
                    logEvent?.(Events.CLICKED_STATS, {
                      from: location.pathname,
                    })
                  }}
                  to="/statistiques"
                >
                  <SvgIcon
                    src={strokePieIcon}
                    alt=""
                    className={styles['nav-item-icon']}
                    width={NAV_ITEM_ICON_SIZE}
                  />
                  Statistiques
                </NavLink>
              </li>
            )}
            <li>
              <div className={styles['separator']} />

              <NavLink
                className={cn(styles['nav-item'], styles['icon-only'])}
                onClick={() =>
                  logEvent?.(Events.CLICKED_LOGOUT, { from: location.pathname })
                }
                to={`${location.pathname}?logout`}
                data-testid="logout-link"
                title="Déconnexion"
              >
                <SvgIcon
                  src={strokeLogoutIcon}
                  alt="Déconnexion"
                  className={cn(
                    styles['nav-item-icon'],
                    styles['signout-icon']
                  )}
                  width={NAV_ITEM_ICON_SIZE}
                />
              </NavLink>
            </li>
          </ul>
        </nav>
      </header>
    )
  }
)
Header.displayName = 'Header'

export default Header
