import cn from 'classnames'
import { forwardRef } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import logoPassCultureProIcon from 'icons/logo-pass-culture-pro.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import deskIcon from 'icons/stroke-desk.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHomeIcon from 'icons/stroke-home.svg'
import strokeLogoutIcon from 'icons/stroke-logout.svg'
import strokeOffersIcon from 'icons/stroke-offers.svg'
import strokePieIcon from 'icons/stroke-pie.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OldHeader.module.scss'

const NAV_ITEM_ICON_SIZE = '24'

export const OldHeader = forwardRef(() => {
  const { logEvent } = useAnalytics()
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const location = useLocation()
  return (
    <header className={styles['menu-v2']} id="header-navigation">
      <nav className={styles['nav']} aria-label="Menu principal">
        <div className={styles['nav-brand']}>
          <NavLink
            className={cn('logo', 'nav-item')}
            to="/accueil"
            onClick={() => {
              logEvent(Events.CLICKED_PRO, { from: location.pathname })
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
                  [styles['nav-item-selected'] ?? '']: isActive,
                })
              }
              onClick={() => {
                logEvent(Events.CLICKED_HOME, { from: location.pathname })
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
                  [styles['nav-item-selected'] ?? '']: isActive,
                })
              }
              onClick={() => {
                logEvent(Events.CLICKED_TICKET, { from: location.pathname })
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
                  [styles['nav-item-selected'] ?? '']: isActive,
                })
              }
              onClick={() => {
                logEvent(Events.CLICKED_OFFER, { from: location.pathname })
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
                  [styles['nav-item-selected'] ?? '']: isActive,
                })
              }
              onClick={() => {
                logEvent(Events.CLICKED_BOOKING, {
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
                  [styles['nav-item-selected'] ?? '']: isActive,
                })
              }
              onClick={() => {
                logEvent(Events.CLICKED_REIMBURSEMENT, {
                  from: location.pathname,
                })
              }}
              to="/remboursements"
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
                    [styles['nav-item-selected'] ?? '']: isActive,
                  })
                }
                onClick={() => {
                  logEvent(Events.CLICKED_STATS, {
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

            <Link
              className={cn(styles['nav-item'], styles['icon-only'])}
              onClick={() =>
                logEvent(Events.CLICKED_LOGOUT, { from: location.pathname })
              }
              to={`${location.pathname}?logout`}
              data-testid="logout-link"
              title="Déconnexion"
            >
              <SvgIcon
                src={strokeLogoutIcon}
                alt="Déconnexion"
                className={cn(styles['nav-item-icon'], styles['signout-icon'])}
                width={NAV_ITEM_ICON_SIZE}
              />
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  )
})
OldHeader.displayName = 'Header'
