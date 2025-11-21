import { useLocation } from 'react-router'

import type { GetOffererResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

import styles from '../../Homepage.module.scss'

export interface BankAccountHasPendingCorrectionCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

export const BankAccountHasPendingCorrectionCallout = ({
  offerer,
}: BankAccountHasPendingCorrectionCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const displayCallout = offerer?.hasBankAccountWithPendingCorrections

  if (!displayCallout) {
    return null
  }

  return (
    <div className={styles['reimbursements-banner']}>
      <Banner
        title=""
        actions={[
          {
            href: `/remboursements/informations-bancaires?structure=${offerer.id}`,
            label: 'Voir les corrections attendues',
            type: 'link',
            icon: fullNextIcon,
            onClick: () => {
              logEvent(
                BankAccountEvents.CLICKED__BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
                {
                  from: location.pathname,
                  offererId: offerer.id,
                }
              )
            },
          },
        ]}
        variant={BannerVariants.ERROR}
        description="Compte bancaire incomplet"
      />
    </div>
  )
}
