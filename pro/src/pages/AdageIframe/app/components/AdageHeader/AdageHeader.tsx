import cn from 'classnames'
import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { AdageFrontRoles, AdageHeaderLink } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import useNotification from 'hooks/useNotification'
import fullDownloadIcon from 'icons/full-download.svg'
import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

import useAdageUser from '../../hooks/useAdageUser'

import styles from './AdageHeader.module.scss'
import AdageHeaderBudget from './AdageHeaderBudget/AdageHeaderBudget'
import { AdageHeaderMenu } from './AdageHeaderMenu/AdageHeaderMenu'

export const AdageHeader = () => {
  const notify = useNotification()
  const { adageUser } = useAdageUser()

  const [isLoading, setIsLoading] = useState(true)
  const [institutionBudget, setInstitutionBudget] = useState(0)
  const { pathname } = useLocation()

  const isDiscoveryPage = pathname === '/adage-iframe/decouverte'

  function logAdageLinkClick(headerLinkName: AdageHeaderLink) {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    apiAdage.logHeaderLinkClick({
      iframeFrom: location.pathname,
      header_link_name: headerLinkName,
    })
  }

  useEffect(() => {
    async function getEducationalInstitutionBudget() {
      try {
        const payload = await apiAdage.getEducationalInstitutionWithBudget()
        setInstitutionBudget(payload.budget)
      } catch (e) {
        notify.error(GET_DATA_ERROR_MESSAGE)

        sendSentryCustomError(e, { uai: adageUser.uai })
      } finally {
        setIsLoading(false)
      }
    }

    if (adageUser.role !== AdageFrontRoles.READONLY) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      getEducationalInstitutionBudget()
    }
  }, [adageUser.role, notify])

  return (
    <div
      className={cn([styles['adage-header']], {
        [styles['adage-header-discovery']]: isDiscoveryPage,
      })}
    >
      <nav className={styles['adage-header-nav']}>
        <div className={styles['adage-header-nav-brand']}>
          <SvgIcon
            src={logoPassCultureIcon}
            alt="Logo du pass Culture"
            width="109"
            viewBox="0 0 71 24"
          />
        </div>
        <AdageHeaderMenu logAdageLinkClick={logAdageLinkClick} />
        {!isLoading && (
          <AdageHeaderBudget
            institutionBudget={institutionBudget}
            logAdageLinkClick={logAdageLinkClick}
          />
        )}
      </nav>
      {adageUser.role !== AdageFrontRoles.READONLY && !isDiscoveryPage && (
        <div className={styles['adage-header-help']}>
          Besoin d’aide pour réserver des offres pass Culture ?
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: `${document.referrer}adage/index/docGet/format/pptx/doc/PRESENTATION_J_UTILISE_PASS_CULTURE`,
              isExternal: true,
              download: true,
            }}
            icon={fullDownloadIcon}
          >
            Télécharger l’aide
          </ButtonLink>
        </div>
      )}
    </div>
  )
}
