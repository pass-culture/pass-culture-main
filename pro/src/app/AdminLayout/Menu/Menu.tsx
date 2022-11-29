import React from 'react'
import { NavLink } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import { ReactComponent as IconCalendar } from 'icons/ico-calendar.svg'
import { ReactComponent as IconDesk } from 'icons/ico-desk.svg'
import { ReactComponent as IconEuro } from 'icons/ico-euro.svg'
import { ReactComponent as IconHome } from 'icons/ico-home.svg'
import { ReactComponent as IconOffers } from 'icons/ico-offers.svg'
import { ReactComponent as StatsIcon } from 'icons/ico-stats.svg'

import styles from './Menu.module.scss'

const Menu = () => {
  const { currentUser } = useCurrentUser()
  const { logEvent } = useAnalytics()
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')

  return (
    <nav className={styles['menu']}>
      <NavLink
        className={styles['nav-item']}
        onClick={() => {
          logEvent?.(Events.CLICKED_HOME, { from: location.pathname })
        }}
        role="menuitem"
        to={currentUser.isAdmin ? '/structures' : '/accueil'}
      >
        <IconHome aria-hidden className={styles['nav-item-icon']} />
        Accueil
      </NavLink>

      <NavLink
        className={styles['nav-item']}
        onClick={() => {
          logEvent?.(Events.CLICKED_TICKET, { from: location.pathname })
        }}
        role="menuitem"
        to="/guichet"
      >
        <IconDesk aria-hidden className={styles['nav-item-icon']} />
        Guichet
      </NavLink>

      <NavLink
        className={styles['nav-item']}
        onClick={() => {
          logEvent?.(Events.CLICKED_OFFER, { from: location.pathname })
        }}
        role="menuitem"
        to="/offres"
      >
        <IconOffers aria-hidden className={styles['nav-item-icon']} />
        Offres
      </NavLink>

      <NavLink
        className={styles['nav-item']}
        onClick={() => {
          logEvent?.(Events.CLICKED_BOOKING, { from: location.pathname })
        }}
        role="menuitem"
        to="/reservations"
      >
        <IconCalendar aria-hidden className={styles['nav-item-icon']} />
        Réservations
      </NavLink>

      <NavLink
        className={styles['nav-item']}
        onClick={() => {
          logEvent?.(Events.CLICKED_REIMBURSEMENT, {
            from: location.pathname,
          })
        }}
        role="menuitem"
        to="/remboursements/justificatifs"
      >
        <IconEuro aria-hidden className={styles['nav-item-icon']} />
        Remboursements
      </NavLink>

      {isOffererStatsActive && (
        <NavLink
          className={styles['nav-item']}
          onClick={() => {
            logEvent?.(Events.CLICKED_STATS, {
              from: location.pathname,
            })
          }}
          role="menuitem"
          to="/statistiques"
        >
          <StatsIcon aria-hidden className={styles['nav-item-icon']} />
          Statistiques
        </NavLink>
      )}
    </nav>
  )
}

export default Menu
