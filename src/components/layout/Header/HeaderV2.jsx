import React from 'react'
import { useDispatch } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { reinitializeData } from 'redux-saga-data'

import { signout } from '../../../repository/pcapi/pcapi'
import Logo from '../Logo'

import { ReactComponent as BookingsSvg } from './assets/bookings.svg'
import { ReactComponent as CounterSvg } from './assets/counter.svg'
import { ReactComponent as HomeSvg } from './assets/home.svg'
import { ReactComponent as OffersSvg } from './assets/offers.svg'
import { ReactComponent as RefundsSvg } from './assets/refunds.svg'
import { ReactComponent as SignoutSvg } from './assets/signout.svg'

const HeaderV2 = () => {
  const dispatch = useDispatch()

  function onSignoutClick() {
    signout().then(() => {
      dispatch(reinitializeData())
    })
  }

  return (
    <header className="menu-v2">
      <nav>
        <div className="nav-brand">
          <Logo className="nav-item" />
        </div>

        <div className="nav-menu">
          <NavLink
            className="nav-item"
            role="menuitem"
            to="/accueil"
          >
            <HomeSvg />
            <span>
              {'Accueil'}
            </span>
          </NavLink>

          <NavLink
            className="nav-item"
            role="menuitem"
            to="/guichet"
          >
            <CounterSvg />
            <span>
              {'Guichet'}
            </span>
          </NavLink>

          <NavLink
            className="nav-item"
            role="menuitem"
            to="/offres"
          >
            <OffersSvg />
            <span>
              {'Offres'}
            </span>
          </NavLink>

          <NavLink
            className="nav-item"
            role="menuitem"
            to="/reservations"
          >
            <BookingsSvg />
            <span>
              {'Réservations'}
            </span>
          </NavLink>

          <NavLink
            className="nav-item"
            role="menuitem"
            to="/remboursements"
          >
            <RefundsSvg />
            <span>
              {'Remboursements'}
            </span>
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

export default HeaderV2
