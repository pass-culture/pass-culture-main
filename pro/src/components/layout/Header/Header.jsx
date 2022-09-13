import React, { useCallback } from 'react'
import { useDispatch } from 'react-redux'
import { NavLink, useHistory, useLocation } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import useCurrentUser from 'components/hooks/useCurrentUser'
import { Events } from 'core/FirebaseEvents/constants'

import Logo from '../Logo'

import { ReactComponent as BookingsSvg } from './assets/bookings.svg'
import { ReactComponent as CounterSvg } from './assets/counter.svg'
import { ReactComponent as HomeSvg } from './assets/home.svg'
import { ReactComponent as OffersSvg } from './assets/offers.svg'
import { ReactComponent as RefundsSvg } from './assets/refunds.svg'
import { ReactComponent as SignoutSvg } from './assets/signout.svg'

const Header = () => {
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()
  const history = useHistory()
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const onSignoutClick = useCallback(() => {
    logEvent?.(Events.CLICKED_LOGOUT, { from: location.pathname })
    history.push('/logout')
  }, [dispatch, history, logEvent, location.pathname])
  return (
    <header className="menu-v2">
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
            to={currentUser.isAdmin ? '/structures' : '/accueil'}
          >
            <HomeSvg aria-hidden />
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
            <CounterSvg aria-hidden />
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
            <OffersSvg aria-hidden />
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
            <BookingsSvg aria-hidden />
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
            <RefundsSvg aria-hidden />
            Remboursements
          </NavLink>

          <div className="separator" />

          <button
            className="nav-item icon-only"
            onClick={onSignoutClick}
            role="menuitem"
            type="button"
          >
            <SignoutSvg />
          </button>
        </div>
      </nav>
    </header>
  )
}

export default Header
