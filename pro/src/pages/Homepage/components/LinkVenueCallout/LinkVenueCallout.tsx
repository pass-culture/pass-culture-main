import { useLocation } from 'react-router'

import type { GetOffererResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import styles from '../../Homepage.module.scss'

export interface LinkVenueCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

export const LinkVenueCallout = ({
  offerer,
}: LinkVenueCalloutProps): JSX.Element | null => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const displayCallout =
    !withSwitchVenueFeature &&
    offerer?.hasValidBankAccount &&
    offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0

  if (!displayCallout) {
    return null
  }

  return (
    <div className={styles['reimbursements-banner']}>
      <Banner
        title="Rattachement bancaire requis"
        actions={[
          {
            href: `/remboursements/informations-bancaires?structure=${offerer.id}`,
            label: 'Gérer le rattachement de mes structures',
            type: 'link',
            onClick: () => {
              logEvent(BankAccountEvents.CLICKED_ADD_VENUE_TO_BANK_ACCOUNT, {
                from: location.pathname,
                offererId: offerer.id,
              })
            },
          },
        ]}
        variant={BannerVariants.ERROR}
        description={`Dernière étape pour recevoir vos remboursements : reliez ${pluralizeFr(offerer.venuesWithNonFreeOffersWithoutBankAccounts.length, 'votre structure', 'vos structures')} à un compte bancaire.`}
      ></Banner>
    </div>
  )
}
