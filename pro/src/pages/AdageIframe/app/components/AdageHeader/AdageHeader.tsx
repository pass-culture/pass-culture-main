import cn from 'classnames'
import { useLocation } from 'react-router'
import useSWR from 'swr'

import { AdageFrontRoles, type AdageHeaderLink } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { GET_EDUCATIONAL_INSTITUTION_BUDGET_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullDownloadIcon from '@/icons/full-download.svg'
import logoPassCultureIcon from '@/icons/logo-pass-culture.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { useAdageUser } from '../../hooks/useAdageUser'
import styles from './AdageHeader.module.scss'
import { AdageHeaderBudget } from './AdageHeaderBudget/AdageHeaderBudget'
import { AdageHeaderMenu } from './AdageHeaderMenu/AdageHeaderMenu'

export const AdageHeader = () => {
  const { adageUser } = useAdageUser()

  const { pathname } = useLocation()

  const isDiscoveryPage = pathname === '/adage-iframe/decouverte'

  function logAdageLinkClick(headerLinkName: AdageHeaderLink) {
    apiAdage.logHeaderLinkClick({
      iframeFrom: location.pathname,
      header_link_name: headerLinkName,
    })
  }

  const getEducationalInstitutionBudget = useSWR(
    adageUser.role !== AdageFrontRoles.READONLY
      ? GET_EDUCATIONAL_INSTITUTION_BUDGET_QUERY_KEY
      : null,
    () => apiAdage.getEducationalInstitutionWithBudget()
  )

  const institutionBudget = getEducationalInstitutionBudget.data?.budget

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
            alt="pass Culture"
            width="109"
            viewBox="0 0 71 24"
          />
        </div>
        <AdageHeaderMenu logAdageLinkClick={logAdageLinkClick} />
        {adageUser.role === AdageFrontRoles.REDACTOR &&
          !getEducationalInstitutionBudget.isLoading && (
            <AdageHeaderBudget
              institutionBudget={institutionBudget ?? 0}
              logAdageLinkClick={logAdageLinkClick}
            />
          )}
      </nav>
      {adageUser.role !== AdageFrontRoles.READONLY && !isDiscoveryPage && (
        <div className={styles['adage-header-help']}>
          Besoin d’aide pour réserver des offres pass Culture ?
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to={`${document.referrer}adage/index/docGet/format/pptx/doc/PRESENTATION_J_UTILISE_PASS_CULTURE`}
            isExternal
            download
            icon={fullDownloadIcon}
            target="_top"
            label="Télécharger l'aide"
          />{' '}
        </div>
      )}
    </div>
  )
}
