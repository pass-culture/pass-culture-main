import cn from 'classnames'
import React, { useEffect, useState } from 'react'
import type { HitsProvided } from 'react-instantsearch-core'
import { connectHits } from 'react-instantsearch-dom'
import { NavLink } from 'react-router-dom'

import { AdageFrontRoles } from 'apiClient/adage'
import { AdageHeaderLink } from 'apiClient/adage/models/AdageHeaderLink'
import { apiAdage } from 'apiClient/api'
import useNotification from 'hooks/useNotification'
import { CalendarCheckIcon, InstitutionIcon, SearchIcon } from 'icons'
import { ReactComponent as FullDownloadIcon } from 'icons/full-download.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Icon from 'ui-kit/Icon/Icon'
import { formatPrice } from 'utils/formatPrice'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'
import { ResultType } from 'utils/types'

import { getEducationalInstitutionWithBudgetAdapter } from '../../adapters/getEducationalInstitutionWithBudgetAdapter'
import useAdageUser from '../../hooks/useAdageUser'

import styles from './AdageHeader.module.scss'

export const AdageHeaderComponent = ({ hits }: HitsProvided<ResultType>) => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')
  const notify = useNotification()
  const adageUser = useAdageUser()

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
    if (adageUser.role !== AdageFrontRoles.READONLY) {
      getEducationalInstitutionBudget()
    }
  }, [adageUser.role])

  const logAdageLinkClick = (headerLinkName: AdageHeaderLink) => {
    apiAdage.logHeaderLinkClick({
      AdageHeaderFrom: removeParamsFromUrl(location.pathname),
      header_link_name: headerLinkName,
    })
  }
  return (
    <div className={styles['adage-header-container']}>
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
            onClick={() => logAdageLinkClick(AdageHeaderLink.SEARCH)}
          >
            <SearchIcon className={styles['adage-header-item-icon']} />
            Rechercher
          </NavLink>
          {adageUser.role !== AdageFrontRoles.READONLY && (
            <NavLink
              to={`/adage-iframe/mon-etablissement?token=${adageAuthToken}`}
              className={({ isActive }) => {
                return cn(styles['adage-header-item'], {
                  [styles['adage-header-item-active']]: isActive,
                })
              }}
              onClick={() =>
                logAdageLinkClick(AdageHeaderLink.MY_INSTITUTION_OFFERS)
              }
            >
              <InstitutionIcon className={styles['adage-header-item-icon']} />
              Pour mon établissement
              <div className={styles['adage-header-nb-hits']}>
                {hits.length}
              </div>
            </NavLink>
          )}
          <a
            href={`${document.referrer}adage/passculture/index`}
            className={styles['adage-header-item']}
            target="_parent"
            onClick={() => logAdageLinkClick(AdageHeaderLink.ADAGE_LINK)}
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
                Solde prévisionnel
                <span className={styles['adage-header-budget']}>
                  {formatPrice(institutionBudget)}
                </span>
              </div>
            </a>
          </div>
        )}
      </nav>
      <div className={styles['adage-header-help']}>
        Besoin d'aide pour réserver des offres pass Culture ?
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: `${document.referrer}adage/index/docGet/format/pptx/doc/PRESENTATION_J_UTILISE_PASS_CULTURE`,
            isExternal: true,
          }}
          Icon={FullDownloadIcon}
        >
          Télécharger l'aide
        </ButtonLink>
      </div>
    </div>
  )
}

export const AdageHeader = connectHits(AdageHeaderComponent)
