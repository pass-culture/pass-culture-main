import cn from 'classnames'
import React from 'react'
import type { HitsProvided } from 'react-instantsearch-core'
import { connectHits } from 'react-instantsearch-dom'
import { NavLink } from 'react-router-dom'

import { CalendarCheckIcon, InstitutionIcon, SearchIcon } from 'icons'
import Icon from 'ui-kit/Icon/Icon'
import { ResultType } from 'utils/types'

import styles from './AdageHeader.module.scss'

export const AdageHeaderComponent = ({ hits }: HitsProvided<ResultType>) => {
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
          <div className={styles['adage-header-nb-hits']}>{hits.length}</div>
        </NavLink>
        <a
          href={`${document.referrer}adage/passculture/index`}
          className={styles['adage-header-item']}
          target="_parent"
        >
          <CalendarCheckIcon className={styles['adage-header-item-icon']} />
          Suivi
        </a>
      </div>
    </nav>
  )
}

export const AdageHeader = connectHits(AdageHeaderComponent)
