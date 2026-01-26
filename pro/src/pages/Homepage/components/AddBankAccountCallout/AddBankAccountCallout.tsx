import { useLocation } from 'react-router'

import type { GetOffererResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

import styles from '../../OldHomepage.module.scss'

interface AddBankAccountCalloutProps {
  offerer?: GetOffererResponseModel | null
}

export const AddBankAccountCallout = ({
  offerer = null,
}: AddBankAccountCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const displayBankAccountBanner =
    offerer &&
    !offerer.hasPendingBankAccount &&
    !offerer.hasValidBankAccount &&
    !offerer.hasBankAccountWithPendingCorrections &&
    offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0

  if (!displayBankAccountBanner) {
    return null
  }

  return (
    <div className={styles['reimbursements-banner']}>
      <Banner
        title="Compte bancaire manquant"
        variant={BannerVariants.ERROR}
        actions={[
          {
            href: '/remboursements/informations-bancaires',
            label: 'Ajouter un compte bancaire',
            type: 'link',
            icon: fullNextIcon,
            onClick: () => {
              logEvent(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
                from: location.pathname,
                offererId: offerer.id,
              })
            },
          },
        ]}
        description="Configurez un compte bancaire pour recevoir vos remboursements."
      />
    </div>
  )
}
