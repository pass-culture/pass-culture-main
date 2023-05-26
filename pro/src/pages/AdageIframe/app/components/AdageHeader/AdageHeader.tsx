import cn from 'classnames'
import React, { useEffect, useState } from 'react'
import type { HitsProvided } from 'react-instantsearch-core'
import { connectHits } from 'react-instantsearch-dom'
import { NavLink } from 'react-router-dom'

import useNotification from 'hooks/useNotification'
import { CalendarCheckIcon, InstitutionIcon, SearchIcon } from 'icons'
import Icon from 'ui-kit/Icon/Icon'
import { REACT_APP_ADAGE_SUIVI_URL } from 'utils/config'
import { ResultType } from 'utils/types'

import { getEducationalInstitutionWithBudgetAdapter } from '../../adapters/getEducationalInstitutionWithBudgetAdapter'

import styles from './AdageHeader.module.scss'

export const AdageHeaderComponent = ({ hits }: HitsProvided<ResultType>) => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')
  const notify = useNotification()

  const [isLoading, setIsLoading] = useState(true)
  const [institutionBudget, setInstitutionBudget] = useState(0)

  const getEducationalInstitutionBudget = async () => {
    const { isOk, payload, message } =
      await getEducationalInstitutionWithBudgetAdapter()

    if (!isOk) {
      return notify.error(message)
    }

    setInstitutionBudget(payload.budget)
    setIsLoading(false)
  }

  useEffect(() => {
    getEducationalInstitutionBudget()
  }, [])

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
          href={REACT_APP_ADAGE_SUIVI_URL}
          className={styles['adage-header-item']}
          target="_parent"
        >
          <CalendarCheckIcon className={styles['adage-header-item-icon']} />
          Suivi
        </a>
      </div>
      {!isLoading && (
        <div className={styles['adage-header-menu-budget']}>
          <a className={styles['adage-header-menu-budget-item']}>
            <div className={styles['adage-header-separator']}></div>
            <div className={styles['adage-budget-text']}>
              <span>Budget restant</span>
              <span className={styles['adage-header-budget']}>
                {institutionBudget.toLocaleString()}€
              </span>
            </div>
          </a>
        </div>
      )}
    </nav>
  )
}

export const AdageHeader = connectHits(AdageHeaderComponent)
