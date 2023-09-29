import React, { useEffect, useState } from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import useNotification from 'hooks/useNotification'
import fullDownloadIcon from 'icons/full-download.svg'
import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { formatPrice } from 'utils/formatPrice'

import { getEducationalInstitutionWithBudgetAdapter } from '../../adapters/getEducationalInstitutionWithBudgetAdapter'
import useAdageUser from '../../hooks/useAdageUser'

import styles from './AdageHeader.module.scss'
import { AdageHeaderMenu } from './AdageHeaderMenu/AdageHeaderMenu'

export const AdageHeader = () => {
  const notify = useNotification()
  const { adageUser } = useAdageUser()

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

  return (
    <div className={styles['adage-header']}>
      <nav className={styles['adage-header-nav']}>
        <div className={styles['adage-header-nav-brand']}>
          <SvgIcon
            src={logoPassCultureIcon}
            alt="Logo du pass Culture"
            width="120"
            viewBox="0 0 71 24"
          />
        </div>
        <AdageHeaderMenu adageUser={adageUser} />
        {!isLoading && (
          <div className={styles['adage-header-nav-menu-budget']}>
            <div className={styles['adage-header-separator']}></div>
            <div className={styles['adage-budget-text']}>
              Solde prévisionnel
              <span className={styles['adage-header-budget']}>
                {formatPrice(institutionBudget)}
              </span>
            </div>
          </div>
        )}
      </nav>
      {adageUser.role !== AdageFrontRoles.READONLY && (
        <div className={styles['adage-header-help']}>
          Besoin d'aide pour réserver des offres pass Culture ?
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: `${document.referrer}adage/index/docGet/format/pptx/doc/PRESENTATION_J_UTILISE_PASS_CULTURE`,
              isExternal: true,
              download: true,
              rel: 'noreferrer',
              target: '_blank',
            }}
            icon={fullDownloadIcon}
          >
            Télécharger l'aide
          </ButtonLink>
        </div>
      )}
    </div>
  )
}
