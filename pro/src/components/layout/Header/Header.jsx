import PropTypes from 'prop-types'
import React, { useCallback } from 'react'
import { useDispatch } from 'react-redux'
import { NavLink, useHistory } from 'react-router-dom'
import { reinitializeData } from 'redux-saga-data'

import { signout } from 'repository/pcapi/pcapi'
import { resetIsInitialized } from 'store/user/actions'

import Logo from '../Logo'

import { ReactComponent as BookingsSvg } from './assets/bookings.svg'
import { ReactComponent as CounterSvg } from './assets/counter.svg'
import { ReactComponent as HomeSvg } from './assets/home.svg'
import { ReactComponent as OffersSvg } from './assets/offers.svg'
import { ReactComponent as RefundsSvg } from './assets/refunds.svg'
import { ReactComponent as SignoutSvg } from './assets/signout.svg'
import { ReactComponent as StyleguideSvg } from './assets/styleguide.svg'

const Header = ({ isStyleguideActive, isUserAdmin }) => {
  const dispatch = useDispatch()
  const history = useHistory()

  const onSignoutClick = useCallback(() => {
    signout().then(() => {
      dispatch(resetIsInitialized())
      dispatch(reinitializeData())
      history.push('/connexion')
    })
  }, [dispatch, history])

  return (
    <header className="menu-v2">
      <nav>
        <div className="nav-brand">
          <Logo className="nav-item" isUserAdmin={isUserAdmin} />
        </div>

        <div className="nav-menu">
          <NavLink
            className="nav-item"
            role="menuitem"
            to={isUserAdmin ? '/structures' : '/accueil'}
          >
            <HomeSvg aria-hidden />
            Accueil
          </NavLink>

          <NavLink className="nav-item" role="menuitem" to="/guichet">
            <CounterSvg aria-hidden />
            Guichet
          </NavLink>

          <NavLink className="nav-item" role="menuitem" to="/offres">
            <OffersSvg aria-hidden />
            Offres
          </NavLink>

          <NavLink className="nav-item" role="menuitem" to="/reservations">
            <BookingsSvg aria-hidden />
            Réservations
          </NavLink>

          <NavLink
            className="nav-item"
            role="menuitem"
            to="/remboursements/justificatifs"
          >
            <RefundsSvg aria-hidden />
            Remboursements
          </NavLink>

          <div className="separator" />

          {isStyleguideActive && (
            <NavLink
              className="nav-item icon-only"
              data-testid="styleguide"
              role="menuitem"
              to="/styleguide"
            >
              <StyleguideSvg />
            </NavLink>
          )}

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

Header.propTypes = {
  isStyleguideActive: PropTypes.bool.isRequired,
  isUserAdmin: PropTypes.bool.isRequired,
}

export default Header
