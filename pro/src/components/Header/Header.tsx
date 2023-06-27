import React, { useCallback } from 'react'
import { NavLink, useNavigate, useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

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
        <div className="nav-brand">logo </div>

        <div className="nav-menu">
          <NavLink
            className="nav-item"
            onClick={() => {
              logEvent?.(Events.CLICKED_HOME, { from: location.pathname })
            }}
            role="menuitem"
            to={'/accueil'}
          >
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
            signout
          </button>
        </div>
      </nav>
    </header>
  )
}

export default Header
