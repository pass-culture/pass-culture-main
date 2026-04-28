import { useLocation } from 'react-router'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

import styles from '../../Homepage.module.scss'

interface BankAccountHasPendingCorrectionCalloutProps {
  venue: GetVenueResponseModel
}
export const BankAccountHasPendingCorrectionCallout = ({
  venue,
}: Readonly<BankAccountHasPendingCorrectionCalloutProps>) => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  return (
    <div className={styles['reimbursements-banner']}>
      <Banner
        actions={[
          {
            href: '/administration/remboursements/informations-bancaires',
            label: 'Voir les corrections attendues',
            type: 'link',
            icon: fullNextIcon,
            onClick: () => {
              logEvent(
                BankAccountEvents.CLICKED_BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
                {
                  from: location.pathname,
                  venueId: venue.id,
                }
              )
            },
          },
        ]}
        variant={BannerVariants.ERROR}
        title="Compte bancaire incomplet"
      />
    </div>
  )
}
