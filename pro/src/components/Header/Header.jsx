import classnames from 'classnames'
import React, { useCallback } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { CalendarIcon } from 'icons'
import { ReactComponent as IconOffers } from 'icons/ico-offers.svg'
import { ReactComponent as IconSignout } from 'icons/ico-signout.svg'
import { ReactComponent as StatsIcon } from 'icons/ico-stats.svg'
import deskIcon from 'icons/stroke-desk.svg'
import strokeEuro from 'icons/stroke-euro.svg'
import strokeHome from 'icons/stroke-home.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { ROOT_PATH } from 'utils/config'

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
      <nav>
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
              src={`${ROOT_PATH}/icons/logo-pass-culture-header.svg`}
              viewBox="0 0 119 40"
            />
          </NavLink>
        </div>

        <div className="nav-menu">
          <NavLink
            className="nav-item"
            onClick={() => {
              logEvent?.(Events.CLICKED_HOME, { from: location.pathname })
            }}
            role="menuitem"
            to={'/accueil'}
          >
            <SvgIcon className="nav-item-icon" src={strokeHome} alt="" />
            Accueil
          </NavLink>

          <NavLink
            className="nav-item"
            onClick={() => {
              logEvent?.(Events.CLICKED_TICKET, { from: location.pathname })
            }}
            role="menuitem"
            to="/guichet"
          >
            <SvgIcon className="nav-item-icon" src={deskIcon} alt="" />
            Guichet
          </NavLink>

          <NavLink
            className="nav-item"
            onClick={() => {
              logEvent?.(Events.CLICKED_OFFER, { from: location.pathname })
            }}
            role="menuitem"
            to="/offres"
          >
            <IconOffers aria-hidden className="nav-item-icon" />
            Offres
          </NavLink>

          <NavLink
            className="nav-item"
            onClick={() => {
              logEvent?.(Events.CLICKED_BOOKING, { from: location.pathname })
            }}
            role="menuitem"
            to="/reservations"
          >
            <CalendarIcon aria-hidden className="nav-item-icon" />
            Réservations
          </NavLink>

          <NavLink
            className="nav-item"
            onClick={() => {
              logEvent?.(Events.CLICKED_REIMBURSEMENT, {
                from: location.pathname,
              })
            }}
            role="menuitem"
            to="/remboursements/justificatifs"
          >
            <SvgIcon className="nav-item-icon" src={strokeEuro} alt="" />
            Remboursements
          </NavLink>

          {isOffererStatsActive && (
            <NavLink
              className="nav-item"
              onClick={() => {
                logEvent?.(Events.CLICKED_STATS, {
                  from: location.pathname,
                })
              }}
              role="menuitem"
              to="/statistiques"
            >
              <StatsIcon aria-hidden className="nav-item-icon" />
              Statistiques
            </NavLink>
          )}

          <div className="separator" />

          <button
            className="nav-item icon-only"
            onClick={onSignoutClick}
            role="menuitem"
            type="button"
          >
            <IconSignout className="nav-item-icon signout-icon" />
          </button>
        </div>
      </nav>
    </header>
  )
}

export default Header
