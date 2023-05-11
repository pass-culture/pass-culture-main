import cn from 'classnames'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { CalendarCheckIcon, InstitutionIcon, SearchIcon } from 'icons'
import Icon from 'ui-kit/Icon/Icon'
import { REACT_APP_ADAGE_SUIVI_URL } from 'utils/config'

import styles from './AdageHeader.module.scss'

const AdageHeader = () => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')
  return (
    <nav className={styles['adage-header']}>
      <div className={styles['adage-header-brand']}>
        <Icon svg="logo-pass-culture-adage" alt="Logo du pass Culture" />
      </div>
      <div className={styles['adage-header-menu']}>
        <NavLink
          to={`/adage-iframe?token=${adageAuthToken}`}
          end
          className={({ isActive }) => {
            return cn(styles['adage-header-item'], {
              [styles['adage-header-item-active']]: isActive,
            })
          }}
        >
          <SearchIcon className={styles['adage-header-item-icon']} />
          Rechercher
        </NavLink>
        <NavLink
          to={`/adage-iframe/mon-etablissement?token=${adageAuthToken}`}
          className={({ isActive }) => {
            return cn(styles['adage-header-item'], {
              [styles['adage-header-item-active']]: isActive,
            })
          }}
        >
          <InstitutionIcon className={styles['adage-header-item-icon']} />
          Pour mon établissement
        </NavLink>
        <a
          href={REACT_APP_ADAGE_SUIVI_URL}
          className={styles['adage-header-item']}
        >
          <CalendarCheckIcon className={styles['adage-header-item-icon']} />
          Suivi
        </a>
      </div>
    </nav>
  )
}

export default AdageHeader
