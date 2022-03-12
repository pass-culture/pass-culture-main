import cn from 'classnames'
import React, { useCallback } from 'react'
import { useDispatch } from 'react-redux'
import { NavLink, useHistory } from 'react-router-dom'
import { reinitializeData } from 'redux-saga-data'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { signout } from 'repository/pcapi/pcapi'
import { resetIsInitialized } from 'store/user/actions'

import Logo from '../Logo'

import { STYLEGUIDE_ACTIVE } from './_constants'
import { ReactComponent as BookingsSvg } from './assets/bookings.svg'
import { ReactComponent as CounterSvg } from './assets/counter.svg'
import { ReactComponent as HomeSvg } from './assets/home.svg'
import { ReactComponent as OffersSvg } from './assets/offers.svg'
import { ReactComponent as RefundsSvg } from './assets/refunds.svg'
import { ReactComponent as SignoutSvg } from './assets/signout.svg'
import { ReactComponent as StyleguideSvg } from './assets/styleguide.svg'
import styles from './Header.module.scss'

const Header = (): JSX.Element => {
  const dispatch = useDispatch()
  const history = useHistory()
  const { currentUser } = useCurrentUser()
  const isUserAdmin = currentUser.isAdmin

  const onSignoutClick = useCallback(() => {
    signout().then(() => {
      dispatch(resetIsInitialized())
      dispatch(reinitializeData())
      history.push('/connexion')
    })
  }, [dispatch, history])

  return (
    <header className={cn(styles['menu-v2'])}>
      <nav>
        <div className={cn(styles['nav-brand'])}>
          <Logo className={cn(styles['nav-item'])} isUserAdmin={isUserAdmin} />
        </div>

        <div className={cn(styles['nav-menu'])}>
          <NavLink
            className={cn(styles['nav-item'])}
            role="menuitem"
            to={isUserAdmin ? '/structures' : '/accueil'}
          >
            <HomeSvg aria-hidden />
            Accueil
          </NavLink>

          <NavLink
            className={cn(styles['nav-item'])}
            role="menuitem"
            to="/guichet"
          >
            <CounterSvg aria-hidden />
            Guichet
          </NavLink>

          <NavLink
            className={cn(styles['nav-item'])}
            role="menuitem"
            to="/offres"
          >
            <OffersSvg aria-hidden />
            Offres
          </NavLink>

          <NavLink
            className={cn(styles['nav-item'])}
            role="menuitem"
            to="/reservations"
          >
            <BookingsSvg aria-hidden />
            Réservations
          </NavLink>

          <NavLink
            className={cn(styles['nav-item'])}
            role="menuitem"
            to="/remboursements/justificatifs"
          >
            <RefundsSvg aria-hidden />
            Remboursements
          </NavLink>

          <div className="separator" />

          {STYLEGUIDE_ACTIVE && (
            <NavLink
              className={cn(styles['nav-item'], styles['icon-only'])}
              data-testid="styleguide"
              role="menuitem"
              to="/styleguide"
            >
              <StyleguideSvg />
            </NavLink>
          )}

          <button
            className={cn(styles['nav-item'], styles['icon-only'])}
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
