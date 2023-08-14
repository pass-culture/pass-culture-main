import classnames from 'classnames'
import React, { useCallback } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import logoPassCultureProIcon from 'icons/logo-pass-culture-pro.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import deskIcon from 'icons/stroke-desk.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHomeIcon from 'icons/stroke-home.svg'
import strokeLogoutIcon from 'icons/stroke-logout.svg'
import strokeOffersIcon from 'icons/stroke-offers.svg'
import strokePieIcon from 'icons/stroke-pie.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

const NAV_ITEM_ICON_SIZE = '24'

const Header = () => {
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')

  const onSignoutClick = useCallback(() => {
    logEvent?.(Events.CLICKED_LOGOUT, { from: location.pathname })
    navigate('/logout')
  }, [navigate, logEvent, location.pathname])
  return (
    <header className="menu-v2" id="header-navigation">
      <nav aria-label="Menu principal">
        <div className="nav-brand">
          <NavLink
            className={classnames('logo', 'nav-item')}
            to={'/accueil'}
            onClick={() => {
              logEvent?.(Events.CLICKED_PRO, { from: location.pathname })
            }}
          >
            <SvgIcon
              alt="Pass Culture pro, l'espace des acteurs culturels"
              src={logoPassCultureProIcon}
              viewBox="0 0 119 40"
              width="119"
            />
          </NavLink>
        </div>

        <ul className="nav-menu">
          <li>
            <NavLink
              className="nav-item"
              onClick={() => {
                logEvent?.(Events.CLICKED_HOME, { from: location.pathname })
              }}
              to={'/accueil'}
            >
              <SvgIcon
                className="nav-item-icon"
                src={strokeHomeIcon}
                alt=""
                width={NAV_ITEM_ICON_SIZE}
              />
              Accueil
            </NavLink>
          </li>
          <li>
            <NavLink
              className="nav-item"
              onClick={() => {
                logEvent?.(Events.CLICKED_TICKET, { from: location.pathname })
              }}
              to="/guichet"
            >
              <SvgIcon
                className="nav-item-icon"
                src={deskIcon}
                alt=""
                width={NAV_ITEM_ICON_SIZE}
              />
              Guichet
            </NavLink>
          </li>
          <li>
            <NavLink
              className="nav-item"
              onClick={() => {
                logEvent?.(Events.CLICKED_OFFER, { from: location.pathname })
              }}
              to="/offres"
            >
              <SvgIcon
                className="nav-item-icon"
                src={strokeOffersIcon}
                alt=""
                width={NAV_ITEM_ICON_SIZE}
              />
              Offres
            </NavLink>
          </li>
          <li>
            <NavLink
              className="nav-item"
              onClick={() => {
                logEvent?.(Events.CLICKED_BOOKING, { from: location.pathname })
              }}
              to="/reservations"
            >
              <SvgIcon
                alt=""
                src={strokeCalendarIcon}
                className="nav-item-icon"
                width={NAV_ITEM_ICON_SIZE}
              />
              Réservations
            </NavLink>
          </li>
          <li>
            <NavLink
              className="nav-item"
              onClick={() => {
                logEvent?.(Events.CLICKED_REIMBURSEMENT, {
                  from: location.pathname,
                })
              }}
              to="/remboursements/justificatifs"
            >
              <SvgIcon
                className="nav-item-icon"
                src={strokeEuroIcon}
                alt=""
                width={NAV_ITEM_ICON_SIZE}
              />
              Remboursements
            </NavLink>
          </li>
          {isOffererStatsActive && (
            <li>
              <NavLink
                className="nav-item"
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
                  className="nav-item-icon"
                  width={NAV_ITEM_ICON_SIZE}
                />
                Statistiques
              </NavLink>
            </li>
          )}
          <li>
            <div className="separator" />

            <button
              className="nav-item icon-only"
              onClick={onSignoutClick}
              type="button"
            >
              <SvgIcon
                src={strokeLogoutIcon}
                alt="Déconnexion"
                className="nav-item-icon signout-icon"
                width={NAV_ITEM_ICON_SIZE}
              />
            </button>
          </li>
        </ul>
      </nav>
    </header>
  )
}

export default Header
