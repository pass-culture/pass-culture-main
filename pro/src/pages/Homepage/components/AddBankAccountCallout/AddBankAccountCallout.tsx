import { useLocation } from 'react-router'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

import styles from '../../Homepage.module.scss'

interface AddBankAccountCalloutProps {
  venue: GetVenueResponseModel
}
export const AddBankAccountCallout = ({
  venue,
}: Readonly<AddBankAccountCalloutProps>) => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  return (
    <div className={styles['reimbursements-banner']}>
      <Banner
        title="Aucun compte bancaire configuré pour percevoir vos remboursements"
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
                venueId: venue.id,
              })
            },
          },
        ]}
      />
    </div>
  )
}
