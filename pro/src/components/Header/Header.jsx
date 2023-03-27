import React, { useCallback } from 'react'
import { NavLink, useNavigate, useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import { CalendarIcon } from 'icons'
import { ReactComponent as IconDesk } from 'icons/ico-desk.svg'
import { ReactComponent as IconEuro } from 'icons/ico-euro.svg'
import { ReactComponent as IconHome } from 'icons/ico-home.svg'
import { ReactComponent as IconOffers } from 'icons/ico-offers.svg'
import { ReactComponent as IconSignout } from 'icons/ico-signout.svg'
import { ReactComponent as StatsIcon } from 'icons/ico-stats.svg'
import Logo from 'ui-kit/Logo/Logo'

const Header = () => {
  const { currentUser } = useCurrentUser()
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
          <Logo
            className="nav-item"
            isUserAdmin={currentUser.isAdmin}
            onClick={() => {
              logEvent?.(Events.CLICKED_PRO, { from: location.pathname })
            }}
          />
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
            <IconHome aria-hidden className="nav-item-icon" />
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
            <IconDesk aria-hidden className="nav-item-icon" />
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
            <IconEuro aria-hidden className="nav-item-icon" />
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
