import { useLocation } from 'react-router'

import {
  type GetOffererResponseModel,
  type GetVenueResponseModel,
  SimplifiedBankAccountStatus,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

import styles from '../../Homepage.module.scss'

export interface BankAccountHasPendingCorrectionCalloutProps {
  offerer?: GetOffererResponseModel | null
  venue?: GetVenueResponseModel | null
  titleOnly?: boolean
}

export const BankAccountHasPendingCorrectionCallout = ({
  offerer,
  venue,
}: BankAccountHasPendingCorrectionCalloutProps): JSX.Element | null => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const displayCallout = withSwitchVenueFeature
    ? venue?.bankAccountStatus ===
      SimplifiedBankAccountStatus.PENDING_CORRECTIONS
    : offerer?.hasBankAccountWithPendingCorrections

  const url =
    '/remboursements/informations-bancaires' +
    (!withSwitchVenueFeature && offerer ? '?structure=' + offerer.id : '')

  if (!displayCallout) {
    return null
  }

  return (
    <div className={styles['reimbursements-banner']}>
      <Banner
        actions={[
          {
            href: url,
            label: 'Voir les corrections attendues',
            type: 'link',
            icon: fullNextIcon,
            onClick: () => {
              logEvent(
                BankAccountEvents.CLICKED__BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
                {
                  from: location.pathname,
                  ...(!withSwitchVenueFeature && { offererId: offerer?.id }),
                  ...(withSwitchVenueFeature && { venueId: venue?.id }),
                }
              )
            },
          },
        ]}
        variant={BannerVariants.ERROR}
        title="Compte bancaire incomplet"
        description={
          withSwitchVenueFeature
            ? ''
            : 'Des informations manquent pour finaliser votre compte bancaire.'
        }
      />
    </div>
  )
}
